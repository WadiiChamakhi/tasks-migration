# Manually migrate tasks from one Google account to another using Google Tasks API

from Google import Create_Service, convert_to_RFC_datetime
from dotenv import load_dotenv  # Environmental variables
import json
import os
import re
import emoji
import time

load_dotenv()

CLIENT_SECRET_FILE = 'client_secret_file.json'  # Get this from GCP
API_NAME = 'tasks'
API_VERSION = 'v1'
SCOPES = ['https://www.googleapis.com/auth/tasks']  # Read & write access

# Redirects to login page; sign in with desired Google account
service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
print(dir(service))

# Get default lists in the destination account
destination_lists = service.tasklists().list().execute()
destination_list_items = destination_lists.get('items', [])

# File with tasks to insert
with open('request_tasks.json', encoding='utf-8') as file:
    tasks = json.loads(file.read())

def extract_list_id_from_url(url):
    pattern = r'/lists/(.*?)/'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def construct_request_body(task):
    try:
        request_body = task
        return request_body
    except Exception:
        return None

# Insert tasks into their respective lists
for task_list in tasks:
    task_list_id = extract_list_id_from_url(task_list['selfLink'])

    # Find the corresponding list in the destination account
    matched_list = next(
        (destination_list for destination_list in destination_list_items if destination_list['id'] == task_list_id),
        None
    )

    # If the list doesn't exist, create it
    if not matched_list:
        list_title = task_list['title']
        new_list = service.tasklists().insert(body={'title': list_title}).execute()
        task_list_id = new_list['id']
    else:
        task_list_id = matched_list['id']

    # Insert the tasks into the corresponding list
    for task in task_list['items']:
        service.tasks().insert(tasklist=task_list_id, body=construct_request_body(task)).execute()
        print(f"Tache {task['title']} ajoutée à la liste {task_list['title']}".encode('utf-8'))
        time.sleep(3) # Sleep for 3 seconds to avoid rate limiting

print("END")
