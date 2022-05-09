# start-multi-rpcs
example of 'launching rpc with a remote node + making a transfer'

Testing on a list of 6 nodes    
with threading: [Finished in 23.8s] (1 rpc wallet for 1 node)    
without threading finsished in 60~ seconds

example output (when i didn't use threading / slow)
```
{'amount': 1,
 'fee': 43990000,
 'multisig_txset': '',
 'spent_key_images': {'key_images': ['29f3a84e88e11cc7eb1504297ceac82922c163bdd671384fe3fb09c9ae708e05']},
 'tx_blob': '',
 'tx_hash': '5e94d77b0b83d9dc14f84a209af9157b2d4a5fd7aac83ace1f515af07cedd851',
 'tx_key': '',
 'tx_metadata': '',
 'unsigned_txset': '',
 'weight': 1449}
Node: stagenet.melo.tools:38081
Fee:43990000
{'amount': 1,
 'fee': 43990000,
 'multisig_txset': '',
 'spent_key_images': {'key_images': ['29f3a84e88e11cc7eb1504297ceac82922c163bdd671384fe3fb09c9ae708e05']},
 'tx_blob': '',
 'tx_hash': 'c240ab6b08d8b8100f988b0eccb3975c6f7412fbd431a1635b6bec2090af837b',
 'tx_key': '',
 'tx_metadata': '',
 'unsigned_txset': '',
 'weight': 1449}
Node: stagenet.xmr-tw.org:38081
Fee:43990000
{'amount': 1,
 'fee': 43990000,
 'multisig_txset': '',
 'spent_key_images': {'key_images': ['29f3a84e88e11cc7eb1504297ceac82922c163bdd671384fe3fb09c9ae708e05']},
 'tx_blob': '',
 'tx_hash': 'ba7b26312449e78f0765d5229c2e012bf19e1886ae86a6b13d1f154bdcc0b5b8',
 'tx_key': '',
 'tx_metadata': '',
 'unsigned_txset': '',
 'weight': 1449}
Node: stagenet.community.rino.io:38081
Fee:43990000
{'amount': 1,
 'fee': 43990000,
 'multisig_txset': '',
 'spent_key_images': {'key_images': ['29f3a84e88e11cc7eb1504297ceac82922c163bdd671384fe3fb09c9ae708e05']},
 'tx_blob': '',
 'tx_hash': 'e9fda8308a051eb9b29a2c0f1405d10d55867ebaec962c669d59d5a5331a66ac',
 'tx_key': '',
 'tx_metadata': '',
 'unsigned_txset': '',
 'weight': 1449}
Node: xmr-lux.boldsuck.org:38081
Fee:43990000
{'amount': 1,
 'fee': 43990000,
 'multisig_txset': '',
 'spent_key_images': {'key_images': ['29f3a84e88e11cc7eb1504297ceac82922c163bdd671384fe3fb09c9ae708e05']},
 'tx_blob': '',
 'tx_hash': '75e71fcf13a8883e23ddeb9a17e24c41ceacd5cd6aa0834701caaf9f03f57f73',
 'tx_key': '',
 'tx_metadata': '',
 'unsigned_txset': '',
 'weight': 1449}
Node: node.sethforprivacy.com:38089
Fee:43990000
{'amount': 1,
 'fee': 43990000,
 'multisig_txset': '',
 'spent_key_images': {'key_images': ['29f3a84e88e11cc7eb1504297ceac82922c163bdd671384fe3fb09c9ae708e05']},
 'tx_blob': '',
 'tx_hash': '7b9a4777ab60eb520499b1ea816b282965ec1f0537f44a0748ff8cda2c697d37',
 'tx_key': '',
 'tx_metadata': '',
 'unsigned_txset': '',
 'weight': 1449}
Node: node2.sethforprivacy.com:38089
Fee:43990000
[Finished in 63.3s]
```
