from web3 import Web3, HTTPProvider
import prometheus_client as prom
from prometheus_client import start_http_server
import time
import schedule


w3 = Web3(HTTPProvider("http://44.227.34.159:8008/rpc"))

peer_gauge = prom.Gauge(
    'peer_count', 'Number of peers in the Ethereum network')
current_head = prom.Gauge(
    'current_head', 'latest block number of the blockchain')


def check_syncing():
    try:
        syncing = w3.eth.syncing
        if syncing:
            print("block-diff:",
                  syncing['highestBlock'] - syncing['currentBlock'])
        else:
            print("Node is synced")
    except Exception as err:
        print("An error occurred:", err)


def current_head():
    try:
        head = w3.eth.block_number
        print("Current block number:", head)
    except Exception as err:
        print("Bad Shit went down:", err)


def peerCount():
    try:
        count = w3.net.peer_count
        # set the gauge to the current peer count
        peer_gauge.set(count)
        print("Peers:", count)
    except Exception as err:
        print("Bad Shit went down:", err)


def netVersion():
    try:
        version = w3.net.version
        if version == "137":
            print("Polygon-Mainnet")
        else:
            print(version)
    except Exception as err:
        print("Bad Shit went down:", err)


schedule.every(15).seconds.do(peerCount)


# if __name__ == '__main__':
#     start_http_server(3000)
#     print("Metrics Server Has started on http://localhost:3000 ")
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

check_syncing()
