import yaml

NET_CONGIG_PATH = "./config/network.yaml"

if __name__ == "__main__":
    with open (NET_CONGIG_PATH, "r") as f:
        net_config = yaml.safe_load(f)

    config = {
        "services": {
            f"node{i}" : {
                "build" : ".",
                "environment" : {
                    "NODE_ID" : f"node{i}",
                    "NEIGHBORS" : ",".join([f"node{j}" for j in range(1, net_config["NUM_AGENTS"] + 1) if j != i])
                },
                "ports" : [f"{net_config["PORT"] + i}:{net_config["PORT"]}"],
                "networks" : [n for n in net_config["NETWORKS"]]
            } for i in range(1, net_config["NUM_AGENTS"] + 1)
        },
        "networks":{
            n:{
                "driver" : "bridge"
            } for n in net_config["NETWORKS"]
        }
    }
    
    with open("compose.yaml", "w") as f:
        yaml.dump(config, f)