import toml
from web3 import Web3, HTTPProvider
import prometheus_client as prom
from prometheus_client import start_http_server
import subprocess
import time
import schedule
import os
import logging

config = toml.load('config.toml')

# Assign the variables
env = config['default'].get('env')
client = config['default'].get('client')
rpcaddress = config['default'].get('rpcaddress')
log = logging.getLogger('pickleLogger')

if env == "prod":
    from systemd.journal import JournalHandler
    log.addHandler(JournalHandler())
else:
    stream_handler = logging.StreamHandler()
    log.addHandler(stream_handler)

log.setLevel(logging.INFO)
log.info(os.uname()[1])

# Conditionals for env and RPC addresses
if rpcaddress:
    w3 = Web3(HTTPProvider(rpcaddress))
    log.info("RPC is pointed to custom addres")
else:
    w3 = Web3(HTTPProvider('http://localhost:8545'))
    log.info("Custom RPC not provided, Using default RPC Address")


# Drop unncesseary python process monitoring
prom.REGISTRY.unregister(prom.PROCESS_COLLECTOR)
prom.REGISTRY.unregister(prom.PLATFORM_COLLECTOR)
prom.REGISTRY.unregister(prom.GC_COLLECTOR)


# Load the config.toml file


# Setting up specific gauges to GethCalls
peer_gauge = prom.Gauge(
    'peer_count', 'Number of peers in the Ethereum network')
latest_block = prom.Gauge(
    'latest_block', 'latest block number of the blockchain')
node_sync_gauge = prom.Gauge(
    'syncing', 'Node Syncing Status'
)
blocks_to_syn_gauge = prom.Gauge(
    'blocks_to_sync', 'Blocks node needs to catch up')

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
            log.info("Node is synced")
            node_sync_gauge.set(1)
            blocks_to_syn_gauge.set(0)
    except Exception as err:
        log.error(f"An error occurred: {err}")


def current_head():
    try:
        head = w3.eth.block_number
        latest_block.set(int(head))
        log.info(f"Latest block number: {head}")
    except Exception as err:
        log.error(f"Bad Shit went down: {err}")


def peerCount():
    try:
        count = w3.net.peer_count
        peer_gauge.set(count)
        log.info(f"Peers: {count}")
    except Exception as err:
        log.error(f"Bad Shit went down: {err}")


def netVersion():
    try:
        version = w3.net.version
        if version:
            netinfo.set(version)
        else:
            log.info(f"Network version: {version}")
    except Exception as err:
        log.error(f"Bad Shit went down: {err}")


def netListening():
    try:
        netstatus = w3.net.listening
        if netstatus == 'True':
            log.info("Net listening: True")
            netListening_gauge.set(1)
        else:
            netListening_gauge.set(0)
    except Exception as err:
        log.error(f"Error: {err}")


gauges = {}


def check_service(service):
    service_name = service.replace('-', '_')
    if service not in gauges:
        gauges[service] = prom.Gauge(
            f'{service_name}', f'{service_name} status', ['service_name'])

    try:
        output = subprocess.check_output(
            ["systemctl", "is-active", service],
            universal_newlines=True
        )
        if output.strip() == "active":
            gauges[service].labels(service_name=service_name).set(1)
        else:
            gauges[service].labels(service_name=service_name).set(0)
    except subprocess.CalledProcessError:
        gauges[service].labels(service_name=service_name).set(0)


functions_to_schedule = [peerCount, check_syncing,
                         current_head, netVersion, netListening]
for function in functions_to_schedule:
    schedule.every(15).seconds.do(function)


if client == 'polygon':
    servicenames = ['bor', 'heimdalld']
    for servicename in servicenames:
        schedule.every(15).seconds.do(
            lambda servicename=servicename: check_service(servicename))
if client == 'eth2':
    servicenames = ['eth2-geth', 'eth2-beaconchain',
                    'eth2-validator']
    for servicename in servicenames:
        schedule.every(15).seconds.do(
            lambda servicename=servicename: check_service(servicename))
else:
    log.info("Name for Go Client was not provided skipping service status check")

if __name__ == '__main__':
    start_http_server(3000)
    log.info("Metrics Server Has started on http://localhost:3000 ")
    while True:
        schedule.run_pending()
        time.sleep(1)
