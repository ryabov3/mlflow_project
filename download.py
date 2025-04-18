#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import os

def download_dataset():
    df = pd.read_csv("https://raw.githubusercontent.com/ryabov3/mlflow_project/refs/heads/main/raw/Student_Performance.csv")
    output_path = os.path.expanduser("~/MLops_work/Student_Performance.csv")
    df.to_csv(output_path, index=False)
    os.chmod(output_path, 0o644)

def preprocess_dataset(path):
    df = pd.read_csv(path)
    df['Extracurricular Activities'] = df['Extracurricular Activities'].map({'Yes': 1, 'No': 0})
    
    df = df[(df['Hours Studied'] <= 24) & 
            (df['Sleep Hours'] >= 4) & 
            (df['Previous Scores'] >= 40)]
    output_path = os.path.expanduser("~/MLops_work/clear_Student_Performance.csv")
    df.to_csv(output_path, index=False)
    os.chmod(output_path, 0o644)

download_dataset()
preprocess_dataset(os.path.expanduser("~/MLops_work/Student_Performance.csv"))


# In[ ]:




