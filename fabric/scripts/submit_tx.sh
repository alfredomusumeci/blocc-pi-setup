#!/bin/bash

set -x

# Check at least two arguments are given (Channel number and readings)
if [ $# -lt 2 ]; then
    echo "Usage: $0 <CHANNEL_NUMBER> <READINGS> [--all=true|--specify=[peer1,peer2,...]]"
    echo "Example: $0 3 \"[0.1,0.3,300]\" --all=true"
    exit 1
fi

CHANNEL_NUMBER=$1
READINGS=$2
ALL=false
SPECIFY=""

# Parse additional arguments
for arg in "$@"
do
    case $arg in
        --all=true)
        ALL=true
        shift # Remove --all=true from processing
        ;;
        --specify=*)
        SPECIFY="${arg#*=}"
        shift # Remove --specify=[...] from processing
        ;;
    esac
done

# Calculate IP Suffix based on CHANNEL_NUMBER
if [[ $CHANNEL_NUMBER -ge 1 && $CHANNEL_NUMBER -le 9 ]]; then
    IP_SUFFIX=20$CHANNEL_NUMBER
elif [[ $CHANNEL_NUMBER -ge 10 && $CHANNEL_NUMBER -le 11 ]]; then
    IP_SUFFIX=2$CHANNEL_NUMBER
else
    echo "Invalid CHANNEL_NUMBER"
    exit 1
fi

# Replace hostname with static IP
ORDERER_ENDPOINT=192.168.199.$IP_SUFFIX:7050
OSN_TLS_CA_ROOT_CERT=/home/pi/fabric/organizations/ordererOrganizations/container${CHANNEL_NUMBER}.blocc.doc.ic.ac.uk/tlsca/tlsca.container${CHANNEL_NUMBER}.blocc.doc.ic.ac.uk-cert.pem

# Declare an associative array for TLS root cert paths
declare -A TLS_ROOT_CERT_PATHS
for i in {1..11}; do
    TLS_ROOT_CERT_PATHS[$i]="/home/pi/fabric/organizations/peerOrganizations/container$i.blocc.doc.ic.ac.uk/peers/peer0.container$i.blocc.doc.ic.ac.uk/tls/ca.crt"
done

# Function to invoke sensor transaction for specified peers
invoke_sensor_transaction() {
    local peer_addresses=""
    local tls_root_cert_files=""

    for peer in "$@"; do
        local peer_ip=$((200 + peer)) # Adjust based on your networking setup
        local tls_root_cert_file=${TLS_ROOT_CERT_PATHS[$peer]}
        peer_addresses+="--peerAddresses 192.168.199.${peer_ip}:7051 "
        tls_root_cert_files+="--tlsRootCertFiles ${tls_root_cert_file} "
    done

    # Construct the Args JSON from the readings
    local args_json=$(echo "$READINGS" | sed 's/\[/"/;s/,/","/g;s/\]/"/')

    peer chaincode invoke -o "$ORDERER_ENDPOINT" \
--tls --cafile ${OSN_TLS_CA_ROOT_CERT} -C channel${CHANNEL_NUMBER} -n sensor_chaincode \
$peer_addresses \
$tls_root_cert_files \
-c "{\"Function\":\"addReading\",\"Args\":[$args_json]}"
}

# Main logic for deciding which peers to include
if [ "$ALL" = true ]; then
    invoke_sensor_transaction $(seq 1 11)
elif [ -n "$SPECIFY" ]; then
    IFS=',' read -ra PEERS <<< "${SPECIFY//[\[\]]/}" # Remove brackets and split
    invoke_sensor_transaction "${PEERS[@]}"
else
    echo "You must specify --all=true or --specify=[peers]"
    exit 1
fi

set +x
