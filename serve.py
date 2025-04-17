#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask, request, jsonify
import pandas as pd
import pickle

app = Flask(__name__)

# Загрузка модели
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Получение данных
        data = request.get_json()
        df = pd.DataFrame([data])
        
        # Предсказание
        prediction = model.predict(df)
        
        # Возврат результата
        return jsonify({'prediction': prediction[0]})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

