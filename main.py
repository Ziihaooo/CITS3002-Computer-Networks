"""Mini Internet Protocol Stack Simulator — entry point.

Usage:
    python main.py <message_size_in_bytes>

Example:
    python main.py 100

Builds Host A, Router R1, and Host B according to the topology defined
in config.py, then sends a message of the given size from Host A to
Host B using the simulated L2/L3/L4 stack.
"""

import sys
from config import (
    HOST_A_IP, HOST_A_MAC, HOST_A_MAC_TABLE, HOST_A_ROUTING_TABLE,
    HOST_B_IP, HOST_B_MAC, HOST_B_MAC_TABLE, HOST_B_ROUTING_TABLE,
    R1_IF1_IP, R1_IF1_MAC, R1_MAC_TABLE_IF1,
    R1_IF2_IP, R1_IF2_MAC, R1_MAC_TABLE_IF2,
    R1_ROUTING_TABLE, R1_IFACE_1, R1_IFACE_2,
)
from devices import Host, Router

# read the message size from the command line, e.g. "python main.py 100"
size = int(sys.argv[1])

# build the three devices from the topology config
host_a = Host("Host A", HOST_A_IP, HOST_A_MAC, HOST_A_MAC_TABLE, HOST_A_ROUTING_TABLE)
host_b = Host("Host B", HOST_B_IP, HOST_B_MAC, HOST_B_MAC_TABLE, HOST_B_ROUTING_TABLE)
r1 = Router(
    "Router R1",
    if1={"ip": R1_IF1_IP, "mac": R1_IF1_MAC, "mac_table": R1_MAC_TABLE_IF1},
    if2={"ip": R1_IF2_IP, "mac": R1_IF2_MAC, "mac_table": R1_MAC_TABLE_IF2},
    routing_table=R1_ROUTING_TABLE,
)

# wire the peers (the "cables" between devices)
# Host A <-> R1 Interface 1
host_a.peer = r1
host_a.peer_iface = R1_IFACE_1
r1.interfaces[R1_IFACE_1]["peer"] = host_a

# Host B <-> R1 Interface 2
host_b.peer = r1
host_b.peer_iface = R1_IFACE_2
r1.interfaces[R1_IFACE_2]["peer"] = host_b

# generate dummy bytes of the requested size and kick off the send from Host A to Host B
data = b"X" * size
host_a.send_message(data, HOST_B_IP)
