#!/bin/bash

source utils.sh

function printHelp() {
  echo -e "Usage: $0 ${C_BLUE}--container=<container_number> [--all | --specify=[3,6,10]]${C_RESET}"
  echo
  echo -e "${C_BLUE}  --container=<container_number>${C_RESET}"
  echo -e "                 Set the FABRIC_CONTAINER_NUM environment variable for the container."
  echo -e "${C_BLUE}  --all${C_RESET}"
  echo -e "                 Generate configuration for all organizations (1 to 11)."
  echo -e "${C_BLUE}  --specify=[list_of_orgs]${C_RESET}"
  echo -e "                 Specify the organizations to include, e.g., --specify=3,6,10."
  echo -e "                 Example: $0 --container=1 --all"
}

if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
  printHelp
  exit 0
fi

CONTAINER_FLAG="--container"
SPECIFY_FLAG="--specify="
ALL_FLAG="--all"
NUM_CONTAINERS=11
MODE=""
SPECIFIED_ORGS=""

# Parse arguments
for i in "$@"
do
case $i in
    --container=*)
    CONTAINER_NUMBER="${i#*=}"
    shift
    ;;
    --specify=*)
    MODE="SPECIFY"
    SPECIFIED_ORGS="${i#*=}"
    shift
    ;;
    --all)
    MODE="ALL"
    shift
    ;;
    *)
    # unknown option
    ;;
esac
done

if [ -z "$CONTAINER_NUMBER" ]; then
  echo -e "${C_RED}Missing container number!${C_RESET}"
  printHelp
  exit 1
fi

function setContainerEnvironmentVariable() {
  local container_num="$1"
  if ! grep -q "FABRIC_CONTAINER_NUM" ~/.bashrc; then
    echo "export FABRIC_CONTAINER_NUM=$container_num" >> ~/.bashrc
    echo "FABRIC_CONTAINER_NUM has been set to: $container_num"
  else
    echo "FABRIC_CONTAINER_NUM is already set in ~/.bashrc."
  fi
}

setContainerEnvironmentVariable "$CONTAINER_NUMBER"

function setEndpointEnvironmentVariable() {
  local peer_external_endpoint="$1"
  if ! grep -q "PEER_EXTERNAL_ENDPOINT" ~/.bashrc; then
    echo "export PEER_EXTERNAL_ENDPOINT=$peer_external_endpoint" >> ~/.bashrc
    echo "PEER_EXTERNAL_ENDPOINT has been set to: $peer_external_endpoint"
  else
    echo "PEER_EXTERNAL_ENDPOINT is already set in ~/.bashrc."
  fi
}

# Calculate IP Suffix based on container_number
IP_SUFFIX=$((CONTAINER_NUMBER + 200))
peer_external_endpoint=192.168.199.$IP_SUFFIX:7051

setEndpointEnvironmentVariable "$peer_external_endpoint"

pullBinaries() {
    echo -e "${C_BLUE}Downloading fabric binaries${C_RESET}"
    BINARY_FILE="hyperledger-fabric-linux-arm64-2.5.1.tar.gz"
    URL="https://github.com/ImperialCollegeLondon/blocc-fabric/releases/download/latest/${BINARY_FILE}"
    DEST_DIR=/home/pi/fabric
    echo -e "${C_BLUE}===> Downloading: ${URL}${C_RESET}"
    echo -e "${C_BLUE}===> Unpacking to: ${DEST_DIR}${C_RESET}"
    curl -L --retry 5 --retry-delay 3 "${URL}" | tar xz -C ${DEST_DIR} || rc=$?
    if [ -n "$rc" ]; then
        echo -e "${C_RED}==> There was an error downloading the binary file.${C_RESET}"
        exit 1
    else
        echo -e "${C_GREEN}==> Done.${C_RESET}"
    fi
}

echo -e "${C_BLUE}Installing Docker...${C_RESET}"

install_package docker-compose

echo -e "${C_BLUE}Installing jq...${C_RESET}"

install_package jq

echo -e "${C_BLUE}Running Docker daemon on start...${C_RESET}"
sudo systemctl enable docker
sudo systemctl start docker

echo -e "${C_BLUE}Adding Docker to this user group...${C_RESET}"
sudo usermod -aG docker $USER

FABRIC_DIR="$HOME/fabric"

if [ -d "$FABRIC_DIR" ]; then
  echo -e "${C_YELLOW}BLOCC Fabric is already installed. Skipping installation.${C_RESET}"
else
  echo -e "${C_BLUE}Creating fabric directory...${C_RESET}"
  mkdir -p "$FABRIC_DIR"
  cd "$FABRIC_DIR" || exit

  echo -e "${C_BLUE}Installing BLOCC Fabric binaries...${C_RESET}"
  pullBinaries
  echo -e "${C_GREEN}BLOCC Fabric binaries installed.${C_RESET}"

  echo -e "${C_BLUE}Creating channel-artefacts directory...${C_RESET}"
  mkdir -p channel-artefacts

  # Going back to working directory
  cd "$HOME/blocc-pi-setup" || exit
fi

echo -e "${C_BLUE}Adding Fabric compose file to fabric directory...${C_RESET}"
cp ./fabric/compose/compose.yaml ~/fabric/

echo -e "${C_BLUE}Adding dashboard compose file to fabric directory...${C_RESET}"
cp ./fabric/compose/dashboard.yaml ~/fabric/

echo -e "${C_BLUE}Adding app compose file to fabric directory...${C_RESET}"
cp ./fabric/compose/app.yaml ~/fabric/

echo -e "${C_BLUE}Adding core.yaml to fabric directory...${C_RESET}"
sed -e "s/\${FABRIC_CONTAINER_NUM}/${CONTAINER_NUMBER}/g" \
    -e "s/\${PEER_EXTERNAL_ENDPOINT}/${peer_external_endpoint}/g" \
./fabric/config/static/core.yaml > ~/fabric/config/core.yaml

echo -e "${C_BLUE}Adding orderer.yaml to fabric directory...${C_RESET}"
sed "s/\${FABRIC_CONTAINER_NUM}/${CONTAINER_NUMBER}/g" ./fabric/config/static/orderer.yaml > ~/fabric/config/orderer.yaml

# Add ~/fabric/bin to PATH if not already added
if [[ ":$PATH:" != *":$FABRIC_DIR/bin:"* ]]; then
  echo -e "${C_BLUE}Adding Hyperledger Fabric binaries to PATH...${C_RESET}"
  echo 'export PATH="$HOME/fabric/bin:$PATH"' >> ~/.bashrc
  source ~/.bashrc
fi

# Set FABRIC_CFG_PATH if not already set
if ! grep -q "export FABRIC_CFG_PATH=~/fabric/config" ~/.bashrc
then
    echo 'export FABRIC_CFG_PATH=~/fabric/config' >> ~/.bashrc
    echo 'FABRIC_CFG_PATH added to ~/.bashrc'
else
    echo 'FABRIC_CFG_PATH already exists in ~/.bashrc'
fi

echo -e "${C_BLUE}Adding container control script to fabric directory...${C_RESET}"
cp ./fabric/container.sh ~/fabric/

# Decide how to call the Python scripts based on MODE
if [ "$MODE" == "ALL" ]; then
    ARGUMENT="--all"
elif [ "$MODE" == "SPECIFY" ]; then
    # Adjusted to remove square brackets
    SPECIFIED_ORGS="${SPECIFIED_ORGS#[}"  # Remove leading '['
    SPECIFIED_ORGS="${SPECIFIED_ORGS%]}"  # Remove trailing ']'
    ARGUMENT="--specify=$SPECIFIED_ORGS"
else
    ARGUMENT="$NUM_CONTAINERS"
fi

echo -e "${C_BLUE}Generating crypto-config.yaml...${C_RESET}"
python3 ./fabric/config/generator/generate_cryptoconfig.py $ARGUMENT

echo -e "${C_BLUE}Adding cryptogen config to fabric directory...${C_RESET}"
cp ./fabric/config/generated/crypto-config.yaml ~/fabric

echo -e "${C_BLUE}Generating configtx.yaml...${C_RESET}"
python3 ./fabric/config/generator/generate_configtx.py $ARGUMENT

echo -e "${C_BLUE}Adding configtx.yaml to fabric directory...${C_RESET}"
cp ./fabric/config/generated/configtx.yaml ~/fabric/config

echo -e "${C_BLUE}Adding fabric scripts to fabric directory...${C_RESET}"
cp -r ./fabric/scripts ~/fabric

echo -e "${C_BLUE}Adding explorer docker-compose YAML to fabric directory...${C_RESET}"
# Create a temporary copy of the explorer directory
cp -r ./fabric/explorer ./explorer_tmp
# Replace the placeholder with the actual value in the copy of network.json
sed -i "s/\${FABRIC_CONTAINER_NUM}/${FABRIC_CONTAINER_NUM}/g" ./explorer_tmp/connection-profile/network.json
# Now copy the temporary explorer directory to the desired location
mkdir -p ~/fabric/explorer
cp -r ./explorer_tmp/* ~/fabric/explorer/
# Remove the temporary directory
rm -rf ./explorer_tmp

echo -e "${C_YELLOW}Note that: you may need to log back in to use docker without sudo${C_RESET}"
echo -e "${C_RED}Note that: you need source ~/.bashrc to activate the settings${C_RESET}"