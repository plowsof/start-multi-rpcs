from monerorpc.authproxy import AuthServiceProxy, JSONRPCException
import pprint
import subprocess
import time
import requests
import threading

# create multiple wallets using monero rpc
# save blockheight as restore height so they can be used 
# I do not need to do this - i can just copy and paste the same wallet also (if spending is not required)
def init_monero_rpc(rpc_port,num_wallets,height):
    rpc_url = f"http://localhost:{rpc_port}/json_rpc"
    rpc_args = [ 
        f"./monero-wallet-rpc", 
        "--wallet-dir", "./wallets",
        "--rpc-bind-port", rpc_port,
        "--disable-rpc-login",
        "--offline"
        #"--daemon-address", remote_node
    ]
    monero_daemon = subprocess.Popen(rpc_args,stdout=subprocess.PIPE)
    rpc_connection = AuthServiceProxy(service_url=rpc_url)

    if rpc_wallet_online(rpc_connection):
        for num in range(num_wallets):
            print("lets create some wallets")
            params={
            "filename": f"wallet_{num}",
            "language": "English"
            }
            print("Creating wallet..")
            rpc_connection.create_wallet(params)
            rpc_connection.open_wallet({"filename": f"wallet_{num}", "password" :""})
            mnemonic = rpc_connection.query_key({"key_type": "mnemonic"})["key"]
            main_address = rpc_connection.get_address()["address"]
            print(f"wallet {num}:\n{main_address}")
            #save the wallet with a correct restore height
            rpc_connection.refresh({"start_height": (height - 1)})
            rpc_connection.store()
    else:
        print("we couldnt start it")

    return monero_daemon

# wait until rpc is reachable
def rpc_wallet_online(rpc_con):
    num_retries = 0
    while True:
        try:
            info = rpc_con.get_version()
            print(f"monero RPC server online.")
            return True
        except Exception as e:
            print(e)
            print("Trying again..")
            if num_retries > 30:
                #the lights are on but nobodys home, exit
                print(f"Unable to communiucate with monero rpc server. Exiting")
                return False
            time.sleep(1)
            num_retries += 1

# todo: handle if remote node is offline / return so the wallet can be used on another node
def open_wallet_transfer(rpc_port,wallet_num,remote_node,wallet):
    print(remote_node)
    rpc_url = f"http://localhost:{rpc_port}/json_rpc"
    rpc_args = [ 
        f"./monero-wallet-rpc", 
        "--wallet-file", f"./wallets/{wallet}",
        "--rpc-bind-port", rpc_port,
        "--disable-rpc-login",
        "--daemon-address", remote_node,
        "--password", "", "--stagenet"
    ]
    monero_daemon = subprocess.Popen(rpc_args,stdout=subprocess.PIPE)
    for line in iter(monero_daemon.stdout.readline,''):
        #print(line)
        if b"Starting wallet RPC server" in line.rstrip():
            break
        if b"Resource temporarily unavailable" in line.rstrip():
            print("Please stop this docker container using 'docker stop <name>")
        if b"Error" in line.rstrip() or b"Failed" in line.rstrip():
            print(line.rstrip())
            break
        if b"failed: no connection to daemon" in line.rstrip():
            print("daemon offline")
            monero_daemon.terminate()
            break
    rpc_connection = AuthServiceProxy(service_url=f"http://127.0.0.1:{rpc_port}/json_rpc")
    params = {
        "destinations":[
            {
                "amount":1,
                "address":"54hzhv2oXnHKHmbDhjuhN8Dz4XjUaxCuBBCWRRL5DPoWW7gDkGvetwB1bAkM4jBxnhLAawfL9sC4dibZGBhCtAMASxCuRvn"
                }],
        "account_index":0,
        "subaddr_indices":[0],
        "priority":0,
        "ring_size":11,
        "do_not_relay": True
        }

    info = rpc_connection.transfer(params)
    pprint.pprint(info)
    print(f"Node: {remote_node}\nFee:{info['fee']}")
    monero_daemon.terminate()

'''
height = requests.get("http://busyboredom.com:18081/get_info").json()["height"]
d = init_monero_rpc("12311",10,height)
d.terminate()
'''

def threaded_test(port,nodes,wallet):
    open_wallet_transfer(port,"test",node,wallet)

nodes_thread1 = [
    "stagenet.melo.tools:38081",
    "stagenet.xmr-tw.org:38081",
    "stagenet.community.rino.io:38081",
    "xmr-lux.boldsuck.org:38081",
    "node.sethforprivacy.com:38089",
    "node2.sethforprivacy.com:38089"
]

num = 1
for node in nodes_thread1:
    th = threading.Thread(target=threaded_test, args=(f"123{num}",node,f"stage{num}"))
    th.start()
    num += 1
