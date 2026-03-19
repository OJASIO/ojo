import pandas as pd
import ast
import numpy as np
from sklearn.preprocessing import StandardScaler
import os
from sqlalchemy import create_engine, text
import json
import pickle
import psycopg2

db_user = os.getenv('db_user')
db_password = os.getenv('db_password')
db_host = os.getenv('db_host')
db_port = os.getenv('db_port')
db_name = os.getenv('db_name')
table_name = os.getenv('table_name')
schema=os.getenv('schema')

def replace_language(lang_list):
    new_list = ['Python' if lang == 'Jupyter Notebook' else lang for lang in lang_list]
    return list(set(new_list))

def load_scaler_from_db(scaler_name: str):
    conn = None
    loaded_scaler = None
    try:
        conn = psycopg2.connect(
            dbname= db_name, user= db_user, password= db_password, host= db_host
        )
        cursor = conn.cursor()
        sql_select_query = f"""SELECT scaler_object FROM "HushHush".scalers WHERE scaler_name = %s"""
        cursor.execute(sql_select_query, (scaler_name,))
        record = cursor.fetchone()
        if record:
            pickled_object_bytes = record[0]
            loaded_scaler = pickle.loads(pickled_object_bytes)
            print(f"Scaler '{scaler_name}' loaded successfully from database.")
        else:
            print(f"No scaler found with the name '{scaler_name}'.")

    except (Exception, psycopg2.Error) as error:
        print(f"Error while fetching scaler: {error}")

    finally:
        if conn:
            cursor.close()
            conn.close()
    
    return loaded_scaler

def load_model_from_db(model_name: str):
    conn = None
    loaded_model = None
    try:
        conn = psycopg2.connect(
            dbname= db_name, user= db_user, password= db_password, host= db_host
        )
        cursor = conn.cursor()
        sql_select_query = f"""SELECT model_object FROM "HushHush".models WHERE model_name = '{model_name}'"""
        cursor.execute(sql_select_query, (model_name,))
        record = cursor.fetchone()
        if record:
            pickled_object_bytes = record[0]
            loaded_model = pickle.loads(pickled_object_bytes)
            print(f"Model '{model_name}' loaded successfully from database.")
        else:
            print(f"No model found with the name '{model_name}'.")
    except (Exception, psycopg2.Error) as error:
        print(f"Error while fetching model from database: {error}")
    finally:
        if conn:
            cursor.close()
            conn.close()
    return loaded_model
    
def data_transformation():
    print("Data Transformation Process Starts")
    connection_str = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(connection_str)
    connection = engine.connect()
    query = """
select * from "HushHush"."Github_Candidates_Unseen_Data_Fetch";
"""
    df = pd.read_sql(query,connection)
    print(df.shape)
    df['Email'] = df['Email'].fillna('lassosrhpythonproject@gmail.com')
    df['primary_language'] = df['primary_language'].apply(ast.literal_eval)
    df['primary_language'] = df['primary_language'].apply(replace_language)
    df['PR_Merge_Percentage'] = (df['Number_of_Pull_Requests_Merged']/df['Number_of_Pull_Requests_Created'])*100
    df['Closed_Issue_Percentage'] = (df['Closed_Issues_Count']/df['Open_Issues_Count'])*100
    df['Github_Activity_Score'] = df['Number_of_Push_Events']+ df['Number_of_Pull_Requests_Events']+df['Number_of_Issues_Event']
    df['PR_Merge_Percentage'] = df['PR_Merge_Percentage'].round(2).fillna(0)
    df['Closed_Issue_Percentage'] = df['Closed_Issue_Percentage'].round(2).fillna(0)
    df['Github_Activity_Score'] = df['Github_Activity_Score'].fillna(0)
    df_final = df
    print("Removing Extreme Outliers")
    df_final = df_final[df_final['total_stargazers']<=50000]
    df_final= df_final[df_final['Open_Issues_Count']<=5000]
    df_final= df_final[df_final['total_forks']<=5000]
    df_final= df_final[df_final['Closed_Issues_Count']<=1250]
    df_final = df_final[df_final['Number_of_Pull_Requests_Created']<=4000]
    df_final = df_final[df_final['Number_of_Pull_Requests_Merged']<=2500]
    print("Cleaned and Transformed Data Frame records are:",df_final.shape)
    scaled_and_normalized_df = data_scaling_and_normalization(df_final)
    print(scaled_and_normalized_df)
    predictions = []
    for idx in range(len(scaled_and_normalized_df)):
        single_candidate_features_1d = scaled_and_normalized_df.iloc[idx]
        single_candidate_features_2d = np.array(single_candidate_features_1d).reshape(1, -1)
        prediction_result = model_predict(single_candidate_features_2d)
        predictions.append(prediction_result[0])
    features_to_use = ['candidate',
    'total_stargazers',
    'total_forks',
    'Total_Repo_Issues_Enabled_Count',
    'PR_Merge_Percentage',
    'Closed_Issue_Percentage']
    df_final = df_final[features_to_use]
    df_final['Status'] = predictions
    return df_final

def data_scaling_and_normalization(df):
    print("Data Standardization and Normalization Function execution starts")
    features_to_use = [
    'total_stargazers',
    'total_forks',
    'Total_Repo_Issues_Enabled_Count',
    'PR_Merge_Percentage',
    'Closed_Issue_Percentage']
    df_features = df[features_to_use]
    log_scaled_df = np.log1p(df_features)
    my_scaler = load_scaler_from_db('standard_scaler_v1')
    features_scaled = my_scaler.fit_transform(log_scaled_df)
    features_scaled_df = pd.DataFrame(features_scaled, columns=features_to_use)
    print("Feature Scaled DataFrame shape is:",features_scaled_df.shape)
    return features_scaled_df

def model_predict(features_scaled_df):
    print("Model Prediction Starts")
    loaded_model = load_model_from_db('logistic_regression_v1')
    print("Model has been loaded successfully from models database")    
    predictions = loaded_model.predict(features_scaled_df)
    status_map = {0: 'Selected', 1: 'Not Selected'}
    predictions = [status_map[p] for p in predictions]
    return predictions