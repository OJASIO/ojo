from flask import Flask, render_template, request, session, redirect, url_for, Response
import joblib
import pandas as pd
import random
import string
from sqlalchemy import create_engine, text, exc
from unseen_data_fetch_code import github_data_fetch
from Data_Transformation_and_Model_Prediction import data_transformation
from Email_Notification import send_selection_email, send_rejection_email,send_acceptance_email
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

db_user = os.getenv('db_user')
db_password = os.getenv('db_password')
db_host = os.getenv('db_host')
db_port = os.getenv('db_port')
db_name = os.getenv('db_name')
schema = os.getenv('schema')
app.secret_key = os.getenv('SECRET_KEY')
CODE_FOLDER = 'candidate_codes'

def connect_to_db(db_user, db_password, db_host, db_port, schema):
    """Establishes a connection to the PostgreSQL database."""
    try:
        connection_str = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(connection_str)
        connection = engine.connect()
        return connection
    except exc.SQLAlchemyError as e:
        print(f"Error creating database engine: {e}")
        return None   

def generate_credentials(username):
    """Generating  a random password."""
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    return  password

def parse_test_results(test_results):
    """
    Parses the test results to check if all test cases passed.
    Returns 'Passed' if all tests pass, otherwise 'Failed'.
    """
    if not isinstance(test_results, list):
        return 'Failed'
        
    for case in test_results:
        if case.get('status') != 'Passed':
            return 'Failed'
    
    return 'Passed'


@app.route('/', methods=['GET','POST'])
def index():
    """Renders the main page with the input form."""
    if 'username' not in session:
        return redirect(url_for('login'))
        
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles the login process."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        connection = connect_to_db(db_user, db_password, db_host, db_port, schema)
        if connection:
            try:
                query = text(f'''SELECT ui_password FROM "{schema}"."security_credentials" WHERE username = '{username}' and role_type = 'Hiring_Manager' ''')
                result = connection.execute(query).fetchone()
                connection.close()
                
                if result and result[0] == password:
                    session['username'] = username
                    return redirect(url_for('index'))
                else:
                    return render_template('login.html', error="Invalid username or password.")
            except exc.SQLAlchemyError as e:
                print(f"Database error during login: {e}")
                return render_template('login.html', error="A database error occurred.")
        else:
            return render_template('login.html', error="Could not connect to the database.")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logs the user out by clearing the session."""
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/process', methods=['POST'])
def process():
    job_role = request.form.get('job_role')
    num_candidates = int(request.form.get('num_candidates'))
    
    candidates_data_df = github_data_fetch(job_role, num_candidates)
    json_columns = ['language_count', 'primary_language']
    for col in json_columns:
        candidates_data_df[col] = candidates_data_df[col].apply(lambda x: json.dumps(x) if pd.notna(x) else None)
    
    if candidates_data_df.empty:
        return render_template('index.html', error="Could not find any candidates.Try a different role.")
    
    db_connect = connect_to_db(db_user, db_password, db_host, db_port, schema)
    candidates_data_df.to_sql("Github_Candidates_Unseen_Data_Fetch", db_connect, schema=schema, if_exists='replace', index=False)
    print("candidate data df shape is:",candidates_data_df.shape)
    data_transformed_df = data_transformation()
    for index, row in data_transformed_df.iterrows():
        if row['Status'] == 'Selected':
            username = row['candidate']
            password = generate_credentials(username)
            dicto = {'username': [username], 'ui_password': [password], 'role_type': 'candidate'}
            df_cred = pd.DataFrame(dicto)
            sc_temp_table_name = "sc_temp_data_load"
            df_cred.to_sql(sc_temp_table_name, db_connect, schema=schema, if_exists='replace', index=False)
            sc_primary_key = "username"
            update_cols = [f'"{col}" = EXCLUDED."{col}"' for col in df_cred.columns if col != sc_primary_key]
            upsert_sql = text(f"""
            INSERT INTO "{schema}"."security_credentials" ({", ".join([f'"{col}"' for col in df_cred.columns])})
            SELECT {", ".join([f'"{col}"' for col in df_cred.columns])} FROM "{schema}"."{sc_temp_table_name}"
            ON CONFLICT ("{sc_primary_key}")
            DO UPDATE SET {", ".join(update_cols)};
            """)
            db_connect.execute(upsert_sql)
            db_connect.commit()
            link = "http://127.0.0.1:5002/login"
            send_selection_email(username, password, link)
            print("Inserting the record into candidate_status table")
            candidate_status_dict = {'username':[username],'selection_status':['In_Review']}
            candidate_status_df = pd.DataFrame(candidate_status_dict)
            candidate_status_df.to_sql("candidate_status", db_connect, schema=schema, if_exists='append', index=False)
            

    results_for_template = [
        {
            'username': row['candidate'],
            'status': row['Status']
        }
        for index, row in data_transformed_df.iterrows()
    ]
    print(results_for_template)
    return render_template('index.html', results=results_for_template)

@app.route('/coding_evaluation')
def coding_evaluation():
    if 'username' not in session:
        return redirect(url_for('login'))

    connection = connect_to_db(db_user, db_password, db_host, db_port, schema)
    if not connection:
        return render_template('coding_evaluation.html', error="Could not connect to the database.")

    try:
        query = text(f'''
            SELECT
                s.username,
                s.question_id,
                s.candidate_code,
                s.test_results,
                cs.selection_status
            FROM
                "{schema}"."submissions" AS s
            LEFT JOIN "{schema}"."candidate_status" AS cs
                ON s.username = cs.username
            ORDER BY s.username, s.question_id
        ''')
        result = connection.execute(query).fetchall()
        
        results_by_candidate = {}
        all_question_ids = set() # Store unique question IDs
        
        for row in result:
            candidate_name, question_id, code_string, test_results, current_status = row

            if candidate_name not in results_by_candidate:
                results_by_candidate[candidate_name] = {
                    'codes': {}, 
                    'statuses': {},
                    'current_status': current_status if current_status else 'In review'
                }
            
            try:
                parsed_test_results = json.loads(test_results)
            except (TypeError, json.JSONDecodeError):
                parsed_test_results = []
                
            status = parse_test_results(parsed_test_results)
            
            question_key = f'Question {question_id}'
            results_by_candidate[candidate_name]['codes'][question_key] = code_string
            results_by_candidate[candidate_name]['statuses'][question_key] = status
            
            all_question_ids.add(question_key) # Add to the set
            
        connection.close()

        sorted_question_ids = sorted(list(all_question_ids))
        
        if not results_by_candidate:
            return render_template('coding_evaluation.html', results=None, error="No coding evaluation results found.")

        return render_template('coding_evaluation.html', results=results_by_candidate, question_ids=sorted_question_ids)

    except exc.SQLAlchemyError as e:
        print(f"Database error during coding evaluation data fetch: {e}")
        return render_template('coding_evaluation.html', error="A database error occurred.")

@app.route('/accept_candidate', methods=['POST'])
def accept_candidate():
    if 'username' not in session:
        return redirect(url_for('login'))

    candidate_name = request.form.get('candidate_name')
    print("candidate name is:",candidate_name)
    if candidate_name:
        connection = connect_to_db(db_user, db_password, db_host, db_port, schema)
        if connection:
            try:
                update_query = text(f"""
                    update "{schema}"."candidate_status"
                    set selection_status = 'Accepted' where username = '{candidate_name}';
                """)
                connection.execute(update_query)
                connection.commit()

                query = text(f'''SELECT ui_password FROM "{schema}"."security_credentials" WHERE username = '{candidate_name}' AND role_type = 'candidate' ''')
                print(query)
                result = connection.execute(query, {'candidate_name': candidate_name}).fetchone()
                print("result output is:",result)
                #link = "https://doodle_onboarding_process.com"
                candidate_email = "lassosrhpythonproject@gmail.com"
                send_acceptance_email(candidate_name, candidate_email) 
                
                connection.close()
            except exc.SQLAlchemyError as e:
                print(f"Database error during candidate acceptance: {e}")
                connection.close()
    return redirect(url_for('coding_evaluation'))

@app.route('/reject_candidate', methods=['POST'])
def reject_candidate():
    if 'username' not in session:
        return redirect(url_for('login'))

    candidate_name = request.form.get('candidate_name')
    if candidate_name:
        connection = connect_to_db(db_user, db_password, db_host, db_port, schema)
        if connection:
            try:
                update_query = text(f"""
                   update "{schema}"."candidate_status"
                    set selection_status = 'Rejected' where username = '{candidate_name}';
                """)
                connection.execute(update_query)
                connection.commit()
                connection.close()

                candidate_email = "lassosrhpythonproject@gmail.com"
                send_rejection_email(candidate_name, candidate_email)
            except exc.SQLAlchemyError as e:
                print(f"Database error during candidate rejection: {e}")
                connection.close()
    
    return redirect(url_for('coding_evaluation'))

if __name__ == '__main__':
    app.run(port = 5005,debug=True)