import json
import subprocess

# Path to the configuration file
config_file_path = './config-graph-mst.json'
# Path to the results file
results_file_path = './results-graph-mst.json'

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


# Function to run Parrotfish with the updated configuration file
def run_parrotfish():
    command = f'nohup parrotfish  --path {config_file_path}'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print("Result of parrotfish:", result)
    output = result.stdout.strip()
    return output

# Function to save the result to a file
def save_result(result, payload):
    # Read the existing results file or create a new one
    try:
        with open(results_file_path, 'r') as file:
            results = json.load(file)
    except FileNotFoundError:
        results = []

    # Append the new result
    results.append({'payload': payload, 'result': result})

    # Save the updated results file
    with open(results_file_path, 'w') as file:
        json.dump(results, file, indent=4)

payload_list = []
for i in range(10, 10000, 100):
    payload_list.append({'n': i})

print(payload_list)
# Iterate over the payloads and run Parrotfish
for item in payload_list:
    # Update the configuration file with the new payload
    update_config(item)
    print(f"Running Parrotfish with payload: {item}")
    result = run_parrotfish()
    # Save the result to a file
    save_result(result, item)

