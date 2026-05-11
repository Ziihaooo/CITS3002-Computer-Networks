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

    # called when a frame is received from other peer and delivered from L2 to L3
    def receive_frame(self, frame, ingress_iface=None):
        log(self.name, "Layer 2", "Frame received") # L2 of peer to L2 of this host
        log(self.name, "Layer 2", f"Source MAC learned: {frame.src_mac}") # log the source mac
        log(self.name, "Layer 2", "Packet delivered to Network Layer") # to L3 of this host
        self.receive_packet(frame.payload) # Call L3 receive_packet with the frame's payload, which is the L3 packet

    # called when need to send a frame to other peer
    def send_frame(self, packet, next_hop_ip):
        log(self.name, "Layer 2", "Packet received from Network Layer")  # L3 of this host to L2 of this host
        dst_mac = self.mac_table[next_hop_ip] # look up the destination mac for the given next-hop ip using the host's mac table
        log(self.name, "Layer 2", f"Destination MAC lookup for next-hop IP ({next_hop_ip}) -> {dst_mac}") # log the result of the mac table lookup
        frame = Frame(dst_mac, self.mac, ETH_TYPE_IPV4, packet) # create a frame with the given packet as payload, and the looked up dst mac and this host's mac as src mac
        log(self.name, "Layer 2", f"Frame created: SRC_MAC={self.mac}, DST_MAC={dst_mac}") # log the creation of the frame with src and dst mac
        log(self.name, "Layer 2", "Frame sent") # to L2 of peer
        self.peer.receive_frame(frame, ingress_iface=self.peer_iface) # Call the L2 of the peer with the created frame, and specify which interface we arrive on at the peer


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

    # called when a frame is received on an interface and delivered from L2 to L3
    def receive_frame(self, frame, ingress_iface):
        log(self.name, "Layer 2", f"Frame received on {ingress_iface}") # L2 of peer to L2 of this router on the given interface
        self.learning_table[frame.src_mac] = ingress_iface # learn the source mac and which interface it came from (dynamic mac learning)
        log(self.name, "Layer 2", f"Source MAC learned: {frame.src_mac} on {ingress_iface}") # log the learned source mac
        log(self.name, "Layer 2", "Packet delivered to Network Layer") # to L3 of this router
        self.receive_packet(frame.payload, ingress_iface) # Call L3 receive_packet with the frame's payload and the ingress interface

    # called when need to forward a frame out a specific interface to other peer
    def send_frame(self, packet, next_hop_ip, out_iface):
        iface = self.interfaces[out_iface] # look up the interface info using the out_iface name
        log(self.name, "Layer 2", "Packet received from Network Layer") # L3 of this router to L2 of this router
        dst_mac = iface["mac_table"][next_hop_ip] # look up the dst mac for the given next-hop ip using this interface's mac table
        log(self.name, "Layer 2", f"Destination MAC lookup for next-hop IP ({next_hop_ip}) -> {dst_mac}") # log the result of the mac table lookup
        frame = Frame(dst_mac, iface["mac"], ETH_TYPE_IPV4, packet) # create a frame with the given packet as payload, looked up dst mac, and this interface's mac as src mac
        log(self.name, "Layer 2", f"Frame created: SRC_MAC={iface['mac']}, DST_MAC={dst_mac}") # log the creation of the frame with src and dst mac
        log(self.name, "Layer 2", f"Frame forwarded on {out_iface}") # to L2 of peer via the specified outgoing interface
        iface["peer"].receive_frame(frame, ingress_iface=iface["peer_iface"]) # Call the L2 of the peer with the created frame, and specify which interface we arrive on at the peer
