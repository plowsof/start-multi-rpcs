# start-multi-rpcs
example of 'launching rpc with a remote node + making a transfer'

```
b'This is the RPC monero wallet. It needs to connect to a monero\n'
b'daemon to work correctly.\n'
b'\n'
b"Monero 'Oxygen Orion' (v0.17.3.2-release)\n"
b'Logging to ./monero-wallet-rpc.log\n'
b'2022-05-09 03:15:00.373\tW Loading wallet...\n'
b'2022-05-09 03:15:03.858\tW Loaded wallet keys file, with public address: 53koLV3YHdrHLvJGD4SCMvEMWVxpx9nj3XtcgUQZgQ7D7pHkB2QypQGgijTWwLef8KeUSWHrsi2MhedGTzLgppYCBhedymL\n'
b'2022-05-09 03:15:04.934\tW Transaction extra has unsupported format: <68cba63815b2e5cab45aa1d8a389d23cb530a6ed04cf4e24b1f80cdc6577b4d0>\n'
b'2022-05-09 03:15:04.934\tW Transaction extra has unsupported format: <a7979526a20416682bd874560058a0a004a47a04134a9ddcc3fafe358491d8e2>\n'
b'2022-05-09 03:15:04.946\tW Transaction extra has unsupported format: <bc79357c986acf7bdf3e7f94d14637ddba3b5474fa59c16e16082bc2be49453d>\n'
b'2022-05-09 03:15:05.125\tW Background mining not enabled. Run "set setup-background-mining 1" in monero-wallet-cli to change.\n'
b'2022-05-09 03:15:05.126\tI Binding on 127.0.0.1 (IPv4):12347\n'
b'2022-05-09 03:15:06.752\tW Starting wallet RPC server\n'
{'amount': 1,
 'fee': 43990000,
 'multisig_txset': '',
 'spent_key_images': {'key_images': ['29f3a84e88e11cc7eb1504297ceac82922c163bdd671384fe3fb09c9ae708e05']},
 'tx_blob': '',
 'tx_hash': 'd0fa5f6cd7a59cb272160d379035a31a27fd0e8a04a2268c292bea982a7b6a37',
 'tx_key': '',
 'tx_metadata': '',
 'unsigned_txset': '',
 'weight': 1449}
[Finished in 8.7s]
```
