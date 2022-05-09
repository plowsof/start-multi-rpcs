from monerorpc.authproxy import AuthServiceProxy, JSONRPCException
import pprint
import subprocess
import time
import requests
import threading
import math
import shutil

def init_monero_rpc(rpc_port,num_wallets,height):
    rpc_url = f"http://localhost:{rpc_port}/json_rpc"
    rpc_args = [ 
        f"./monero-wallet-rpc", 
        "--wallet-dir", "./wallets",
        "--rpc-bind-port", rpc_port,
        "--disable-rpc-login",
        "--offline", "--stagenet"
        #"--daemon-address", remote_node
    ]
    monero_daemon = subprocess.Popen(rpc_args,stdout=subprocess.PIPE)
    rpc_connection = AuthServiceProxy(service_url=rpc_url)

    if rpc_wallet_online(rpc_connection):
        for num in range(num_wallets):
            print("lets create some wallets")
            params={
            "filename": f"stage{num}",
            "language": "English"
            }
            print("Creating wallet..")
            rpc_connection.create_wallet(params)
            rpc_connection.open_wallet({"filename": f"stage{num}", "password" :""})
            mnemonic = rpc_connection.query_key({"key_type": "mnemonic"})["key"]
            main_address = rpc_connection.get_address()["address"]
            print(f"wallet {num}:\n{main_address}")
            #save the wallet with a correct restore height
            rpc_connection.refresh({"start_height": (height - 1)})
            rpc_connection.close_wallet()
    else:
        print("we couldnt start it")

    return monero_daemon

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

# torsocks --port 9150 /Applications/monero-wallet-gui.app/Contents/MacOS/monero-wallet-gui
def open_wallet_transfer(rpc_port,remote_node,wallet):
    remote_node = "xmr-lux.boldsuck.org:38081"
    rpc_url = f"http://localhost:{rpc_port}/json_rpc"
    rpc_args = [ 
        f"./monero-wallet-rpc", 
        "--wallet-file", f"./wallets/stage{str(wallet)}",
        "--rpc-bind-port", str(rpc_port),
        "--disable-rpc-login",
        "--daemon-address", remote_node,
        "--password", "", "--stagenet"
    ]
    monero_daemon = subprocess.Popen(rpc_args,stdout=subprocess.PIPE)
    for line in iter(monero_daemon.stdout.readline,''):
        #print(line)
        if b"Starting wallet RPC server" in line.rstrip():
            break
        # wallet file open by another rpc
        # failure to bind on port also an issue
        if b"Resource temporarily unavailable" in line.rstrip():
            print("Please stop this docker container using 'docker stop <name>")
        if b"Error" in line.rstrip().lower() or b"Failed" in line.rstrip() or b"EXCEPTION" in line.rstrip():
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
    print(f"Node: {remote_node}\nFee:{info['fee']}")
    rpc_connection.close_wallet()
    monero_daemon.terminate()

def threaded_test(port,nodes,wallet):
    for node in nodes:
        node = f'{node["hostname"]}:{node["port"]}'
        if "onion" not in node:
            print(f"{port} {node} {wallet}")
            open_wallet_transfer(port,node,str(wallet))

def main():
    stagenet = requests.get("https://www.ditatompel.com/api/monero/remote-node?nettype=stagenet").json()["data"]

    extra_data =  {'adjusted_time': 1652096821,
      'asn': 53667,
      'asn_name': 'PONYNET',
      'city': 'Roost',
      'country': 'LU',
      'database_size': 10737418240,
      'difficulty': 323248,
      'hostname': 'xmr-lux.boldsuck.org',
      'ip_address': '104.244.75.217',
      'is_tor': False,
      'last_checked': 1652096854,
      'last_height': 1088846,
      'nettype': 'stagenet',
      'port': 38081,
      'postal': 0,
      'protocol': 'http',
      'status': 'online',
      'uptime': 99.49
      }


    for i in range(30):
        stagenet.append(extra_data)
    num_wallets = 10
    per_thread = len(stagenet) / num_wallets

    counter = 1
    total = len(stagenet)

    if per_thread < 1:
        per_thread = total

    per_thread = math.floor(per_thread)

    the_list = {}
    for i in range(num_wallets):
        the_list[i] = []
        the_list[i]

    port = 14444
    wallet_port = {}
    for i in range(num_wallets):
        wallet_port[i] = port
        port+=1 

    i = 0
    wallet_counter = 0
    for i in range(len(stagenet)):
        the_list[wallet_counter].append(stagenet[i])
        if wallet_counter == 9:
            wallet_counter = 0
        else:
            wallet_counter += 1

    for l in the_list:
        t = threading.Thread(target=threaded_test, args=(wallet_port[l],the_list[l],l,))
        t.start()

if __name__ == "__main__":
    #height = requests.get("http://busyboredom.com:18081/get_info").json()["height"]
    '''
    height = requests.get("http://xmr-lux.boldsuck.org:38081/get_info").json()["height"]
    d = init_monero_rpc("12311",10,height)
    d.terminate()
    '''
    # i cant make a wallet for some reason. copy an existing one instead
    for i in range(10):
        shutil.copy("./wallets/stage", f"./wallets/stage{i}")
        shutil.copy("./wallets/stage.keys", f"./wallets/stage{i}.keys")
    main()
