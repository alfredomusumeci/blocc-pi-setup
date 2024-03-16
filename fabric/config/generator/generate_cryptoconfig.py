# crypto_config_generator.py
import os
import sys

OrdererOrgTemplate = """  - Name: ContainerOrderer{i}
    Domain: container{i}.blocc.doc.ic.ac.uk

    Specs:
      - Hostname: orderer
        SANS:
          - blocc-container{i}.local
          - blocc-container{i}-orderer
          - blocc-container{i}
          - localhost
          - 127.0.0.1
          - 192.168.199.{endpoint}

"""

PeerOrgTemplate = """  - Name: Container{i}
    Domain: container{i}.blocc.doc.ic.ac.uk
    EnableNodeOUs: true
    Template:
      Count: 1
      SANS:
        - blocc-container{i}.local
        - blocc-container{i}
        - localhost
        - 127.0.0.1
        - 192.168.199.{endpoint}
    Users:
      Count: 1

"""

def generate_orderer_orgs_yaml(num_orderers):
    orderer_orgs_yaml = "OrdererOrgs:\n"
    for i in range(1, num_orderers + 1):
        orderer_orgs_yaml += OrdererOrgTemplate.format(i=i, endpoint=200+i)
    return orderer_orgs_yaml

def generate_peer_orgs_yaml(num_peers):
    peer_orgs_yaml = "PeerOrgs:\n"
    for i in range(1, num_peers + 1):
        peer_orgs_yaml += PeerOrgTemplate.format(i=i, endpoint=200+i)
    return peer_orgs_yaml

def generate_crypto_config_yaml(num_containers):
    orderer_orgs_yaml = generate_orderer_orgs_yaml(num_containers)
    peer_orgs_yaml = generate_peer_orgs_yaml(num_containers)
    return orderer_orgs_yaml + peer_orgs_yaml

def write_crypto_config_to_file(yaml_content, file_path='../generated/crypto-config.yaml'):
    directory = os.path.dirname(file_path)
    
    # Create the directory if it does not exist
    os.makedirs(directory, exist_ok=True)
    
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, 'w') as file:
        file.write(yaml_content)
    print(f"Crypto configuration file {file_path} has been generated.")

def main():
    num_containers = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    crypto_config_yaml = generate_crypto_config_yaml(num_containers)
    write_crypto_config_to_file(crypto_config_yaml)

if __name__ == "__main__":
    main()
