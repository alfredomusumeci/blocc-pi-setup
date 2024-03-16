# configtx_generator.py
import os
import sys
import argparse
from config_tx_templates import (
    ContainerOrdererTemplate,
    ContainerOrgTemplate,
    generate_capabilities_application_template_dynamic,
    OrdererTemplate,
    ChannelTemplate,
    ProfileTemplate
)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate configtx.yaml for Hyperledger Fabric.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true', help='Generate configuration for all organizations (1 to 11).')
    group.add_argument('--specify', type=lambda s: [int(item) for item in s.split(',')], help='Specify the organizations to include, e.g., --specify=3,6,10')
    group.add_argument('num', nargs='?', type=int, help='Number of organizations to generate configuration for. This argument is optional and used if --all or --specify are not provided.')
    return parser.parse_args()

def generate_yaml_section(orgs, template):
    yaml_section = ""
    for i in orgs:
        yaml_section += template.format(i=i, endpoint=200+i)
    return yaml_section

def generate_orderers_yaml(orgs):
    return generate_yaml_section(orgs, OrdererTemplate)

def generate_channels_yaml(orgs):
    channels_yaml = ""
    for i in orgs:
        channels_yaml += ChannelTemplate.format(i=i)
    return channels_yaml

def generate_profiles_yaml(orgs):
    profiles_yaml = "Profiles:\n"
    for i in orgs:
        profiles_yaml += ProfileTemplate.format(i=i)
    return profiles_yaml

def generate_config_yaml(orgs):
    num_channels = len(orgs)  # Adjusted to reflect the actual number of specified organizations
    orderer_orgs_yaml = "Organizations:\n" + generate_yaml_section(orgs, ContainerOrdererTemplate)
    peer_orgs_yaml = generate_yaml_section(orgs, ContainerOrgTemplate)
    capabilities_application_yaml = generate_capabilities_application_template_dynamic(orgs)
    orderers_yaml = generate_orderers_yaml(orgs)
    channels_yaml = generate_channels_yaml(orgs)
    profiles_yaml = generate_profiles_yaml(orgs)
    return orderer_orgs_yaml + peer_orgs_yaml + capabilities_application_yaml + orderers_yaml + channels_yaml + profiles_yaml

def write_config_to_file(yaml_content, file_path='./fabric/config/generated/configtx.yaml'):
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, 'w') as file:
        file.write(yaml_content)
    print(f"Configuration file {file_path} has been generated.")

def main():
    args = parse_arguments()
    orgs = []

    if args.all:
        orgs = list(range(1, 12))  # Assumes organizations 1 to 11 exist
    elif args.specify:
        orgs = args.specify  # Organizations specified by the user
    else:
        orgs = list(range(1, args.num + 1)) if args.num else [1]  # Default to 1 organization if no argument is given

    config_yaml = generate_config_yaml(orgs)
    write_config_to_file(config_yaml)

if __name__ == "__main__":
    main()
