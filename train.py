#!/usr/bin/env python
# coding: utf-8

# ### Реквизиты автора: Рябов Михаил Сергеевич

# In[41]:


import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OrdinalEncoder, OneHotEncoder, PowerTransformer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import SGDRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import root_mean_squared_error
import numpy as np
import matplotlib.pyplot as plt
import pickle
import mlflow
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from mlflow.models import infer_signature
from sklearn.model_selection import GridSearchCV
import logging


logging.basicConfig(level=logging.WARNING)

# In[42]:


# Настройка MLflow
mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("hwork")


# In[43]:


def prepare_data(df):
    X = df.drop(columns=['Performance Index'])
    y = df['Performance Index']
    
    X_train_val, X_test, y_train_val, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
    )

    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=0.25, random_state=42
    )
    return X_train, X_val, X_test, y_train, y_val, y_test


# In[44]:


def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2


# In[45]:


def create_preprocessor():
    numeric_features = ['Hours Studied', 'Previous Scores', 
                      'Sleep Hours', 'Sample Question Papers Practiced',
                      'Extracurricular Activities']
    
    preprocessor = Pipeline(
        steps=[('scaler', StandardScaler())]
    )
    return preprocessor


# In[46]:


def train_and_log_model(model, params, model_name, X_train, y_train, X_val, y_val):
    with mlflow.start_run(run_name=model_name):
        preprocessor = create_preprocessor()
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('model', model)
        ])
        
        if params:
            mlflow.log_params({
                "grid_search_params": str(params)
            })
            
            clf = GridSearchCV(pipeline, params, cv=5, scoring='r2')
            clf.fit(X_train, y_train)
            best_model = clf.best_estimator_
            
            best_params = {"best_" + k: v for k, v in clf.best_params_.items()}
            mlflow.log_params(best_params)
        else:
            pipeline.fit(X_train, y_train)
            best_model = pipeline
        
        y_pred = best_model.predict(X_val)
        rmse, mae, r2 = eval_metrics(y_val, y_pred)
        
        mlflow.log_metrics({
            "rmse": rmse,
            "mae": mae,
            "r2": r2
        })
        
        signature = infer_signature(X_train, best_model.predict(X_train))
        mlflow.sklearn.log_model(best_model, model_name, signature=signature)
        
        return best_model


# In[47]:


# Датасеет: https://www.kaggle.com/datasets/nikhil7280/student-performance-multiple-linear-regression
# Загрузка датасета и начало работы
if __name__ == "__main__":
    df = pd.read_csv("clear_Student_Performance.csv")
    X_train, X_val, X_test, y_train, y_val, y_test = prepare_data(df)
    
    params = {
        'model__alpha': [0.0001, 0.001, 0.01],
        'model__l1_ratio': [0.15, 0.2, 0.25],
        'model__max_iter': [1000, 2000]
    }
    model = train_and_log_model(
        SGDRegressor(random_state=42),
        params,
        "model",
        X_train, y_train, X_val, y_val
    )
    
    pickle.dump(model, open('model.pkl', 'wb'))
    
    dfruns = mlflow.search_runs()
    path_to_model = dfruns.sort_values("metrics.r2", ascending=False).iloc[0]['artifact_uri'].replace("file://","") + '/model'
    with open("best_model.txt", "w") as file:
        file.write(path_to_model)




