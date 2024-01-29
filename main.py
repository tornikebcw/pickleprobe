import toml
import subprocess
from logger import log

# Load the config.toml file
config = toml.load('config.toml')

# Assign the variables
client_type = config.get('default', {}).get('client')

# Mapping client type to the respective script
client_script_map = {
    'evm': 'evm.py',
    'solana': 'solana.py'
}

# Check if the client value is in the mapping
if client_type in client_script_map:
    script_to_run = client_script_map[client_type]
    log.info(f"Running script: {script_to_run}")

    try:
        subprocess.run(['python', script_to_run], check=True)
    except subprocess.CalledProcessError as e:
        log.error(f"An error occurred while running {script_to_run}: {e}")
else:
    log.error(
        f"Client configuration '{client_type}' is not valid or not supported.")
