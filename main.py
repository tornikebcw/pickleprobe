from web3 import Web3, HTTPProvider
import prometheus_client as prom
from prometheus_client import start_http_server
import subprocess
import time
import schedule
import os

print(os.uname()[1])

prom.REGISTRY.unregister(prom.PROCESS_COLLECTOR)
prom.REGISTRY.unregister(prom.PLATFORM_COLLECTOR)
prom.REGISTRY.unregister(prom.GC_COLLECTOR)

w3 = Web3(HTTPProvider("http://44.227.34.159:8008/rpc"))

peer_gauge = prom.Gauge(
    'peer_count', 'Number of peers in the Ethereum network')
latest_block = prom.Gauge(
    'latest_block', 'latest block number of the blockchain')
node_sync_gauge = prom.Gauge(
    'syncing', 'Node Syncing Status'
)
blocks_to_syn_gauge = prom.gauge(
    'blocks_to_sync', 'Blocks node needs to catch up')

bor_status_gauge = prom.Gauge(
    '{}_status'.format('bor'), 'Status of the Service', ['service_name'])
heimdall_status_gauge = prom.Gauge(
    '{}_status'.format('heimdall'), 'Status of the Service', ['service_name'])

netinfo = prom.Gauge(
    'network_name', 'network-name')


def check_syncing():
    try:
        syncing = w3.eth.syncing
        if syncing:
            node_sync_gauge.set(0)
            blocks_to_syn_gauge.set(
                syncing['highestBlock'] - syncing['currentBlock'])
        else:
            print("Node is synced")
            node_sync_gauge.set(1)
    except Exception as err:
        print("An error occurred:", err)


def current_head():
    try:
        head = w3.eth.block_number
        latest_block.set(int(head))
        print("latest block number:", head)
    except Exception as err:
        print("Bad Shit went down:", err)


def peerCount():
    try:
        count = w3.net.peer_count
        peer_gauge.set(count)
        print("Peers:", count)
    except Exception as err:
        print("Bad Shit went down:", err)


def netVersion():
    try:
        version = w3.net.version
        if version == "137":
            print("Polygon-Mainnet")
            netinfo.set(version)
        else:
            print(version)
    except Exception as err:
        print("Bad Shit went down:", err)


def check_service(service):
    try:
        output = subprocess.check_output(
            ["systemctl", "is-active", service],
            universal_newlines=True
        )
        if output.strip() == "active":
            service_status_gauge.labels(service_name=service).set(1)
        else:
            service_status_gauge.labels(service_name=service).set(0)
    except subprocess.CalledProcessError:
        service_status_gauge.labels(service_name=service).set(0)


schedule.every(15).seconds.do(peerCount)
schedule.every(15).seconds.do(check_syncing)
schedule.every(15).seconds.do(current_head)
schedule.every(15).seconds.do(netVersion)

# schedule.every(15).seconds.do(check_service("bor"))
# schedule.every(15).seconds.do(check_service("heimdall"))

if __name__ == '__main__':
    start_http_server(3000)
    print("Metrics Server Has started on http://localhost:3000 ")
    while True:
        schedule.run_pending()
        time.sleep(1)
