import pandas as pd
from sksurv.svm.survival_svm import FastSurvivalSVM
from sksurv. util import Surv
from sksurv.metrics import concordance_index_censored


if __name__ == "__main__":
    import sys
    organomics_path = sys.argv[1]
    endpoints_path = sys.argv[2]
    organomics = pd.read_csv(organomics_path)
    endpoints = pd.read_csv(endpoints_path)
    patient_ids = organomics["Patient_ID"]
    train_ids = patient_ids[:round(len(patient_ids)*.8)]
    test_ids = patient_ids[round(len(patient_ids)*.8):]
    X_train = organomics[organomics["Patient_ID"].isin(train_ids)]
    X_test = organomics[organomics["Patient_ID"].isin(test_ids)]

    Y_train = Surv.from_arrays(endpoints[endpoints["PatientID"].isin(train_ids)]["Relapse"],
                               endpoints[endpoints["PatientID"].isin(train_ids)]["RFS"])
    
    Y_test = Surv.from_arrays(endpoints[endpoints["PatientID"].isin(test_ids)]["Relapse"],
                               endpoints[endpoints["PatientID"].isin(test_ids)]["RFS"])
    X_train = X_train.fillna(0)
    X_test = X_test.fillna(0)
    del X_train["Patient_ID"]
    model = FastSurvivalSVM()
    model.fit(X_train, Y_train)
    y_hat_test = model.predict(X_test)
    concordance_index_censored(endpoints[endpoints["PatientID"].isin(test_ids)]["Relapse"],
                               endpoints[endpoints["PatientID"].isin(test_ids)]["RFS"],
                               y_hat_test)