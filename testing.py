from monerorpc.authproxy import AuthServiceProxy, JSONRPCException
import pprint
import subprocess
import time
import requests
import threading
import math
import shutil
from bs4 import BeautifulSoup
import random
import sqlite3

# global block list https://gui.xmr.pm/files/block.txt
get_info_template = ['adjusted_time', 'alt_blocks_count', 'block_size_limit', 'block_size_median', 'block_weight_limit', 'block_weight_median', 'bootstrap_daemon_address', 'busy_syncing', 'credits', 'cumulative_difficulty', 'cumulative_difficulty_top64', 'database_size', 'difficulty', 'difficulty_top64', 'free_space', 'grey_peerlist_size', 'height', 'height_without_bootstrap', 'incoming_connections_count', 'mainnet', 'nettype', 'offline', 'outgoing_connections_count', 'rpc_connections_count', 'stagenet', 'start_time', 'status', 'synchronized', 'target', 'target_height', 'testnet', 'top_block_hash', 'top_hash', 'tx_count', 'tx_pool_size', 'untrusted', 'update_available', 'version', 'was_bootstrap_ever_used', 'white_peerlist_size', 'wide_cumulative_difficulty', 'wide_difficulty']


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

def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5h://127.0.0.1:9050',
                       'https': 'socks5h://127.0.0.1:9050'}
    return session

# torsocks --port 9150 /Applications/monero-wallet-gui.app/Contents/MacOS/monero-wallet-gui
def open_wallet_transfer(rpc_port,remote_node,wallet):
    global get_info_template
    #remote_node = "xmr-lux.boldsuck.org:38081"

    rpc_url = f"http://localhost:{rpc_port}/json_rpc"
    # check if we're online + synched
    get_info = f'{remote_node.split("/json_rpc")[0]}/get_info'
    try:
        if ".onion" in get_info:
            ses = get_tor_session()
            r = ses.get(get_info,timeout=60)
        else:
            r = requests.get(get_info,timeout=60)
        lol = list(r.json().keys())
        if lol == get_info_template:
            print(f"{get_info} nice")
        else:
            print(f"{get_info} naughty")
            con = sqlite3.connect('santas_xmr_list.db')
            cur = con.cursor()
            sql = '''INSERT OR IGNORE INTO naughty(ip) VALUES(?)'''
            cur.execute(sql, (remote_node,))
            con.commit()
            con.close()
            if r.json()["status"] == "Client signature does not verify for get_info":
                return
            if r.json().get("restricted") == True:
                print("restwicted")
        if r.json()["synchronized"] != True:
            # not synced
            return
    except Exception as e:
        print(e)
        # its offline / slow
        return

    rpc_args = [ 
        f"./monero-wallet-rpc", 
        "--wallet-file", f"./wallets/stage{str(wallet)}",
        "--rpc-bind-port", str(rpc_port),
        "--disable-rpc-login",
        "--daemon-address", remote_node,
        "--password", ""#, "--stagenet"
    ]
    if "onion" in remote_node:
        rpc_args.append("--proxy")
        rpc_args.append("127.0.0.1:9050")
    monero_daemon = subprocess.Popen(rpc_args,stdout=subprocess.PIPE)
    for line in iter(monero_daemon.stdout.readline,''):
        #print(line)
        if b"Starting wallet RPC server" in line.rstrip():
            break
        # wallet file open by another rpc
        # failure to bind on port also an issue
        if b"Resource temporarily unavailable" in line.rstrip():
            print(line)
            print("Please stop this docker container using 'docker stop <name>")
            print(f"{remote_node} offline")
            monero_daemon.terminate()
            monero_daemon.wait()
            return
        if b"Error" in line.rstrip().lower() or b"Failed" in line.rstrip() or b"EXCEPTION" in line.rstrip():
            print(line)
            print(f"{remote_node} offline")
            monero_daemon.terminate()
            monero_daemon.wait()
            return
        if b"failed: no connection to daemon" in line.rstrip():
            print("daemon offline")
            print(f"{remote_node} offline")
            monero_daemon.terminate()
            monero_daemon.wait()
            return
    rpc_connection = AuthServiceProxy(service_url=f"http://127.0.0.1:{rpc_port}/json_rpc")
    params = {
        "destinations":[
            {
                "amount":1,
                "address":"88UbURD1esv6wJNqLEvJFn82JbX6awYW2BW4Sj2E3rahQbxP2C4FgGS6tdLp2wdPHJZ4PjgjuZbfi139oZ3LK9gcMXugv7C"
                }],
        "account_index":0,
        "subaddr_indices":[0],
        "priority":0,
        "ring_size":11,
        "do_not_relay": True
        }
    try:
        r = requests.post(rpc_url, json={"jsonrpc":"2.0","id":"0","method":"transfer","params":params},timeout=120)
        
        fee = r.json()["result"]["fee"]
        print(fee)
        con = sqlite3.connect('santas_xmr_list.db')
        cur = con.cursor()
        sql = '''INSERT OR IGNORE INTO fees(ip,fee) VALUES(?,?)'''
        cur.execute(sql, (remote_node,fee))
        con.commit()
        con.close()
        if fee > 8230000:
            print(f"Node: {remote_node}")
            print(r.json()["result"]["fee"])
        rpc_connection.close_wallet()
        monero_daemon.terminate()
        monero_daemon.wait()
    except Exception as e:
        print(e)
        monero_daemon.terminate()
        monero_daemon.wait()

def threaded_test(port,nodes,wallet):
    for node in nodes:
        #node = f'{node["hostname"]}:{node["port"]}'node1.xmr-tw.org:18081
        #print(f"{port} {node} {wallet}")
        open_wallet_transfer(port,node,str(wallet))

def main():
    '''
    response = requests.get("https://monero.fail/?nettype=mainnet")
    webpage = response.content
    stagenet = []
    soup = BeautifulSoup(webpage, "html.parser")
    for tr in soup.find_all('tr'):
        values = [data for data in tr.find_all('td')]
        for value in values:
            if "http" in value.text:
                stagenet.append(value.text)
    '''
    # get peer list ips
    con = sqlite3.connect('santas_xmr_list.db')
    cur = con.cursor()
    create_naughty_table = """ CREATE TABLE IF NOT EXISTS naughty (
                                ip text PRIMARY KEY
                            ); """
    create_fee_table = """ CREATE TABLE IF NOT EXISTS fees (
                            ip text,
                            fee integer
                        ); """
    cur.execute(create_fee_table)
    cur.execute(create_naughty_table)
    con.commit()
    con.close()
    
    r = requests.get("http://192.168.1.68:18081/get_peer_list").json()

    node_list = []
    for x in r["white_list"]:
        if x.get("rpc_port"):
            if "::ffff:" in x["host"]:
                x['host'] = x['host'].split("::ffff:")[1]   
            host = f"http://{x['host']}:{x['rpc_port']}/json_rpc"
            node_list.append(host)

    stagenet = node_list
    num_wallets = 3
    random.shuffle(stagenet)
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
        if wallet_counter == (num_wallets - 1):
            wallet_counter = 0
        else:
            wallet_counter += 1
    pprint.pprint(the_list)
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
    #for i in range(10):
    #    shutil.copy("./wallets/kikstarter-test", f"./wallets/stage{i}")
    #    shutil.copy("./wallets/kikstarter-test.keys", f"./wallets/stage{i}.keys")
    main()
