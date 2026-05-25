import yaml

NUM_AGENTS = 64
PORT = 5000
NETWORKS = ["peernet"]

if __name__ == "__main__":
    config = {
        "services": {
            f"node{i}" : {
                "build" : ".",
                "environment" : {
                    "NODE_ID" : f"node{i}",
                    "NEIGHBORS" : ",".join([f"node{j}" for j in range(1, NUM_AGENTS + 1) if j != i])
                },
                "ports" : [f"{PORT + i}:{PORT}"],
                "networks" : [n for n in NETWORKS]
            } for i in range(1, NUM_AGENTS + 1)
        },
        "networks":{
            n:{
                "driver" : "bridge"
            } for n in NETWORKS
        }
    }
    
    with open("compose.yaml", "w") as f:
        yaml.dump(config, f)