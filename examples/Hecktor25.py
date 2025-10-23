## Inspired from https://github.com/Lrebaud/ICARE/blob/main/notebook/reproducing_HECKTOR2022.ipynb

import numpy as np

import warnings
import pandas as pd
import matplotlib.pyplot as plt
from sksurv.util import Surv
from sksurv.metrics import concordance_index_censored, cumulative_dynamic_auc
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest
from sksurv.svm import FastSurvivalSVM
from sksurv.linear_model import CoxnetSurvivalAnalysis
from icare.survival import BaggedIcareSurvival


warnings.filterwarnings("ignore")
organomics = pd.read_csv("../data/csvs/Hecktor25_Organomics.csv", index_col="Patient_ID")
endpoints_clinical = pd.read_csv("../data/csvs/HECKTOR_2025_Training_Task_2.csv", index_col="PatientID")

endpoints_clinical["Gender"] = [-1 if x == "M" else 1 for x in endpoints_clinical["Gender"]]
endpoints_clinical["Tobacco Consumption"] = [1 if x == 1. else -1 if x ==0. else 0 for x in endpoints_clinical["Tobacco Consumption"]]
endpoints_clinical["Alcohol Consumption"] = [1 if x == 1. else -1 if x ==0. else 0 for x in endpoints_clinical["Alcohol Consumption"]]
endpoints_clinical["Performance Status"] = [-1 if np.isnan(x) else x for x in endpoints_clinical["Performance Status"]]
endpoints_clinical["M-stage"] = [-1 if np.isnan(x) else 0 if x=='M0' else  1 if x=='Mx' else 2  for x in endpoints_clinical["Performance Status"]]

df_train = organomics
# df_train = radiomics
# df_train = endpoints_clinical
df_train = pd.merge(df_train, endpoints_clinical, left_index=True, right_index=True)

####

y_train = Surv.from_arrays(event=df_train['Relapse'].values,
                           time=df_train['RFS'].values)
kfold = StratifiedKFold(3, random_state=np.random.randint(0, 100000000), shuffle=True)


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

# Removing duplicate columns
# duplicate_columns = get_duplicates(df_train)
# for c in duplicate_columns:
#     if c not in ["RFS", "Relapse", "Patient ID"]:
#         del df_train[c]
# print(df_train.shape)


# Remove some
#for col in df_train.columns:
#    if "CT_nasal" not in str(col) and col not in ["Relapse", "RFS"]:
#        del df_train[col]
#print(df_train.shape)

####


#df_train = df_train.fillna(0)
df_train = df_train.dropna(axis=1)

ci_avg_test = 0.
ci_avg_train = 0.
cdauc_avg_test=0.
cdauc_avg_train=0.
ids = df_train.index
censored = df_train["Relapse"]
for tr_ids, ts_ids in kfold.split(ids, censored):
    print("###############################################")
    train_ids = ids[tr_ids]
    test_ids = ids[ts_ids]
    X_train_local = df_train[df_train.index.isin(train_ids)]
    X_test_local = df_train[df_train.index.isin(test_ids)]
    Y_train_local = Surv.from_arrays(df_train[df_train.index.isin(train_ids)]["Relapse"],
                                        df_train[df_train.index.isin(train_ids)]["RFS"])
    Y_test_local = Surv.from_arrays(df_train[df_train.index.isin(test_ids)]["Relapse"],
                                        df_train[df_train.index.isin(test_ids)]["RFS"])

    model = BaggedIcareSurvival(n_estimators=1000,
                                parameters_sets=None,  # hyperparameters_sets,
                                aggregation_method='median',
                                n_jobs=-1)
    #model = FastSurvivalSVM()
    #model = CoxnetSurvivalAnalysis()
    
    banned_features = ["RFS", "Relapse", "Task 1", "Task 2", "CenterID"]
    for banned_feature in banned_features:
        try:
            del X_train_local[banned_feature]
            del X_test_local[banned_feature]
        except KeyError:
            pass

    def f_uci(X,Y):
        Y = Surv.from_arrays(event=[x[0] for x in Y], time=[x[1] for x in Y])
        scores = []
        pvals = []
        for col_nb in range(X.shape[1]):
            fs_model = CoxnetSurvivalAnalysis()
            #fs_model = FastSurvivalSVM()
            fs_model.fit(X[:,col_nb].reshape(-1, 1), Y)
            corr_score = concordance_index_censored(Y["event"], Y["time"],
                                                        fs_model.predict(X[:, col_nb].reshape(-1, 1)))
            scores.append(corr_score[0])
            pvals.append(1/corr_score[0])
        return scores, scores
    
    selector = SelectKBest(score_func=f_uci, k=10)
    X_train_selected = selector.fit(X_train_local.values, Y_train_local)
    X_train_selected = selector.transform(X_train_local)
    X_test_selected = selector.transform(X_test_local)

    selected_features = X_train_local.columns[selector.get_support()]
    f_scores = selector.scores_[selector.get_support()]
    X_train_local = X_train_local[selected_features]
    X_test_local = X_test_local[selected_features]
    
    print(f"Selected Features: {selected_features}")
    #print(f"F-Scores: {f_scores}")
    
    
    scaler = StandardScaler()
    X_train_local_np = scaler.fit_transform(X_train_local)
    X_test_local_np = scaler.transform(X_test_local)

    model.fit(X_train_local, Y_train_local) # , feature_groups=features_groups_id)
    train_pred = model.predict(X_train_local)
    test_pred = model.predict(X_test_local)

    ci_train = concordance_index_censored(Y_train_local["event"], Y_train_local["time"], train_pred)
    ci_test = concordance_index_censored(Y_test_local["event"], Y_test_local["time"], test_pred)
    ci_avg_train+=ci_train[0]
    ci_avg_test+=ci_test[0]
    print(ci_train[0], ci_test[0])
    
    time_points_train = np.arange(Y_train_local["time"][np.argpartition(Y_train_local["time"],5)[5]],
                                                    Y_train_local["time"][np.argpartition(Y_train_local["time"],-5)[-5]], 50)
    time_points_test = np.arange(Y_test_local["time"][np.argpartition(Y_test_local["time"],5)[5]],
                                                    Y_test_local["time"][np.argpartition(Y_test_local["time"],-5)[-5]], 50)
    cdauc_train = cumulative_dynamic_auc(Y_train_local, Y_train_local, train_pred, times=time_points_train)[1]
    cdauc_test = cumulative_dynamic_auc(Y_train_local, Y_test_local, test_pred, times=time_points_test)[1]
    cdauc_avg_train+=cdauc_train
    cdauc_avg_test+=cdauc_test
    print(cdauc_train, cdauc_test)

print(f"Average train CI:{ci_avg_train/3}")
print(f"Average test CI:{ci_avg_test/3}")
print(f"Average train cdAUC:{cdauc_avg_train/5}")
print(f"Average test cdAUC:{cdauc_avg_test/5}")