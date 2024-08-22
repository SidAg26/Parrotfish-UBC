import json
import subprocess
import time

# Path to the configuration file
config_file_path = './config-pagerank.json'
# Path to the results file
results_file_path = './results-graph-pagerank.json'
# Payload file path 
payload_file_path = '/home/ubuntu/memFigLessDIR/Mem-Fig-Less/estimation-algorithms/results-graph-pagerank.json'

# Function to update the payload in the configuration file
def update_config(payload):
    # Read the existing configuration file
    with open(config_file_path, 'r') as file:
        config = json.load(file)
    
    # Update the payload
    config['payload'] = payload
    
    # Save the updated configuration file
    with open(config_file_path, 'w') as file:
        json.dump(config, file, indent=4)

# # Function to update the payload in the configuration file
# def update_config(payload, mean_duration):
#     # Read the existing configuration file
#     with open(config_file_path, 'r') as file:
#         config = json.load(file)
    
#     # # Update the payload
#     # config['payload'] = payload
#     # Update the payloads
#     config['payloads'] = [{'payload': n, 'weight': 1/len(payload)} for n in payload]
#     config['constraint_execution_time_threshold'] = mean_duration
#     # Save the updated configuration file
#     with open(config_file_path, 'w') as file:
#         json.dump(config, file, indent=4)


# Function to run Parrotfish with the updated configuration file
def run_parrotfish():
    command = f'nohup parrotfish  --path {config_file_path}'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print("Result of parrotfish:", result)
    output = result.stdout.strip()
    return output

# Function to save the result to a file
def save_result(result, payload, end):
    # Read the existing results file or create a new one
    try:
        with open(results_file_path, 'r') as file:
            results = json.load(file)
    except FileNotFoundError:
        results = []

    # Append the new result
    results.append({'payload': payload, 'result': result, 'processing_time': end})

    # Save the updated results file
    with open(results_file_path, 'w') as file:
        json.dump(results, file, indent=4)
# # Function to save the result to a file
# def save_result(result, payload):
#     # Read the existing results file or create a new one
#     try:
#         with open(results_file_path, 'r') as file:
#             results = json.load(file)
#     except FileNotFoundError:
#         results = []

#     # Append the new result
#     results.append({'payload': payload, 'result': result})

#     # Save the updated results file
#     with open(results_file_path, 'w') as file:
#         json.dump(results, file, indent=4)

payload_list = []
# Read the JSON file
with open(payload_file_path, 'r') as file:
    _payload = json.load(file)

# Extract the 'payload' key from every list item
payload_list = [{'n': int(item['payload']) if type(item['payload']) is not int else item['payload'] } for item in _payload]
# _duration = [item['billed_duration'] for item in _payload]
# mean_duration = int((sum(_duration) / len(_duration))*1.1)
mean_duration = int(870 * 1.5) # 50% increase in the mean duration from metadata

print(payload_list)
# Iterate over the payloads and run Parrotfish
for item in payload_list[:20]:
    # Update the configuration file with the new payload
    update_config(item)
    print(f"Running Parrotfish with payload: {item}")
    start = time.time()
    result = run_parrotfish()
    end = time.time() - start
    # Save the result to a file
    save_result(result, item, end)

# # print(payload_list)
# update_config(payload_list, mean_duration)
# print(f"Running Parrotfish with payload: {payload_list} with mean duration: {mean_duration}")
# # Iterate over the payloads and run Parrotfish
# for i in range(0, len(payload_list), 5):
#     subset = payload_list[i:i+5]
#     # Update the configuration file with the new payload subset
#     update_config(subset, mean_duration)
#     print(f"Running Parrotfish with payload subset: {subset}")
#     result = run_parrotfish()
#     # Save the result to a file
#     save_result(result, subset)



# Iterate over the payloads and run Parrotfish
# for item in payload_list:
#     # Update the configuration file with the new payload
#     update_config(item)
#     print(f"Running Parrotfish with payload: {item}")
#     result = run_parrotfish()
#     # Save the result to a file
#     save_result(result, item)

