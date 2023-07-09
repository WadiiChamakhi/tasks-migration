# Manually migrate tasks from one Google account to another using Google Tasks API

from Google import Create_Service, convert_to_RFC_datetime
from dotenv import load_dotenv  # Environmental variables
import json
import os
import re
import emoji
import time
import sys

load_dotenv()

sys.stdout.reconfigure(encoding='utf-8')


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

        request_body = {
            'title': "No title"
        }
        
        if 'title' in task:
            request_body['title'] = task['title']

        if 'kind' in task:
            request_body['kind'] = task['kind']

        if 'id' in task:
            request_body['id'] = task['id']

        if 'etag' in task:
            request_body['etag'] = task['etag']

        if 'updated' in task:
            request_body['updated'] = task['updated']


        if 'selfLink' in task:
            request_body['selfLink'] = task['selfLink']


        if 'position' in task:
            request_body['position'] = task['position']
        
        if 'status' in task:
            request_body['status'] = task['status']

        
        if 'completed' in task:
            request_body['completed'] = task['completed']

        if 'deleted' in task:
            request_body['deleted'] = task['deleted']


        if 'hidden' in task:
            request_body['hidden'] = task['hidden']


        # Include due date if available
        if 'due' in task:
            request_body['due'] = task['due']

        # Include task_type if available
        if 'task_type' in task:
            request_body['task_type'] = task['task_type']

        # Include notes if available
        if 'notes' in task:
            request_body['notes'] = task['notes']

        # Include links or attachments if available
        if 'links' in task:
            request_body['links'] = task['links']

        return request_body
    except Exception as e:
        print(f"Erreur lors de la construction du corps de la requête pour la tâche : {task['title']}")
        print(e)
        return None

total_tasks = 0  # Le nombre total de tâches
added_tasks = 0  # Le nombre de tâches ajoutées

# Compter le nombre total de tâches
for task_list in tasks:
    total_tasks += len(task_list['items'])

# Insert tasks into their respective lists
for task_list in tasks:
    task_list_id = extract_list_id_from_url(task_list['selfLink'])
    print(f"Pour la Liste {task_list['title']} : {task_list_id}")

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
        parent_id = task.get('parent')
        if parent_id:
            parent_task = next(
                (t for t in task_list['items'] if t['id'] == parent_id),
                None
            )
            if not parent_task:
                print(f"La tâche parente pour la tâche {task['title']} n'existe pas. La tâche sera ignorée.")
                continue  # Skip the task if the parent task doesn't exist

        request_body = construct_request_body(task)
        if request_body:
            if parent_id:
                request_body['parent'] = parent_task['id']

            service.tasks().insert(tasklist=task_list_id, body=request_body).execute()
            added_tasks += 1

            # Calculer le pourcentage de tâches ajoutées
            percentage = (added_tasks / total_tasks) * 100
            print(f"Tâche {task['title']} ajoutée à la liste {task_list['title']}")
            print(f"Tâches : {added_tasks}/{total_tasks} - {percentage:.2f}%")
            time.sleep(3)  # Sleep for 3 seconds to avoid rate limiting

print("END")
