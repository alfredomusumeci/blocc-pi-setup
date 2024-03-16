# crypto_config_generator.py
import os
import sys
import argparse

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

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate crypto-config.yaml for Hyperledger Fabric.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true', help='Generate configuration for all organizations (1 to 11).')
    group.add_argument('--specify', type=lambda s: [int(item) for item in s.split(',')], help='Specify the organizations to include, e.g., --specify=3,6,10')
    group.add_argument('num', nargs='?', type=int, help='Number of organizations. This argument is optional and used if --all or --specify are not provided.')
    return parser.parse_args()

def generate_orderer_orgs_yaml(orgs):
    orderer_orgs_yaml = "OrdererOrgs:\n"
    for i in orgs:
        orderer_orgs_yaml += OrdererOrgTemplate.format(i=i, endpoint=200+i)
    return orderer_orgs_yaml

def generate_peer_orgs_yaml(orgs):
    peer_orgs_yaml = "PeerOrgs:\n"
    for i in orgs:
        peer_orgs_yaml += PeerOrgTemplate.format(i=i, endpoint=200+i)
    return peer_orgs_yaml

def generate_crypto_config_yaml(orgs):
    orderer_orgs_yaml = generate_orderer_orgs_yaml(orgs)
    peer_orgs_yaml = generate_peer_orgs_yaml(orgs)
    return orderer_orgs_yaml + peer_orgs_yaml

def write_crypto_config_to_file(yaml_content, file_path='./fabric/config/generated/configtx.yaml'):
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, 'w') as file:
        file.write(yaml_content)
    print(f"Crypto configuration file {file_path} has been generated.")

def main():
    args = parse_arguments()
    orgs = []

    if args.all:
        orgs = list(range(1, 12))  # Assumes organizations 1 to 11 exist
    elif args.specify:
        orgs = args.specify  # Organizations specified by the user
    else:
        orgs = list(range(1, args.num + 1)) if args.num else [1]  # Default to 1 organization if no argument is given

    crypto_config_yaml = generate_crypto_config_yaml(orgs)
    write_crypto_config_to_file(crypto_config_yaml)

if __name__ == "__main__":
    main()
