# templates.py

ContainerOrdererTemplate = """- &ContainerOrdererOrg{i}

  Name: ContainerOrderer{i}MSP
  ID: ContainerOrderer{i}MSP
  MSPDir: ../organizations/ordererOrganizations/container{i}.blocc.doc.ic.ac.uk/msp
  Policies:
    Readers:
      Type: Signature
      Rule: "OR('ContainerOrderer{i}MSP.member')"
    Writers:
      Type: Signature
      Rule: "OR('ContainerOrderer{i}MSP.member')"
    Admins:
      Type: Signature
      Rule: "OR('ContainerOrderer{i}MSP.admin')"
  OrdererEndpoints:
  - 192.168.199.{endpoint}:7050

"""

ContainerOrgTemplate = """- &ContainerOrg{i}
  Name: Container{i}MSP
  ID: Container{i}MSP
  MSPDir: ../organizations/peerOrganizations/container{i}.blocc.doc.ic.ac.uk/msp
  Policies:
    Readers:
      Type: Signature
      Rule: "OR('Container{i}MSP.admin', 'Container{i}MSP.peer', 'Container{i}MSP.client')"
    Writers:
      Type: Signature
      Rule: "OR('Container{i}MSP.admin', 'Container{i}MSP.client')"
    Admins:
      Type: Signature
      # Adding peer to Admins since each peerOrg is a shipping container
      Rule: "OR('Container{i}MSP.admin', 'Container{i}MSP.peer')"
    Endorsement:
      Type: Signature
      Rule: "OR('Container{i}MSP.peer')"

"""

CapabilitiesApplicationTemplateStatic = """Capabilities:
  Channel: &ChannelCapabilities
    V2_0: true

  Orderer: &OrdererCapabilities
    V2_0: true

  Application: &ApplicationCapabilities
    V2_5: true

Application: &ApplicationDefaults

  Organizations:
"""

# Function to dynamically generate the organizations part
def generate_capabilities_application_template_dynamic(orgs):
    organizations_yaml = ""
    for i in orgs:
        organizations_yaml += f"    - *ContainerOrg{i}\n"
    return CapabilitiesApplicationTemplateStatic + organizations_yaml + """
  Policies:
    Readers:
      Type: ImplicitMeta
      Rule: "ANY Readers"
    Writers:
      Type: ImplicitMeta
      Rule: "ANY Writers"
    Admins:
      Type: ImplicitMeta
      Rule: "MAJORITY Admins"
    LifecycleEndorsement:
      Type: ImplicitMeta
      Rule: "MAJORITY Endorsement"
    Endorsement:
      Type: ImplicitMeta
      Rule: "MAJORITY Endorsement"

  Capabilities:
    <<: *ApplicationCapabilities

"""

OrdererTemplate = """Orderer: &ContainerOrderer{i}

  OrdererType: etcdraft

  EtcdRaft:
    Consenters:
    - Host: 192.168.199.{endpoint}
      Port: 7050
      # NOTE: For simplicity, each orderer in this example is using the same TLS certificate for both the server and client, although this is not required.
      ClientTLSCert: ../organizations/ordererOrganizations/container{i}.blocc.doc.ic.ac.uk/orderers/orderer.container{i}.blocc.doc.ic.ac.uk/tls/server.crt
      ServerTLSCert: ../organizations/ordererOrganizations/container{i}.blocc.doc.ic.ac.uk/orderers/orderer.container{i}.blocc.doc.ic.ac.uk/tls/server.crt

  BatchTimeout: 2s

  BatchSize:
    MaxMessageCount: 1
    AbsoluteMaxBytes: 99 MB
    PreferredMaxBytes: 512 KB
  Organizations:
  Policies:
    Readers:
      Type: ImplicitMeta
      Rule: "ANY Readers"
    Writers:
      Type: ImplicitMeta
      Rule: "ANY Writers"
    Admins:
      Type: ImplicitMeta
      Rule: "MAJORITY Admins"
    # BlockValidation specifies what signatures must be included in the block
    # from the orderer for the peer to validate it.
    BlockValidation:
      Type: ImplicitMeta
      Rule: "ANY Writers"
    SensorySigners:
      Type: ImplicitMeta
      Rule: "ANY Readers"

"""

ChannelTemplate = """Channel: &Channel{i}
  Policies:
    # Who may invoke the 'Deliver' API
    Readers:
      Type: ImplicitMeta
      Rule: "ANY Readers"
    # Who may invoke the 'Broadcast' API
    Writers:
      Type: ImplicitMeta
      Rule: "ANY Writers"
    # By default, who may modify elements at this config level
    Admins:
      Type: ImplicitMeta
      Rule: "MAJORITY Admins"
    ChannelLeader:
      Type: Signature
      Rule: "OR('Container{i}MSP.member')"
    SensorySigners:
      Type: ImplicitMeta
      Rule: "ANY Readers"

  Capabilities:
    <<: *ChannelCapabilities

"""

ProfileTemplate = """
  Channel{i}Genesis:
    <<: *Channel{i}
    Orderer:
      <<: *ContainerOrderer{i}
      Organizations:
      - *ContainerOrdererOrg{i}
      Capabilities: *OrdererCapabilities
    Application: *ApplicationDefaults
"""
