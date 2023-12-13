import argparse
import json
import re
import requests
import time
import yaml

from constants import NAME, URL, METHOD, HEADERS, BODY, MAX_LATENCY, TIMEOUT, GET, POST

# start time set at the beginning 
start_time = time.monotonic()
# dictionary storing all the domains and test outcome key : [count UP, count total]
HEALTH_RESULT = {}

def check_health(json_file):
    for i, data in enumerate(json_file):
        name = data[NAME]
        url = data[URL]
        if url not in HEALTH_RESULT:
            HEALTH_RESULT[url] = [0, 0]

        method = GET if METHOD not in data else data[METHOD]
        headers = None if HEADERS not in data else data[HEADERS]
        body = None if BODY not in data else data[BODY]
        response = None
        request_start_time = time.perf_counter()
        if method == GET:
            if body is None:
                if headers is None:
                    response = requests.get(url)
                else:
                    response = requests.get(url, headers=headers)
            else:
                if headers is None:
                    response = requests.get(url, data=json.dumps(body)) 
                else:
                    response = requests.get(url, headers=headers, data=json.dumps(body))
        elif method == POST:
            if body is None:
                if headers is None:
                    response = requests.post(url)
                else:
                    response = requests.post(url, headers=headers)
            else:
                if headers is None:
                    response = requests.post(url, data=json.dumps(body)) 
                else:
                    response = requests.post(url, headers=headers, data=json.dumps(body))

        request_time = time.perf_counter() - request_start_time
        if 200 <= response.status_code <= 299 and request_time < MAX_LATENCY: 
            HEALTH_RESULT[url][0] += 1
            HEALTH_RESULT[url][1] += 1
        else:
            HEALTH_RESULT[url][1] += 1
        
    for domain_name in HEALTH_RESULT.keys():
        percentage = round(100 * (HEALTH_RESULT[domain_name][0] / HEALTH_RESULT[domain_name][1]))
        log_message = domain_name + ' has ' + str(percentage) + '% availability percentage'
        print(log_message)
        

# require the user to provide a file path input
parser = argparse.ArgumentParser()
parser.add_argument('--path', help='Enter a file path to the YAML file')
args = parser.parse_args()

# Check file format is .yml or .yaml
file_path = args.path
pattern = re.compile('\S+.(yml|yaml)')
if pattern.match(file_path):
    try:
        with open(file_path, 'r') as file:
            json_file = yaml.safe_load(file)
            while True:
                check_health(json_file)
                # trigger every 15 seconds 
                time.sleep(TIMEOUT - ((time.monotonic() - start_time) % TIMEOUT))
    except FileNotFoundError:
        print('The input file was not found')
    except KeyError:
        print('YAML list has missing HTTP endpoint elements')
    except KeyboardInterrupt:
        print("Keyboard Interrupt - ending program")
        exit()
else:
    print('Wrong file path - file path should end with .yml or .yaml')
