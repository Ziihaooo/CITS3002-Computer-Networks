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

    # L3 calls this when it wants to send a packet out
    def send_frame(self, packet, next_hop_ip):
        log(self.name, "Layer 2", "Packet received from Network Layer")
        dst_mac = self.mac_table[next_hop_ip]
        log(self.name, "Layer 2", f"Destination MAC lookup for next-hop IP ({next_hop_ip}) -> {dst_mac}")
        frame = Frame(dst_mac, self.mac, ETH_TYPE_IPV4, packet)
        log(self.name, "Layer 2", f"Frame created: SRC_MAC={self.mac}, DST_MAC={dst_mac}")
        log(self.name, "Layer 2", "Frame sent")
        # transmit by calling into the peer (in-process, no real network)
        self.peer.receive_frame(frame, ingress_iface=self.peer_iface)

    # peer calls this when a frame arrives on the wire
    def receive_frame(self, frame, ingress_iface=None):
        log(self.name, "Layer 2", "Frame received")
        log(self.name, "Layer 2", f"Source MAC learned: {frame.src_mac}")
        log(self.name, "Layer 2", "Packet delivered to Network Layer")
        self.receive_packet(frame.payload)

    # stub - partner fills this in for #7 (layer 3)
    def receive_packet(self, packet):
        pass


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
