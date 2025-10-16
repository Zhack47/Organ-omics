## Inspired from https://github.com/Lrebaud/ICARE/blob/main/notebook/reproducing_HECKTOR2022.ipynb

import numpy as np

import warnings
import pandas as pd
import matplotlib.pyplot as plt
from sksurv.util import Surv
from sksurv.metrics import concordance_index_censored, cumulative_dynamic_auc
from scipy.stats import spearmanr, pearsonr
from sklearn.model_selection import StratifiedKFold

from icare.survival import BaggedIcareSurvival
from icare.visualisation import plot_avg_sign


warnings.filterwarnings("ignore")
organomics = pd.read_csv("../data/csvs/Organomics.csv", index_col="Patient_ID")
endpoints = pd.read_csv("../data/csvs/hecktor2022_endpoint_training.csv", index_col="PatientID")
clinical = pd.read_csv("../data/csvs/hecktor2022_clinical_info_training.csv", index_col="PatientID")
print(clinical)
print(np.nanmedian(clinical["Weight"]))
clinical["Weight"] = [np.nanmedian(clinical["Weight"]) if np.isnan(x) else x for x in clinical["Weight"]]
clinical["Gender"] = [-1 if x == "M" else 1 for x in clinical["Gender"]]
clinical["Tobacco"] = [1 if x == 1. else -1 if x ==0. else 0 for x in clinical["Tobacco"]]
clinical["Alcohol"] = [1 if x == 1. else -1 if x ==0. else 0 for x in clinical["Alcohol"]]
clinical["Performance status"] = [-1 if np.isnan(x) else x for x in clinical["Performance status"]]
clinical["Surgery"] = [1 if x == 1. else -1 if x ==0. else 0 for x in clinical["Surgery"]]
clinical["HPV status (0=-, 1=+)"] = [1 if x == 1. else -1 if x ==0. else 0 for x in clinical["HPV status (0=-, 1=+)"]]
print(clinical)
print(organomics.shape)
print(clinical.shape)
print(endpoints.shape)

df_train = pd.merge(organomics, endpoints, left_index=True, right_index=True)
df_train = pd.merge(df_train, clinical, left_index=True, right_index=True)
print(df_train.shape)
#####

features = list(set(df_train.columns.tolist()) - set(['Relapse', 'RFS', 'Task 1', 'Task 2', 'CenterID']))
#features = [x for x in features if 'lesions_merged' not in x and 'lymphnodes_merged' not in x]
extra_features = ['Gender',
                  'Age',
                  'Weight',
                  'Tobacco',
                  'Alcohol',
                  'Performance status',
                  'HPV status (0=-, 1=+)',
                  'Surgery',
                  'Chemotherapy',
                  #'nb_lesions',
                  #'nb_lymphnodes',
                  #'whole_body_scan'
                  ]


features_groups = list(map(str, np.unique(["_".join(x.split('_')[:-2]) for x in features])))
features_groups = list(set(features_groups) - set(extra_features))
# features_groups = [x + '_' for x in features_groups]
features_groups.append('extra_features')
print(len(features_groups), features_groups)

####

y_train = Surv.from_arrays(event=df_train['Relapse'].values,
                           time=df_train['RFS'].values)
#X_train, X_test = df_train[features], df_test[features]
kfold = StratifiedKFold(5, random_state=np.random.randint(0, 100000000), shuffle=True)


####
features_groups_id = []
for f in df_train.columns:
    if f in extra_features:
        features_groups_id.append(features_groups.index('extra_features'))
    else:
        group = "_".join(f.split('_')[:-2])
        features_groups_id.append(features_groups.index(group))


####

hyperparameters_sets = [
 {'rho': 0.66,
  'cmin': 0.53,
  'max_features': 0.00823045267489712,
  'mandatory_features': extra_features,
  'sign_method': 'harrell',
  'features_groups_to_use': [2, 4, 8, 10]},
 {'rho': 0.72,
  'cmin': 0.59,
  'max_features': 0.009465020576131687,
  'mandatory_features': extra_features,
  'sign_method': 'harrell',
  'features_groups_to_use': [3, 4, 10, 11, 12]},
 {'rho': 0.87,
  'cmin': 0.55,
  'max_features': 0.06131687242798354,
  'mandatory_features': extra_features,
  'sign_method': 'harrell',
  'features_groups_to_use': [1, 3, 4, 10, 11, 12]},
 {'rho': 0.57,
  'cmin': 0.51,
  'max_features': 0.005761316872427984,
  'mandatory_features': extra_features,
  'sign_method': 'harrell',
  'features_groups_to_use': [0, 2, 5, 6, 9, 11, 12]},
 {'rho': 0.71,
  'cmin': 0.57,
  'max_features': 0.16131687242798354,
  'mandatory_features': extra_features,
  'sign_method': 'harrell',
  'features_groups_to_use': [4, 8, 12]}
]

####

censored = df_train["Relapse"]
ids = df_train.index
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

    model = BaggedIcareSurvival(n_estimators=100,
                                parameters_sets=None,  # hyperparameters_sets,
                                aggregation_method='median',
                                n_jobs=-1)

    model.fit(X_train_local, Y_train_local) # , feature_groups=features_groups_id)
    train_pred = model.predict(X_train_local)
    test_pred = model.predict(X_test_local)
    #print(train_pred)
    #test_pred = model.predict(X_test)

    print(concordance_index_censored(Y_train_local["event"], Y_train_local["time"], train_pred))
    print(concordance_index_censored(Y_test_local["event"], Y_test_local["time"], test_pred))
    #spearmanr(train_pred, Y_train_local["time"])
    #plot_avg_sign(model, features=extra_features)
    #plt.show()
