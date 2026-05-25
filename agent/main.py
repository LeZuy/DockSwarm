import os
from typing import Any

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

NODE_ID = os.getenv("NODE_ID", "unknown-node")
PEERS = [
    peer.strip()
    for peer in os.getenv("PEERS", "").split(",")
    if peer.strip()
]

store: dict[str, Any] = {}

@app.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "node": NODE_ID,
            "peers": PEERS,
        }
    )

@app.get("/state")
def state():
    return jsonify(
        {
            "node": NODE_ID,
            "data": store,
        }
    )

@app.get("/kv/<key>")
def get_value(key: str):
    if key not in store:
        return jsonify({"error": "key not found", "node": NODE_ID}), 404

    return jsonify(
        {
            "node": NODE_ID,
            "key": key,
            "value": store[key],
        }
    )

@app.put("/kv/<key>")
def put_value(key: str):
    body = request.get_json(silent=True) or {}

    if "value" not in body:
        return jsonify({"error": "request body must contain 'value'"}), 400

    value = body["value"]
    store[key] = value

    replication_results = []

    for peer in PEERS:
        try:
            response = requests.put(
                f"http://{peer}/internal/replicate/{key}",
                json={"value": value, "source": NODE_ID},
                timeout=1.0,
            )

            replication_results.append(
                {
                    "peer": peer,
                    "status": "success",
                    "http_status": response.status_code,
                }
            )
        except requests.RequestException as exc:
            replication_results.append(
                {
                    "peer": peer,
                    "status": "failed",
                    "error": str(exc),
                }
            )

    return jsonify(
        {
            "node": NODE_ID,
            "key": key,
            "value": value,
            "replication": replication_results,
        }
    )

@app.put("/internal/replicate/<key>")
def replicate_value(key: str):
    body = request.get_json(silent=True) or {}

    if "value" not in body:
        return jsonify({"error": "request body must contain 'value'"}), 400

    store[key] = body["value"]

    return jsonify(
        {
            "node": NODE_ID,
            "replicated_key": key,
            "source": body.get("source"),
        }
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)