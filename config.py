"""Static configuration for the network topology.

Defines the fixed parameters of the simulator: IP addresses, MAC
addresses, routing tables, and per-node MAC tables. These values
are read by main.py when constructing the Host and Router objects.

Topology:

    Host A ----L1---- Router R1 ----L2---- Host B
    10.0.1.10        10.0.1.1 / 10.0.2.1     10.0.2.20

    Network 1 (L1): 10.0.1.0/24
    Network 2 (L2): 10.0.2.0/24
"""

# ---------------------------------------------------------------------------
# IP addresses
# ---------------------------------------------------------------------------

HOST_A_IP = "10.0.1.10"
HOST_B_IP = "10.0.2.20"
R1_IF1_IP = "10.0.1.1"
R1_IF2_IP = "10.0.2.1"

NETWORK_1 = ("10.0.1.0", 24)
NETWORK_2 = ("10.0.2.0", 24)

# ---------------------------------------------------------------------------
# MAC addresses
# ---------------------------------------------------------------------------

HOST_A_MAC = "AA:AA:AA:AA:AA:AA"
R1_IF1_MAC = "BB:BB:BB:BB:BB:BB"
R1_IF2_MAC = "CC:CC:CC:CC:CC:CC"
HOST_B_MAC = "DD:DD:DD:DD:DD:DD"

# ---------------------------------------------------------------------------
# Interface names
# ---------------------------------------------------------------------------

# Hosts have a single interface; R1 has two named interfaces (matching the
# names used in the spec's expected log output: "Interface 1" / "Interface 2").
HOST_IFACE = "eth0"
R1_IFACE_1 = "Interface 1"
R1_IFACE_2 = "Interface 2"

# ---------------------------------------------------------------------------
# Routing tables (per node)
# ---------------------------------------------------------------------------
#
# Each entry: (destination_network, prefix_length, next_hop_ip, outgoing_interface)
#
# When `next_hop_ip` is None the destination network is directly connected,
# so the L3 routing logic should set the next-hop IP equal to the packet's
# destination IP (per spec: "Since the destination is on a directly connected
# network, the next-hop IP is set to the destination IP itself").

HOST_A_ROUTING_TABLE = [
    ("10.0.1.0", 24, None,       HOST_IFACE),  # directly connected
    ("10.0.2.0", 24, R1_IF1_IP,  HOST_IFACE),  # via R1
]

HOST_B_ROUTING_TABLE = [
    ("10.0.2.0", 24, None,       HOST_IFACE),  # directly connected
    ("10.0.1.0", 24, R1_IF2_IP,  HOST_IFACE),  # via R1
]

R1_ROUTING_TABLE = [
    ("10.0.1.0", 24, None, R1_IFACE_1),  # directly connected via Interface 1
    ("10.0.2.0", 24, None, R1_IFACE_2),  # directly connected via Interface 2
]

# ---------------------------------------------------------------------------
# MAC tables (next-hop IP -> MAC)
# ---------------------------------------------------------------------------
#
# Static map used by Layer 2 to resolve the destination MAC for a given
# next-hop IP supplied by Layer 3. (Real systems would populate this via
# ARP; this simulator hard-codes it for determinism.)

HOST_A_MAC_TABLE = {
    R1_IF1_IP: R1_IF1_MAC,
}

HOST_B_MAC_TABLE = {
    R1_IF2_IP: R1_IF2_MAC,
}

# R1 has a per-interface MAC table because each interface lives on a
# different subnet and only knows the MACs reachable on its own link.
R1_MAC_TABLE_IF1 = {
    HOST_A_IP: HOST_A_MAC,
}

R1_MAC_TABLE_IF2 = {
    HOST_B_IP: HOST_B_MAC,
}

# ---------------------------------------------------------------------------
# Protocol constants
# ---------------------------------------------------------------------------

# Layer 2
ETH_TYPE_IPV4 = 0x0800

# Layer 3
IP_PROTO_UDP = 17
INITIAL_TTL = 100

# Layer 4
L4_TYPE_DATA = 0
L4_TYPE_ACK = 1
MAX_SEGMENT_DATA = 500  # max application data per UDP-like segment (bytes)

# Default application ports (matching the spec example trace)
DEFAULT_SRC_PORT = 5000
DEFAULT_DST_PORT = 80
