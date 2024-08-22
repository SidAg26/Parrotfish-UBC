import boto3
import pickle
import io, json, os
import numpy as np
import pandas as pd
import time, re
import base64



def invoke_lambda(lambda_name, payload, memory):
    lambda_client = boto3.client('lambda', region_name='ap-southeast-2')

    # Check if there exists a version with the desired memory configuration
    try:
        response = lambda_client.list_versions_by_function(FunctionName=lambda_name)
        versions = [v['Version'] for v in response['Versions']]
        version_with_best_mem = None

        for version in versions:
            if version == '$LATEST':
                continue
            config = lambda_client.get_function_configuration(FunctionName=lambda_name, Qualifier=version)
            if config['MemorySize'] == memory:
                version_with_best_mem = version
                break

        if version_with_best_mem:
            print(f"Version {version_with_best_mem} of Lambda function {lambda_name} with memory {memory} exists.")
        else:
            print(f"No version of Lambda function {lambda_name} with memory {memory} exists. Creating version...")
            lambda_client.update_function_configuration(FunctionName=lambda_name, MemorySize=memory, Description=f'RAM{memory}')
            # wait for the configuration to be updated
            time.sleep(10)
            publish_response = lambda_client.publish_version(FunctionName=lambda_name)
            version_with_best_mem = publish_response['Version']
            lambda_client.create_alias(FunctionName=lambda_name, FunctionVersion=version_with_best_mem, Name=f'RAM{memory}')
            print(f"Version {version_with_best_mem} of Lambda function {lambda_name} created with memory {memory}.")
    except Exception as e:
        print(f"Error checking or creating Lambda function version: {e}")
        return

    # Invoke the Lambda function version
    try:
        if lambda_name == 'workbench-chameleon':
            payload = {
                    "num_of_rows": payload,
                    "num_of_cols": 25
                }
        elif lambda_name == 'workbench-pyaes':
            payload = {
                    "length_of_message": payload,
                    "num_of_iterations": 10
            }
        else:
            payload = {'n': payload}
        response = lambda_client.invoke(
            FunctionName=lambda_name,
            Qualifier=version_with_best_mem,
            LogType='Tail',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        print(f"Lambda function {lambda_name} version {version_with_best_mem} invoked.")
        # Get the Billed duration from response
        _log_result = base64.b64decode(response.get('LogResult')).decode('utf-8')
        billed_duration = extract_duration(_log_result)
        init_duration = extract_init_duration(_log_result)
        memory_size = extract_memory_size(_log_result)
        memory_used = extract_memory_used(_log_result)
        function_error = extract_function_error(_log_result)
    
        # return response['ResponseMetadata']['RequestId']
        return {
            'statusCode': 200,
            'body':{
                'RequestId': response['ResponseMetadata']['RequestId'],
                'BilledDuration': billed_duration,
                'InitDuration': init_duration,
                'MemorySize': memory_size,
                'MemoryUsed': memory_used,
                'FunctionError': function_error
            }
        }


    except Exception as e:
        print(f"Error invoking Lambda function version: {e}")
        return
    
def extract_function_error(log):
    regex = r'Error (?P<Error>.*)|'\
            r'Exception (?P<Exception>.*)|'\
            r'error (?P<error>.*)|'\
            r'Status (?P<Status>.*)'
    match = re.search(regex, log, re.IGNORECASE)
    if match:
        if match.group('Error'):
            return match.group('Error')
        elif match.group('Exception'):
            return match.group('Exception')
        elif match.group('error'):
            return match.group('error')
        elif match.group('Status'):
            return match.group('Status')
    return None

def extract_request_id(log):
    regex = r'^REPORT RequestId:\s+([a-f0-9-]+)'
    match = re.search(regex, log)
    if match:
        return match.group(1)
    return None

def extract_duration(log):
    regex = r'Billed Duration: (\d+) ms'
    match = re.search(regex, log)
    if match:
        return int(match.group(1))
    return None

def extract_init_duration(log):
    regex = r'Init Duration: (\d+)'
    match = re.search(regex, log)
    if match:
        return int(match.group(1))
    return None

def extract_memory_size(log):
    regex = r'Memory Size: (\d+) MB'
    match = re.search(regex, log)
    if match:
        return int(match.group(1))
    return None

def extract_memory_used(log):
    regex = r'Memory Used: (\d+) MB'
    match = re.search(regex, log)
    if match:
        return int(match.group(1))
    return None


function_name = 'sebs-graph-pagerank'
json_file_path = '/home/ubuntu/memFigLessDIR/Parrotfish-UBC/results-graph-pagerank.json'
with open(json_file_path, 'r') as file:
    json_data = json.load(file)

parsed_data = (json_data)
parsed_data = [x for x in parsed_data if 'processing_time' in x]
# Parse the JSON data
parsed_data = sorted(parsed_data, key=lambda x: x['payload']['n'])
# parsed_data = [x for x in parsed_data if 'init_duration' in x and x['init_duration'] is None]
payload = []
memory = []

for item in parsed_data:
    payload.append(item['payload']['n'])
    # Define the regular expression pattern
    pattern = r"Optimization result: (\d+)\.\d+ MB"

    # Search for the pattern in the string
    match = re.search(pattern, item['result'])

    # Extract the integer if a match is found
    if match:
        result = int(match.group(1))
        # print(f'Extracted integer: {result}')
    else:
        print('No match found for ipnut:', item['payload']['n'])
        result = 0
    memory.append(result)

for i in range(len(payload)):
    if memory[i] != 0:
        print(f"Invoking Lambda function {function_name} with payload {payload[i]} and memory {memory[i]}")
        _invoke_result = invoke_lambda(function_name, payload[i], memory[i])
        if _invoke_result:
            result_data = {
                'FunctionName': function_name,
                'Payload': payload[i],
                'Memory': memory[i],
                'RequestId': _invoke_result['body']['RequestId'],
                'BilledDuration': _invoke_result['body']['BilledDuration'],
                'InitDuration': _invoke_result['body']['InitDuration'],
                'MemorySize': _invoke_result['body']['MemorySize'],
                'MemoryUsed': _invoke_result['body']['MemoryUsed'],
                'FunctionError': _invoke_result['body']['FunctionError']
            }
            with open('pagerank_data.json', 'a') as file:
                json.dump(result_data, file)
                file.write('\n')
            print(f"Lambda function {function_name} invoked with payload {payload[i]} and memory {memory[i]}")
            print(f"Request ID: {_invoke_result['body']['RequestId']}")
            print(f"Billed Duration: {_invoke_result['body']['BilledDuration']} ms")
            print(f"Init Duration: {_invoke_result['body']['InitDuration']} ms")
            print(f"Memory Size: {_invoke_result['body']['MemorySize']} MB")
            print(f"Memory Used: {_invoke_result['body']['MemoryUsed']} MB")
            print(f"Function Error: {_invoke_result['body']['FunctionError']}")
        else:
            print(f"Error invoking Lambda function {function_name} with payload {payload[i]} and memory {memory[i]}")
    else:
        print(f"Skipping Lambda function {function_name} with payload {payload[i]} and memory {memory[i]}")
