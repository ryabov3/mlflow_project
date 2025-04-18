#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd

def download_dataset():
    df = pd.read_csv("https://raw.githubusercontent.com/ryabov3/mlflow_project/refs/heads/main/raw/Student_Performance.csv")
    df.to_csv("Student_Performance.csv", index=False)

def preprocess_dataset(path):
    df = pd.read_csv(path)
    df['Extracurricular Activities'] = df['Extracurricular Activities'].map({'Yes': 1, 'No': 0})
    
    df = df[(df['Hours Studied'] <= 24) & 
            (df['Sleep Hours'] >= 4) & 
            (df['Previous Scores'] >= 40)]
    df.to_csv("clear_Student_Performance.csv", index=False)

download_dataset()
preprocess_dataset("Student_Performance.csv")


# In[ ]:




