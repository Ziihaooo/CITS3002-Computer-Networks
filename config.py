"""Static config for the network.
Holds the topology - ip addresses, mac addresses, routing tables, etc.
Read by main.py when building the Host and Router objects.

Topology:
    Host A ----L1---- Router R1 ----L2---- Host B
    10.0.1.10        10.0.1.1 / 10.0.2.1    10.0.2.20

    Network 1 (L1): 10.0.1.0/24
    Network 2 (L2): 10.0.2.0/24
"""

# ---------------------------------------------------------------------------
# ip addresses
# ---------------------------------------------------------------------------

HOST_A_IP = "10.0.1.10"
HOST_B_IP = "10.0.2.20"
R1_IF1_IP = "10.0.1.1"
R1_IF2_IP = "10.0.2.1"

NETWORK_1 = ("10.0.1.0", 24)
NETWORK_2 = ("10.0.2.0", 24)

# ---------------------------------------------------------------------------
# mac addresses
# ---------------------------------------------------------------------------

HOST_A_MAC = "AA:AA:AA:AA:AA:AA"
R1_IF1_MAC = "BB:BB:BB:BB:BB:BB"
R1_IF2_MAC = "CC:CC:CC:CC:CC:CC"
HOST_B_MAC = "DD:DD:DD:DD:DD:DD"

# ---------------------------------------------------------------------------
# interface names
# ---------------------------------------------------------------------------

# hosts only have one interface, r1 has two
# r1 interface names must match the spec log lines exactly
HOST_IFACE = "eth0"
R1_IFACE_1 = "Interface 1"
R1_IFACE_2 = "Interface 2"

# ---------------------------------------------------------------------------
# routing tables (per node)
# ---------------------------------------------------------------------------
# each entry: (network, prefix_length, next_hop_ip, outgoing_interface)
# if next_hop is None then the network is directly connected, so the l3
# code should set next_hop = the packet's destination ip at lookup time
# (spec: "next-hop IP is set to the destination IP itself")

HOST_A_ROUTING_TABLE = [
    ("10.0.1.0", 24, None,       HOST_IFACE),  # directly connected
    ("10.0.2.0", 24, R1_IF1_IP,  HOST_IFACE),  # via r1
]

HOST_B_ROUTING_TABLE = [
    ("10.0.2.0", 24, None,       HOST_IFACE),  # directly connected
    ("10.0.1.0", 24, R1_IF2_IP,  HOST_IFACE),  # via r1
]

R1_ROUTING_TABLE = [
    ("10.0.1.0", 24, None, R1_IFACE_1),  # directly connected on interface 1
    ("10.0.2.0", 24, None, R1_IFACE_2),  # directly connected on interface 2
]

# ---------------------------------------------------------------------------
# mac tables (next-hop ip -> mac)
# ---------------------------------------------------------------------------
# layer 2 uses these to find the destination mac for a given next-hop ip
# r1 has one per interface because each interface is on its own subnet

HOST_A_MAC_TABLE = {
    R1_IF1_IP: R1_IF1_MAC,
}

HOST_B_MAC_TABLE = {
    R1_IF2_IP: R1_IF2_MAC,
}

R1_MAC_TABLE_IF1 = {
    HOST_A_IP: HOST_A_MAC,
}

R1_MAC_TABLE_IF2 = {
    HOST_B_IP: HOST_B_MAC,
}

# ---------------------------------------------------------------------------
# protocol constants
# ---------------------------------------------------------------------------

# layer 2
ETH_TYPE_IPV4 = 0x0800 # indicates the payload is an ipv4 packet

# layer 3
IP_PROTO_UDP = 17 # indicates the payload is a udp segment (rdt2.2 in our case)
INITIAL_TTL = 100 # initial TTL for packets sent by hosts
# layer 4
L4_TYPE_DATA = 0 # indicates a data segment (rdt2.2) 
L4_TYPE_ACK = 1  # indicates an ACK segment (rdt2.2)
MAX_SEGMENT_DATA = 500  # max app data per segment in bytes

# default ports (matches the spec example trace)
DEFAULT_SRC_PORT = 5000  # arbitrary source port for segments sent by hosts
DEFAULT_DST_PORT = 80    # arbitrary destination port for segments sent by hosts, just for logging
