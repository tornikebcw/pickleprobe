import toml
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


# Load the config file
config = toml.load('config.toml')

# Assign the variables
env = config['default'].get('env')
client = config['default'].get('client')
rpcaddress = config['default'].get('rpcaddress')


if env == 'dev':
    w3 = Web3(HTTPProvider('http://44.227.34.159:8008/rpc'))
    print("Env set to local, RPC is pointed to Dev Server")
elif not env:
    w3 = Web3(HTTPProvider('http://localhost:8545'))
    print("Env not set , Using default RPC Address")
else:
    w3 = Web3(HTTPProvider('rpcAddress'))
    print("RPC is pointed to:", rpcAddress)


peer_gauge = prom.Gauge(
    'peer_count', 'Number of peers in the Ethereum network')
latest_block = prom.Gauge(
    'latest_block', 'latest block number of the blockchain')
node_sync_gauge = prom.Gauge(
    'syncing', 'Node Syncing Status'
)
blocks_to_syn_gauge = prom.Gauge(
    'blocks_to_sync', 'Blocks node needs to catch up')

bor_status_gauge = prom.Gauge(
    '{}_status'.format('bor'), 'Status of the Service', ['service_name'])
heimdall_status_gauge = prom.Gauge(
    '{}_status'.format('heimdall'), 'Status of the Service', ['service_name'])

netinfo = prom.Gauge(
    'network_name', 'network-name')
netListening_gauge = prom.Gauge(
    'net_listening', 'true if client is actively listening for network connections')


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
            blocks_to_syn_gauge.set(0)
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


def netListening():
    try:
        netstatus = w3.net.listening

        if netstatus == 'true':
            netListening_gauge.set(1)
        else:
            netListening_gauge.set(0)
    except Exception as err:
        print("Error:", err)


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
schedule.every(15).seconds.do(netListening)

if client == 'polygon':
    schedule.every(15).seconds.do(check_service("bor"))
    schedule.every(15).seconds.do(check_service("heimdall"))
if client == 'eth2':
    schedule.every(15).seconds.do(check_service("eth2-geth"))
    schedule.every(15).seconds.do(check_service("eth2-beaconchain"))
    schedule.every(15).seconds.do(check_service("eth2-validator"))
else:
    print("Name for Go Client was not provided skipping service status check")

if __name__ == '__main__':
    start_http_server(3000)
    print("Metrics Server Has started on http://localhost:3000 ")
    while True:
        schedule.run_pending()
        time.sleep(1)
