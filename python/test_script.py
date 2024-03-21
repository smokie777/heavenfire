import requests
from concurrent.futures import ThreadPoolExecutor

def send_request(i):
    url = 'http://localhost:5001/receive_prompt'
    json_data = {
        'prompt': f'Vedal987 just gifted a tier 1 sub to anny{i}{i}{i}!',
        'priority': 'PRIORITY_PUBSUB_EVENTS_QUEUE'
    }
    response = requests.post(url, json=json_data)
    return response.status_code

# List to hold all your futures
futures = []

# Using ThreadPoolExecutor to send requests in parallel
with ThreadPoolExecutor(max_workers=10) as executor:
    for i in range(9):
        # Submitting the send_request function to the executor
        futures.append(executor.submit(send_request, i))