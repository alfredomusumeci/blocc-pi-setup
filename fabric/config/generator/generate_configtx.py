# configtx_generator.py
import os
import sys
from config_tx_templates import (
    ContainerOrdererTemplate,
    ContainerOrgTemplate,
    generate_capabilities_application_template_dynamic,
    OrdererTemplate,
    ChannelTemplate,
    ProfileTemplate
)

def generate_yaml_section(num_containers, template):
    yaml_section = ""
    for i in range(1, num_containers + 1):
        yaml_section += template.format(i=i, endpoint=200+i)
    return yaml_section

def generate_orderers_yaml(num_orderers):
    orderers_yaml = ""
    for i in range(1, num_orderers + 1):
        orderers_yaml += OrdererTemplate.format(i=i, endpoint=200+i)
    return orderers_yaml

def generate_channels_yaml(num_channels):
    channels_yaml = ""
    for i in range(1, num_channels + 1):
        channels_yaml += ChannelTemplate.format(i=i)
    return channels_yaml

def generate_profiles_yaml(num_profiles):
    profiles_yaml = "Profiles:\n"
    for i in range(1, num_profiles + 1):
        profiles_yaml += ProfileTemplate.format(i=i)
    return profiles_yaml

def generate_config_yaml(num_containers, num_channels):
    orderer_orgs_yaml = "Organizations:\n" + generate_yaml_section(num_containers, ContainerOrdererTemplate)
    peer_orgs_yaml = generate_yaml_section(num_containers, ContainerOrgTemplate)
    # Adjusted to dynamically generate based on num_containers
    capabilities_application_yaml = generate_capabilities_application_template_dynamic(num_containers)
    orderers_yaml = generate_orderers_yaml(num_containers)
    channels_yaml = generate_channels_yaml(num_channels)
    profiles_yaml = generate_profiles_yaml(num_channels)
    return orderer_orgs_yaml + peer_orgs_yaml + capabilities_application_yaml + orderers_yaml + channels_yaml + profiles_yaml

def write_config_to_file(yaml_content, file_path='../generated/configtx.yaml'):
    directory = os.path.dirname(file_path)
    
    # Create the directory if it does not exist
    os.makedirs(directory, exist_ok=True)
    
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, 'w') as file:
        file.write(yaml_content)
    print(f"Configuration file {file_path} has been generated.")

def main():
    num_containers = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    num_channels = num_containers  # As stated, there are as many channels as containers
    config_yaml = generate_config_yaml(num_containers, num_channels)
    write_config_to_file(config_yaml)

if __name__ == "__main__":
    main()
