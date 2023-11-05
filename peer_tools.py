import json
import os
import sys
from symbolpeer.SymbolPeerClient import SymbolPeerClient
from symbolpeer.ChainInfoCreator import ChainInfoCreator
from symbolpeer.NodeInfoCreator import NodeInfoCreator
from symbolpeer.NodePeersCreator import NodePeersCreator
from symbolpeer.NodeUnlockedAccountsCreator import NodeUnlockedAccountCreator


CERTIFICATE_DIRECTORY = os.path.dirname(__file__) + "/cert"


def default_method(item):
    if isinstance(item, object) and hasattr(item, "__dict__"):
        return item.__dict__
    else:
        raise TypeError


def main(argv):
    command = ""
    hostname = "127.0.0.1"
    port = 7900
    if 2 > len(argv):
        print()
        print(os.path.basename(__file__) + " COMMAND [HOSTNAME] [PORT]")
        print()
        print("COMMANDS")
        print("  chainInfo\t\t\t/chain/info")
        print("  nodeInfo\t\t\t/node/info")
        print("  nodePeers\t\t\t/node/peers")
        print("  nodeUnlockedaccount\t\t/node/unlockedaccount")
        print("HOSTNAME")
        print("  default: 127.0.0.1")
        print("PORT")
        print("  default: 7900")
        print()
        return 0
    if 3 <= len(argv):
        hostname = argv[2]
    if 4 <= len(argv):
        if not argv[3].isdigit():
            print("argument is not digit")
            return 1
        port = argv[3]

    command = argv[1]

    peer_client = SymbolPeerClient(hostname, port, CERTIFICATE_DIRECTORY)
    ssocket = peer_client.connection()
    if command == "chainInfo" or command == "ci":
        node_peers_creator = ChainInfoCreator()
        node_peers = node_peers_creator.create(ssocket)
        print(json.dumps(node_peers, default=default_method, indent=2))
    elif command == "nodeInfo" or command == "ni":
        node_peers_creator = NodeInfoCreator()
        node_peers = node_peers_creator.create(ssocket)
        print(json.dumps(node_peers, default=default_method, indent=2))
    elif command == "nodePeers" or command == "np":
        node_peers_creator = NodePeersCreator()
        node_peers = node_peers_creator.create(ssocket)
        print(json.dumps(node_peers, default=default_method, indent=2))
    elif command == "nodeUnlockedaccount" or command == "nu":
        node_unlocked_account_creator = NodeUnlockedAccountCreator()
        node_unlocked_account = node_unlocked_account_creator.create(ssocket)
        print(json.dumps(node_unlocked_account, default=default_method, indent=2))
    else:
        print("unknown command")
        ssocket.close()
        return 1

    ssocket.close()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as ex:
        print(ex)
