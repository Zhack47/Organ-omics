
import sys
import warnings
import numpy as np
import pandas as pd
from tqdm import tqdm
from sksurv. util import Surv
from sksurv.metrics import concordance_index_censored, cumulative_dynamic_auc
from sksurv.linear_model.coxnet import CoxnetSurvivalAnalysis
from sklearn.model_selection import StratifiedKFold
from icare.survival import BaggedIcareSurvival


np.random.seed(1053)
warnings.filterwarnings("ignore") #,message="'force_all_finite' was renamed to 'ensure_all_finite' in 1.6 and will be removed in 1.8")

radiomics_path = sys.argv[1]
endpoints_path = sys.argv[2]
radiomics = pd.read_csv(radiomics_path)
endpoints = pd.read_csv(endpoints_path)

# Remove samples with no endpoint
radiomics = radiomics[radiomics["Patient_ID"].isin(endpoints["PatientID"])]

ids = endpoints["PatientID"]
censored = endpoints["Relapse"]
kfold = StratifiedKFold(6, random_state=np.random.randint(0, 100000000), shuffle=True)

for i in range(10):
    avg_ci = 0.
    avg_cdauc = 0.
    for tr_ids, ts_ids in kfold.split(ids, censored):
        train_ids = ids[tr_ids]
        test_ids = ids[ts_ids]
        patient_ids = radiomics["Patient_ID"]
        X_train = radiomics[radiomics["Patient_ID"].isin(train_ids)]
        X_test = radiomics[radiomics["Patient_ID"].isin(test_ids)]

        Y_train = Surv.from_arrays(endpoints[endpoints["PatientID"].isin(train_ids)]["Relapse"],
                                    endpoints[endpoints["PatientID"].isin(train_ids)]["RFS"])

        Y_test = Surv.from_arrays(endpoints[endpoints["PatientID"].isin(test_ids)]["Relapse"],
                                    endpoints[endpoints["PatientID"].isin(test_ids)]["RFS"])
        X_train = X_train.fillna(0)
        X_test = X_test.fillna(0)
        del X_train["Patient_ID"]
        del X_test["Patient_ID"]

        # Feature selection
        for col in tqdm(X_train.columns):
            model = CoxnetSurvivalAnalysis()
            model.fit(X_train[col].values.reshape(-1, 1), Y_train)
            corr_score = concordance_index_censored(Y_train["event"], Y_train["time"],
                                                        model.predict(X_train[col].values.reshape(-1, 1)))
            if corr_score[0] <.5:
                del X_train[col]
                del X_test[col]

        model = BaggedIcareSurvival(n_jobs=-1)
        model.fit(X_train, Y_train)
        y_hat_test = model.predict(X_test)
        y_hat_train = model.predict(X_train)
        ci = concordance_index_censored(Y_test["event"], Y_test["time"], y_hat_test)
        time_points = np.arange(Y_test["time"][np.argpartition(Y_test["time"],5)[5]],
                                        Y_test["time"][np.argpartition(Y_test["time"],-5)[-5]], 50)
        cd_auc = cumulative_dynamic_auc(Y_train, Y_test, y_hat_test, times=time_points)
        avg_ci += ci[0]
        avg_cdauc += cd_auc[1]
        #print(ci)
        #print(cd_auc[1])
    print(avg_ci/6)
    print(avg_cdauc/6)
    print()