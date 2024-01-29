import requests
import json
import toml

import prometheus_client as prom
from prometheus_client import start_http_server
import subprocess
import time
import schedule
from logger import log
config = toml.load('config.toml')
rpcaddress = config['default'].get('rpcaddress')

prom.REGISTRY.unregister(prom.PROCESS_COLLECTOR)
prom.REGISTRY.unregister(prom.PLATFORM_COLLECTOR)
prom.REGISTRY.unregister(prom.GC_COLLECTOR)


node_block_height = prom.Gauge(
    'solana_node_block_height', 'Nodes latest block height')
node_health = prom.Gauge(
    'Health', 'Node Health Status'
)


def get_block_height():
    url = rpcaddress
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBlockHeight"
    })

    try:
        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            json_data = response.json()

            if "result" in json_data:
                blockHeight = json.dumps(json_data['result'])
                print(f"Block Height: {blockHeight}")
                node_block_height.set(blockHeight)
            else:
                print("Error: Response does not contain 'result'.")
                print(json_data)
        else:
            print(f"Error: {response.status_code} - {response.reason}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


functions_to_schedule = [get_block_height]
for function in functions_to_schedule:
    schedule.every(15).seconds.do(function)

if __name__ == '__main__':
    start_http_server(1234)
    log.info("Metrics Server Has started on http://localhost:1234 ")
    while True:
        schedule.run_pending()
        time.sleep(1)
