
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
from sksurv.ensemble import RandomSurvivalForest
from icare.survival import BaggedIcareSurvival
from sklearn.model_selection import StratifiedKFold



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
organomics_path = sys.argv[1]  # Path to organomic features csv
endpoints_path = sys.argv[2]  # Path to Hecktor endpoints file
clinical_path = sys.argv[3]  # Path to Hecktor clinical data file
organomics = pd.read_csv(organomics_path)
endpoints = pd.read_csv(endpoints_path)
clinical_data = pd.read_csv(clinical_path)
clinical_data["Gender"] = clinical_data["Gender"].apply(lambda x: 1 if x =="M" else 2)
clinical_data["Tobacco"] = clinical_data["Tobacco"].apply(lambda x: 1 if x ==1 else -1 if x==0 else 0)
clinical_data["Surgery"] = clinical_data["Surgery"].apply(lambda x: 1 if x ==1 else -1 if x==0 else 0)
clinical_data["Chemotherapy"] =clinical_data["Chemotherapy"].apply(lambda x: 1 if x ==1 else -1 if x==0 else 0)
clinical_data["Performance status"] =clinical_data["Performance status"].apply(lambda x: x+1 if x in (0,1,2,3,4) else 0)
clinical_data["HPV status (0=-, 1=+)"] = clinical_data["HPV status (0=-, 1=+)"].apply(lambda x: 1 if x ==1 else -1 if x==0 else 0)
del clinical_data["Task 1"]
del clinical_data["Task 2"]



organomics.set_index('Patient_ID', inplace=True)
clinical_data.set_index('PatientID', inplace=True)
idx = organomics.index
organomics = pd.merge(organomics, clinical_data, left_index=True, right_index=True)
organomics.insert(0, "Patient_ID", idx)
del clinical_data


# Remove samples with no endpoint
organomics = organomics[organomics["Patient_ID"].isin(endpoints["PatientID"])]

ids = endpoints["PatientID"]
censored = endpoints["Relapse"]
kfold = StratifiedKFold(5, random_state=np.random.randint(0, 100000000), shuffle=True)

thresh_range = np.arange(.52, .58, .001)

list_models = [#CoxnetSurvivalAnalysis(n_alphas=10),
              #CoxnetSurvivalAnalysis(n_alphas=100),
              FastSurvivalSVM(max_iter=3),
              #FastSurvivalSVM(max_iter=10),
              #FastSurvivalSVM(max_iter=100),
              #FastSurvivalSVM(max_iter=1000),
              #BaggedIcareSurvival(n_estimators=10, n_jobs=-1),
              #BaggedIcareSurvival(n_estimators=100, n_jobs=-1),
              #BaggedIcareSurvival(n_estimators=200, n_jobs=-1),
              #BaggedIcareSurvival(n_estimators=500, n_jobs=-1),
              #BaggedIcareSurvival(n_estimators=1000, n_jobs=-1),
              RandomSurvivalForest(n_estimators=100)
              ]
with open("../data/csvs/Organomics_performance.csv", "w") as csvfile:
    csvfile.write("Model")
    for t in thresh_range:
        csvfile.write(f",{t}")
    csvfile.write("\n")
    for model in list_models:
        res_dict = {i:[] for i in thresh_range}
        print(str(model).replace(",", " "))
        for tr_ids, ts_ids in kfold.split(ids, censored):
            train_ids = ids[tr_ids]
            test_ids = ids[ts_ids]
            X_train = organomics[organomics["Patient_ID"].isin(train_ids)]
            X_test = organomics[organomics["Patient_ID"].isin(test_ids)]

            Y_train = Surv.from_arrays(endpoints[endpoints["PatientID"].isin(train_ids)]["Relapse"],
                                        endpoints[endpoints["PatientID"].isin(train_ids)]["RFS"])

            Y_test = Surv.from_arrays(endpoints[endpoints["PatientID"].isin(test_ids)]["Relapse"],
                                        endpoints[endpoints["PatientID"].isin(test_ids)]["RFS"])
            
            duplicate_columns = get_duplicates(organomics)
            for c in duplicate_columns:
                if c not in ["RFS", "Relapse", "Patient ID"]:
                    del organomics[c]

            X_train = X_train.fillna(0)
            X_test = X_test.fillna(0)
            del X_train["Patient_ID"]
            del X_test["Patient_ID"]

            for thresh in tqdm(thresh_range):
                # Feature selection
                for col in X_train.columns:
                    fs_model = CoxnetSurvivalAnalysis()
                    fs_model.fit(X_train[col].values.reshape(-1, 1), Y_train)
                    corr_score = concordance_index_censored(Y_train["event"], Y_train["time"],
                                                                fs_model.predict(X_train[col].values.reshape(-1, 1)))
                    if corr_score[0] < thresh:
                        del X_train[col]
                        del X_test[col]

                avg_ci = 0.
                avg_cdauc = 0.
                for i in range(4):
                    model.fit(X_train, Y_train)
                    y_hat_train = model.predict(X_train)
                    y_hat_test = model.predict(X_test)
                    ci_train = concordance_index_censored(Y_train["event"], Y_train["time"], y_hat_train)
                    ci = concordance_index_censored(Y_test["event"], Y_test["time"], y_hat_test)
                    print(ci_train, ci)
                    time_points = np.arange(Y_test["time"][np.argpartition(Y_test["time"],5)[5]],
                                                    Y_test["time"][np.argpartition(Y_test["time"],-5)[-5]], 50)
                    cd_auc = cumulative_dynamic_auc(Y_train, Y_test, y_hat_test, times=time_points)
                    avg_ci += ci[0]
                    avg_cdauc += cd_auc[1]
                res_dict[thresh].append(avg_ci/4)
        csvfile.write(f"{str(model).replace(',', ' ')}")
        for k in res_dict.keys():
            avg = np.mean(res_dict[k])
            csvfile.write(f",{avg}")            
        csvfile.write("\n")
