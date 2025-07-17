
import sys
import copy
import warnings
import numpy as np
import pandas as pd
from tqdm import tqdm
from sksurv. util import Surv
from sksurv.svm import FastSurvivalSVM
from sksurv.metrics import concordance_index_censored, cumulative_dynamic_auc
from sksurv.linear_model.coxnet import CoxnetSurvivalAnalysis
from sklearn.model_selection import StratifiedKFold
from icare.survival import BaggedIcareSurvival



def get_duplicates(dataframe):
    columns_to_remove = []
    list_columns = copy.deepcopy(dataframe.columns)
    i = 1
    for column1 in list_columns:
        for column2 in list_columns[i:]:
            if dataframe[column1].equals(dataframe[column2]):
                columns_to_remove.append(column1)
                break
        i+=1
    return columns_to_remove

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
kfold = StratifiedKFold(5, random_state=np.random.randint(0, 100000000), shuffle=True)

res_dict = {i:[] for i in np.arange(.52, .58, .001)}
patient_ids = radiomics["Patient_ID"]

list_models = [FastSurvivalSVM(max_iter=3),
              FastSurvivalSVM(max_iter=100),
              #FastSurvivalSVM(max_iter=1000),
              BaggedIcareSurvival(n_estimators=10, n_jobs=-1),
              #BaggedIcareSurvival(n_estimators=100, n_jobs=-1),
              #BaggedIcareSurvival(n_estimators=200, n_jobs=-1),
              #BaggedIcareSurvival(n_estimators=500, n_jobs=-1),
              #BaggedIcareSurvival(n_estimators=1000, n_jobs=-1),
              ]
with open("../data/csvs/Radiomics_performance.csv", "w") as csvfile:
    csvfile.write("Model")
    for t in np.arange(.52, .58, .01):
        csvfile.write(f",{t}")
    for model in list_models:
        for tr_ids, ts_ids in kfold.split(ids, censored):
            train_ids = ids[tr_ids]
            test_ids = ids[ts_ids]
            X_train = radiomics[radiomics["Patient_ID"].isin(train_ids)]
            X_test = radiomics[radiomics["Patient_ID"].isin(test_ids)]
            duplicate_columns = get_duplicates(X_train)
            for c in duplicate_columns:
                if c not in ["RFS", "Relapse", "Patient ID"]:
                    del X_train[c]
                    del X_test[c]
            Y_train = Surv.from_arrays(endpoints[endpoints["PatientID"].isin(train_ids)]["Relapse"],
                                        endpoints[endpoints["PatientID"].isin(train_ids)]["RFS"])

            Y_test = Surv.from_arrays(endpoints[endpoints["PatientID"].isin(test_ids)]["Relapse"],
                                        endpoints[endpoints["PatientID"].isin(test_ids)]["RFS"])
            X_train = X_train.fillna(0)
            X_test = X_test.fillna(0)
            del X_train["Patient_ID"]
            del X_test["Patient_ID"]

            for thresh in tqdm(np.arange(.52, .58, .001)):
                # Feature selection
                for col in X_train.columns:
                    model = CoxnetSurvivalAnalysis()
                    model.fit(X_train[col].values.reshape(-1, 1), Y_train)
                    corr_score = concordance_index_censored(Y_train["event"], Y_train["time"],
                                                                model.predict(X_train[col].values.reshape(-1, 1)))
                    if corr_score[0] < thresh:
                        del X_train[col]
                        del X_test[col]

                avg_ci = 0.
                avg_cdauc = 0.
                for i in range(4):
                    #model = FastSurvivalSVM(max_iter=3)
                    model.fit(X_train, Y_train)
                    y_hat_test = model.predict(X_test)
                    y_hat_train = model.predict(X_train)
                    ci = concordance_index_censored(Y_test["event"], Y_test["time"], y_hat_test)
                    time_points = np.arange(Y_test["time"][np.argpartition(Y_test["time"],5)[5]],
                                                    Y_test["time"][np.argpartition(Y_test["time"],-5)[-5]], 50)
                    cd_auc = cumulative_dynamic_auc(Y_train, Y_test, y_hat_test, times=time_points)
                    avg_ci += ci[0]
                    avg_cdauc += cd_auc[1]
                res_dict[thresh].append(avg_ci/4)
    csvfile.write(f"{model.__str__()}")
    for k in res_dict.keys():
        avg = np.mean(res_dict[k])
        csvfile.write(f",{avg}")
    csvfile.write(f"\n")
