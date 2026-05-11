"""Host and Router classes.

Host runs L2/L3/L4, Router runs L2/L3 only.
Shared log helper at the top so every layer prints in the same format.
"""

from protocol import Frame
from config import ETH_TYPE_IPV4

# ---------------------------------------------------------------------------
# logging helper
# ---------------------------------------------------------------------------

# prints one log line in the format the spec pdf expects
def log(device, layer, message):
    print(f"{device}: {layer}: {message}")


# blank line between sections so the output is easier to read
def log_blank():
    print()


# ---------------------------------------------------------------------------
# Host
# ---------------------------------------------------------------------------

class Host:
    def __init__(self, name, ip, mac, mac_table, routing_table):
        self.name = name                    # for logging only, e.g. "Host A"
        self.ip = ip                        # IP address (4 bytes), the host's own IP address  
        self.mac = mac                      # MAC address (6 bytes), the host's own MAC address       
        self.mac_table = mac_table          # each host has one mac table mapping next-hop ip -> mac, used by L2 to find the dst mac for a given next-hop ip
        self.routing_table = routing_table  # each host has a routing table for L3 lookups, just for completeness and not used in this topology
        self.peer = None                    # the other end (host or router) of the link, set by main.py when building the topology
        self.peer_iface = None              # which interface we arrive on at the peer




# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

class Router:
    def __init__(self, name, if1, if2, routing_table):
        self.name = name                    # for logging, e.g. "Router R1"
        # each interface is a dict with keys: ip, mac, mac_table (next-hop ip -> mac).
        # peer and peer_iface get wired up in main.py when the topology is built.
        # Router need this to look up info when forwarding packets out each interface.
        # if1 and if2 will have the info ip, mac, and mac_table for the directly connected subnet on that interface.
        self.interfaces = {
            "Interface 1": dict(if1, peer=None, peer_iface=None),
            "Interface 2": dict(if2, peer=None, peer_iface=None),
        }
        self.routing_table = routing_table  # routing table for L3 lookups, used by L3 to find the outgoing interface and next-hop ip for a given destination ip
        self.learning_table = {}            # learn incoming source MAC + which interface it came from
 