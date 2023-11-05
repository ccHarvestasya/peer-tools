import json
import os
from flask import Flask, Response, request

from symbolpeer.ChainInfoCreator import ChainInfoCreator
from symbolpeer.NodeInfoCreator import NodeInfoCreator
from symbolpeer.NodePeersCreator import NodePeersCreator
from symbolpeer.NodeUnlockedAccountsCreator import NodeUnlockedAccountCreator
from symbolpeer.SymbolPeerClient import SymbolPeerClient

HOST = "127.0.0.1"
PORT = 7900
CERTIFICATE_DIRECTORY = os.path.dirname(__file__) + "/cert"


app = Flask(__name__)


class ErrorResponse:
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message


def default_method(item):
    if isinstance(item, object) and hasattr(item, "__dict__"):
        return item.__dict__
    else:
        raise TypeError


def response_json(json_data) -> Response:
    response = Response(json_data)
    response.headers["Content-Type"] = "application/json"
    return response


@app.route("/chain/info")
def chain_info():
    peer_client = SymbolPeerClient(HOST, PORT, CERTIFICATE_DIRECTORY)

    try:
        with peer_client.connection() as ssocket:
            node_peers_creator = ChainInfoCreator()
            node_peers = node_peers_creator.create(ssocket)
            return (
                response_json(json.dumps(node_peers, default=default_method, indent=2)),
                200,
            )
    except Exception as ex:
        error_res = ErrorResponse("ResourceNotFound", str(ex))
        return (
            response_json(json.dumps(error_res, default=default_method, indent=2)),
            500,
        )


@app.route("/node/info")
def node_info():
    peer_client = SymbolPeerClient(HOST, PORT, CERTIFICATE_DIRECTORY)

    try:
        with peer_client.connection() as ssocket:
            node_peers_creator = NodeInfoCreator()
            node_peers = node_peers_creator.create(ssocket)
            return (
                response_json(json.dumps(node_peers, default=default_method, indent=2)),
                200,
            )
    except Exception as ex:
        error_res = ErrorResponse("ResourceNotFound", str(ex))
        return (
            response_json(json.dumps(error_res, default=default_method, indent=2)),
            500,
        )


@app.route("/node/peers")
def node_peers():
    peer_client = SymbolPeerClient(HOST, PORT, CERTIFICATE_DIRECTORY)

    try:
        with peer_client.connection() as ssocket:
            node_peers_creator = NodePeersCreator()
            node_peers = node_peers_creator.create(ssocket)
            return (
                response_json(json.dumps(node_peers, default=default_method, indent=2)),
                200,
            )
    except Exception as ex:
        error_res = ErrorResponse("ResourceNotFound", str(ex))
        return (
            response_json(json.dumps(error_res, default=default_method, indent=2)),
            500,
        )


@app.route("/node/unlockedaccount")
def node_unlockedaccount():
    peer_client = SymbolPeerClient(HOST, PORT, CERTIFICATE_DIRECTORY)

    try:
        with peer_client.connection() as ssocket:
            node_unlocked_account_creator = NodeUnlockedAccountCreator()
            node_unlocked_account = node_unlocked_account_creator.create(ssocket)
            return (
                response_json(
                    json.dumps(node_unlocked_account, default=default_method, indent=2)
                ),
                200,
            )
    except Exception as ex:
        error_res = ErrorResponse("ResourceNotFound", str(ex))
        return (
            response_json(json.dumps(error_res, default=default_method, indent=2)),
            500,
        )


@app.errorhandler(404)
def error_404(error):
    error_res = ErrorResponse("ResourceNotFound", request.path + " does not exist")
    return (
        response_json(json.dumps(error_res, default=default_method, indent=2)),
        500,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
