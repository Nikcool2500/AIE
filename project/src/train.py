import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from catboost import CatBoostRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import RobustScaler, StandardScaler
import random
import os
import joblib
import mlflow


SEED = 42
os.environ['PYTHONHASHSEED'] = str(SEED)
random.seed(SEED)
np.random.seed(SEED)


mlflow.set_tracking_uri("./mlruns")
mlflow.set_experiment("Credit_Prediction_Experiments_Catboost")

df = pd.read_csv('https://raw.githubusercontent.com/liAmirali/UIML-credit-limit-project/refs/heads/main/CreditPrediction.csv')
df = df.drop(columns=['CLIENTNUM', 'Unnamed: 19'])
df = df[(df['Customer_Age'] <= 80)]
print(f'Размер данных после удаления аномалий: {df.shape[0]}')

target_col = "Credit_Limit"
num_cols = [col for col in df.select_dtypes(include=['int64', 'float64']).columns if col != target_col]
cat_cols = df.select_dtypes(include=['object']).columns.tolist()
print(num_cols)
print(cat_cols)

for col_name in cat_cols:
    df[col_name] = df[col_name].fillna('Unknown')
for col_name in num_cols:
    df[col_name] = df[col_name].fillna(df[col_name].median())

X = df.drop(columns=[target_col])
y = df[target_col]

X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.25, random_state=42)

print(f'Train: {X_train.shape[0]} ({X_train.shape[0]/len(X)*100:.1f}%)')
print(f'Validation: {X_val.shape[0]} ({X_val.shape[0]/len(X)*100:.1f}%)')
print(f'Test: {X_test.shape[0]} ({X_test.shape[0]/len(X)*100:.1f}%)')

cols_to_log = ['Total_Revolving_Bal', 'Total_Amt_Chng_Q4_Q1', 'Total_Trans_Amt', 'Total_Ct_Chng_Q4_Q1', 'Avg_Utilization_Ratio']

traget_logged = False
for col in cols_to_log:
    if col in X_train.columns:
        X_train[col] = np.log1p(X_train[col])
        X_val[col] = np.log1p(X_val[col])
        X_test[col] = np.log1p(X_test[col])

X_train_cb = X_train.copy()
X_val_cb = X_val.copy()
X_test_cb = X_test.copy()

print(f"Shape X_train: {X_train_cb.shape}")
print(f"Категориальные колонки: {cat_cols}")

scaler = StandardScaler()

X_train_cb[num_cols] = scaler.fit_transform(X_train_cb[num_cols])

X_val_cb[num_cols] = scaler.transform(X_val_cb[num_cols])

X_test_cb[num_cols] = scaler.transform(X_test_cb[num_cols])

joblib.dump(scaler, '../artifacts/scaler_cb.pkl')


cb_model = CatBoostRegressor(
    iterations=600,
    depth=9,
    learning_rate=0.061502811982602434,
    l2_leaf_reg=1.3240524100782431,
    random_state=SEED,
    verbose=False,
    loss_function='RMSE',
    grow_policy='Lossguide',
    cat_features=cat_cols
)

print("Обучение CatBoost модели...")
cb_model.fit(X_train_cb, y_train, eval_set=[(X_val_cb, y_val)])
print("Обучение завершено!")

import json, hashlib

config = {
    'iterations': 600,
    'depth': 9,
    'learning_rate': 0.061502811982602434,
    'loss_function': 'RMSE',
    'grow_policy': 'Lossguide',
    "target_col": target_col,
    "num_cols": num_cols,
    "cat_cols": cat_cols,
    "encoder": "TargetEncoder(smoothing=10.0)",
    "scaler": str(scaler)[:-2],
    "random_state": 42,
    "train_size": len(X_train),
    "val_size": len(X_val),
    "test_size": len(X_test),
    "data_alteration": "Only age<=80, Log of features" + ", Log of target" if traget_logged else "",
}

with open("../artifacts/CB_mlflow/catboost_train_config.json", "w") as f:
    json.dump(config, f, indent=2)

data_path = "../data/CreditPrediction.csv"
with open(data_path, "rb") as f:
    data_hash = hashlib.md5(f.read()).hexdigest()
print(f"Data hash: {data_hash}")


def plot_feature_importance(model, X_train, top_n=15):
    """Рисует график важности признаков"""
    feature_importance = pd.DataFrame({
        'feature': X_train.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    top_features = feature_importance.head(top_n)
    ax.barh(range(len(top_features)), top_features['importance'].values)
    ax.set_yticks(range(len(top_features)))
    ax.set_yticklabels(top_features['feature'].values)
    ax.set_xlabel('Importance', fontsize=12)
    ax.set_title(f'Top {top_n} Feature Importance', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    plt.tight_layout()
    plt.show()
    
    return feature_importance

y_train_pred = cb_model.predict(X_train_cb)
y_val_pred = cb_model.predict(X_val_cb)
y_test_pred = cb_model.predict(X_test_cb)


def calculate_cb_metrics(y_true, y_pred, dataset_name):
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    print(f'\n{dataset_name}:')
    print(f'  MSE:   {mse:.4f}')
    print(f'  RMSE:  {rmse:.4f}')
    print(f'  MAE:   {mae:.4f}')
    print(f'  R²:    {r2:.4f}')
    
    return {'MSE': mse, 'RMSE': rmse, 'MAE': mae, 'R2': r2}

print('=' * 50)
print('Метрики CatBoost модели')
print('=' * 50)

train_cb_metrics = calculate_cb_metrics(y_train, y_train_pred, 'TRAIN')
val_cb_metrics = calculate_cb_metrics(y_val, y_val_pred, 'VALIDATION')
test_cb_metrics = calculate_cb_metrics(y_test, y_test_pred, 'TEST')

print('\n' + '=' * 50)

joblib.dump(cb_model, '../artifacts/model_catboost.pkl')
print("\nМодель сохранена в '../artifacts/model_catboost.pkl'")

with mlflow.start_run(run_name="Catboost_train"):
    
    mlflow.log_params(config)
    mlflow.log_param("data_hash", data_hash)
    
    mlflow.log_metrics({
        "train_mse": train_cb_metrics["MSE"],
        "train_rmse": train_cb_metrics["RMSE"],
        "train_mae": train_cb_metrics["MAE"],
        "train_r2": train_cb_metrics["R2"],
        "val_mse": val_cb_metrics["MSE"],
        "val_rmse": val_cb_metrics["RMSE"],
        "val_mae": val_cb_metrics["MAE"],
        "val_r2": val_cb_metrics["R2"],
        "test_mse": test_cb_metrics["MSE"],
        "test_rmse": test_cb_metrics["RMSE"],
        "test_mae": test_cb_metrics["MAE"],
        "test_r2": test_cb_metrics["R2"],
    })
    
    mlflow.sklearn.log_model(cb_model, "model")
    
    mlflow.log_artifact("../artifacts/CB_mlflow/catboost_train_config.json")
    mlflow.log_artifact(data_path, "data")
    