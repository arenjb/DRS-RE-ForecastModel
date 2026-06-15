import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score 
import numpy as np

def compute_metrics(y_true, y_pred, capacity_mw):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse =  np.sqrt(mean_squared_error(y_true, y_pred))
    nmae = (mae / capacity_mw) * 100
    nrmse = (rmse / capacity_mw) * 100
    r2 =  r2_score(y_true, y_pred)
    mbe = np.mean(y_pred - y_true) # Mean Bias Error
    return {
        "MAE": mae,
        "RMSE": rmse,
        "NMAE (%)": nmae,
        "NRMSE (%)": nrmse,
        "R²": r2,
        "MBE": mbe
    }

if __name__ == "__main__":
    # Example usage
    y_true = [25.0, 30.0, 20.0, 30.0, 40.0]
    y_pred = [25.5, 29.2, 21.0, 29.9, 40.8]
    capacity_mw = 100
    metrics = compute_metrics(y_true, y_pred, capacity_mw)
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")
