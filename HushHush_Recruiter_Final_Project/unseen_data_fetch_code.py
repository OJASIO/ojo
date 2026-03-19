import requests
from collections import Counter 
import pandas as pd
#import numpy as np
import time
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
#print(GITHUB_TOKEN)
query = 'language:python'
#page = 10
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}
API_BASE_URL = 'https://api.github.com'
def get_usernames(query,page,requested_number_of_candidates):
    params = {'q': query, 'per_page': 30,'page': page}
    response = requests.get(f"{API_BASE_URL}/search/users", headers=HEADERS, params=params)
    #print(response)
    results = response.json().get('items', [])
    #print(results)
    username = []
    #print(results)
    for i in results:
        username.append(i['login'])
    print("Usernames are:",username)
    final_username = username[:requested_number_of_candidates]
    return final_username

def get_repo_data(username):
    all_candidate_repo_data = []
    for i in range(0,len(username)):
         #print(username[i])
         total_stars = 0
         total_forks = 0
         owned_repo_count = 0
         #total_open_issue_count = 0
         total_repo_issues_enabled_count = 0
         total_repo_discussions_enabled_count = 0
         email_data = requests.get(f"{API_BASE_URL}/users/{username[i].strip()}", headers=HEADERS)
         email_response  = email_data.json()
         candidate_email = email_response['email']
         all_languages = []
         primary_language_list =[]
         language_counts = Counter()
         #print(f"{API_BASE_URL}/users/{username[i].strip()}/repos")
         repo_response = requests.get(f"{API_BASE_URL}/users/{username[i].strip()}/repos", headers=HEADERS)
         #print(repo_response)
         repo_result = repo_response.json()
         for repo in repo_result:
            if not repo['fork']:
                owned_repo_count += 1
                total_stars += repo['stargazers_count']
                total_forks += repo['forks_count']
               # total_open_issue_count +=repo['open_issues_count']
                if repo.get('has_issues'):
                    total_repo_issues_enabled_count+=1
                if repo.get('has_discussions'):
                    total_repo_discussions_enabled_count+=1
                lang = repo.get('language')
                # Count the occurrences of each language
                if lang is not None:
                    all_languages.append(lang)
         if all_languages:
                    language_counts = Counter(all_languages)
                    sort_language = language_counts.most_common()
                    highest_language_count=sort_language[0][1]
                    for lang,count in sort_language:
                        if count == highest_language_count:
                            primary_language_list.append(lang)
                        else:
                            break

         else:
              primary_language_list = []
         total_pull_requests_created = number_of_pr_created(username[i])
         total_pull_requests_merged = number_of_merged_pr(username[i])
         event_type_details = get_events_type_count(username[i])
         total_open_issue_count = number_of_open_issues_count(username[i])
         total_closed_issue_count = number_of_closed_issues_count(username[i])
         #print(event_type_details)
         repo_details = {'name':repo['name'],
                            'username':username[i],
                            'Email':candidate_email,
                        'stargazers_count':total_stars,
                        'is_fork':repo['fork'],
                        'forks_count':total_forks,
                        'language_count':dict(language_counts),
                        'primary_language': primary_language_list,
                        'Open_Issues_Count':total_open_issue_count,
                        'Closed_Issues_Count':total_closed_issue_count,
                        'Total_Repo_Issues_Enabled_Count':total_repo_issues_enabled_count,
                        'Total_Repo_Discussions_Enabled_Count':total_repo_discussions_enabled_count,
                        'Number_of_Pull_Requests_Created':total_pull_requests_created,
                        'Number_of_Pull_Requests_Merged':total_pull_requests_merged,
                        'Number_of_Push_Events':event_type_details['Number_of_PushEvent'],
                        'Number_of_Create_Events':event_type_details['Number_of_Create_Event'],
                        'Number_of_Pull_Requests_Events':event_type_details['Number_of_Pull_Requests_Event'],
                        'Number_of_Watch_Event':event_type_details['Number_of_Watch_Event'],
                        'Number_of_Issues_Event':event_type_details['IssuesEvent']}
         
         #print("Repo_Details are:",repo_details)
         repo_dict = {'candidate':username[i],
                      'Email':candidate_email,
        'total_stargazers': total_stars,
        'total_forks': total_forks,
        'language_count':dict(language_counts),
        'primary_language': primary_language_list,
        'Open_Issues_Count':total_open_issue_count,
        'Closed_Issues_Count':total_closed_issue_count,
        'Total_Repo_Issues_Enabled_Count':total_repo_issues_enabled_count,
        'Total_Repo_Discussions_Enabled_Count':total_repo_discussions_enabled_count,
        'Number_of_Pull_Requests_Created':total_pull_requests_created,
        'Number_of_Pull_Requests_Merged':total_pull_requests_merged,
        'Number_of_Push_Events':event_type_details['Number_of_PushEvent'],
        'Number_of_Create_Events':event_type_details['Number_of_Create_Event'],
        'Number_of_Pull_Requests_Events':event_type_details['Number_of_Pull_Requests_Event'],
        'Number_of_Watch_Event':event_type_details['Number_of_Watch_Event'],
        'Number_of_Issues_Event':event_type_details['IssuesEvent']
    }
         all_candidate_repo_data.append(repo_dict)
         time.sleep(2)
         #print(all_candidate_repo_data)
         #print("After exit :",all_candidate_repo_data)
    return all_candidate_repo_data

def number_of_pr_created(username):
    try:
        print(f"Fetching PR details for {username}")
        pr_create_query = f"type:pr author:{username}"
        pr_params = {'q': pr_create_query}
        time.sleep(1)
        pr_api_response = requests.get(f"{API_BASE_URL}/search/issues", headers=HEADERS,params=pr_params)
        pr_api_response.raise_for_status()
        Total_PR_created = pr_api_response.json().get('total_count', 0)
        #print(f"Total_PR_Created for {username}",Total_PR_created)
        return Total_PR_created
    except requests.exceptions.RequestException as e: ###Introduced this step as facing issue while fetching merge pr count
        print(f"API request failed: {e}")
        return None 


def number_of_merged_pr(username):
    print(f"Fetching merged PR count for {username}")
    try:
        pr_merged_query = f"type:pr author:{username} is:merged"
        pr_merge_params = {'q':pr_merged_query}
        time.sleep(1)
        pr_merge_api_response = requests.get(f"{API_BASE_URL}/search/issues", headers=HEADERS,params=pr_merge_params)
        pr_merge_api_response.raise_for_status()
        Total_PR_Merge_Count = pr_merge_api_response.json().get('total_count', 0)
        return Total_PR_Merge_Count
    except requests.exceptions.RequestException as e: ###Introduced this step as facing issue while fetching merge pr count
        print(f"API request failed: {e}")
        return None

def get_events_type_count(username):
    print(f"Fetching Events type count for {username}")
    try:
        event_params = {'per_page': 100}
        events_type_count_response = requests.get(f"{API_BASE_URL}/users/{username}/events", headers=HEADERS,params=event_params)
        events_type_count_response.raise_for_status()
        events_type_count = events_type_count_response.json()
        if not events_type_count:
            print(f"No event actions found for user {username}")
            total_event_type_count = {    'Number_of_PushEvent':0,
            'Number_of_Create_Event':0,
            'Number_of_Pull_Requests_Event':0,
            'Number_of_Watch_Event':0,
            'IssuesEvent':0
        }
            return total_event_type_count
        event_types = [events['type'] for events in events_type_count]
        # Count the frequency of all event types --> Counter({'PushEvent': 3, 'WatchEvent': 2, 'CreateEvent': 1})
        event_counts = Counter(event_types)
        total_event_type_count = {
            'Number_of_PushEvent':event_counts.get('PushEvent', 0),
            'Number_of_Create_Event':event_counts.get('CreateEvent',0),
            'Number_of_Pull_Requests_Event':event_counts.get('PullRequestEvent',0),
            'Number_of_Watch_Event':event_counts.get('WatchEvent',0),
            'IssuesEvent':event_counts.get('IssuesEvent',0)
        }
        print("total_event_type_count is:",total_event_type_count)
        return total_event_type_count
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

def number_of_open_issues_count(username):
    query = f"author:{username} is:issue"
    open_issue_params = {'q': query}
    try:
        number_of_open_issues_count_response = requests.get(f"{API_BASE_URL}/search/issues", headers=HEADERS,params=open_issue_params)
        number_of_open_issues_count_response.raise_for_status()
        Total_open_Issues_Count = number_of_open_issues_count_response.json().get('total_count', 0)
        time.sleep(2)
        return Total_open_Issues_Count
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None


def number_of_closed_issues_count(username):
    query = f"author:{username} is:issue is:closed"
    closed_issue_params = {'q': query}
    try:
        number_of_closed_issues_count_response = requests.get(f"{API_BASE_URL}/search/issues", headers=HEADERS,params=closed_issue_params)
        number_of_closed_issues_count_response.raise_for_status()
        Total_Closed_Issues_Count = number_of_closed_issues_count_response.json().get('total_count', 0)
        time.sleep(2)
        return Total_Closed_Issues_Count
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

def github_data_fetch(job_role,number_of_candidates):
    print("Job role is:",job_role)
    github_start_page = 31
    github_end_page = 31
    requested_number_of_candidates = number_of_candidates
    all_pages_combined_df = []
    for page_number in range(github_start_page,github_end_page+1):
        print(f"Processing page {page_number}")
        x = get_usernames(query,page_number,requested_number_of_candidates)
        repo_data = get_repo_data(x)
        #print(repo_data)
        df = pd.DataFrame(repo_data)
        ###filling na value with 0 for below 2 fields as value was not fetch during api call as getting failed with request.exception error 403
        df['Number_of_Pull_Requests_Created'] = df['Number_of_Pull_Requests_Created'].fillna(0).astype(int)
        df['Number_of_Pull_Requests_Merged'] = df['Number_of_Pull_Requests_Merged'].fillna(0).astype(int)
        all_pages_combined_df.append(df)
        time.sleep(1)
    print(f"Data Processing completed for {number_of_candidates} candidates")
    final_df = pd.concat(all_pages_combined_df, ignore_index=True)
    #print(final_df)
    print(f"Final Dataframe consists of:{final_df.shape}")
    final_df.to_csv("D:/python/HushHush/Unseen_Data_Github_Fetch.csv",index = False)
    return final_df
