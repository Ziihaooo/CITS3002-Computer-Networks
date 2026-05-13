"""Host and Router classes.

Host runs L2/L3/L4, Router runs L2/L3 only.
Shared log helper at the top so every layer prints in the same format.
"""

from protocol import Frame, Packet, Segment, compute_checksum, verify_checksum
from config import ETH_TYPE_IPV4, INITIAL_TTL, IP_PROTO_UDP, L4_TYPE_DATA, L4_TYPE_ACK, MAX_SEGMENT_DATA, DEFAULT_SRC_PORT, DEFAULT_DST_PORT

# logging helper
# prints one log line in the format the spec pdf expects
def log(device, layer, message):
    print(f"{device}: {layer}: {message}")

# routing helpers (used by L3 on hosts and routers)
# check if ip belongs to the given network 
# simple function because we only have /24 networks in this topologys
# so just compare the first 3 bytes of the ip and network
def ip_in_network(ip, network):
    return ip.rsplit(".", 1)[0] == network.rsplit(".", 1)[0]


# walk the routing table and return (next_hop_ip, out_iface) for dst_ip
def routing_lookup(routing_table, dst_ip):
    for network, _prefix, next_hop, iface in routing_table: 
        if ip_in_network(dst_ip, network): # if the dst_ip belongs to this network
            return (next_hop if next_hop else dst_ip, iface) # return the next_hop_ip (or dst_ip itself if next_hop is None, meaning it's directly connected) and the outgoing interface
    return (None, None)  # no route found

# Host
class Host:
    def __init__(self, name, ip, mac, mac_table, routing_table):
        self.name = name                    # for logging only, e.g. "Host A"
        self.ip = ip                        # IP address (4 bytes), the host's own IP address  
        self.mac = mac                      # MAC address (6 bytes), the host's own MAC address       
        self.mac_table = mac_table          # each host has one mac table mapping next-hop ip -> mac, used by L2 to find the dst mac for a given next-hop ip
        self.routing_table = routing_table  # routing table used by L3 to find the next-hop ip and outgoing interface when sending
        self.peer = None                    # the other end (host or router) of the link, set by main.py when building the topology
        self.peer_iface = None              # which interface we arrive on at the peer
        self.next_seq = 0                   # seq num to use to put on the next data segment this hst send (flips 0 -> 1 -> 0 ...)
        self.last_ack_seq = None            # seq num of the last ACK this host received
        self.expected_seq = 0               # seq num this host expect on the next incoming DATA segment

    # called when a frame is received from other peer and delivered from L2 to L3
    def receive_frame(self, frame, ingress_iface=None):
        log(self.name, "Layer 2", "Frame received") # L2 of peer to L2 of this host
        log(self.name, "Layer 2", f"Source MAC learned: {frame.src_mac}") # log the source mac
        log(self.name, "Layer 2", "Packet delivered to Network Layer") # to L3 of this host
        print() # blank line between L2 and L3 sections (matches spec example)
        self.receive_packet(frame.payload) # Call L3 receive_packet with the frame's payload, which is the L3 packet

    # called when a packet is received from L2 and delivered to L3
    def receive_packet(self, packet):
        log(self.name, "Layer 3", f"Packet received from Data Link Layer: SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}") # L2 of this host to L3 of this host
        log(self.name, "Layer 3", f"Destination IP read: {packet.dst_ip}") # read the dst ip from the packet to decide what to do
        if packet.dst_ip == self.ip: # if dst ip is this host's own ip then it's local delivery
            log(self.name, "Layer 3", "Packet identified as local delivery") # log the local delivery decision
            log(self.name, "Layer 3", "Segment delivered to Transport Layer") # to L4 of this host
            print() # blank line between L3 and L4 sections (matches spec example)
            self.receive_segment(packet.payload, packet.src_ip) # Call L4 receive_segment with the packet's payload, which is the L4 segment, and the sender's IP for the ACK return

    # called by main.py to send a message to a destination host
    # splits into 500-byte segments and uses alternating-bit (retransmit on wrong ACK)
    def send_message(self, data, dst_ip):
        log(self.name, "Layer 4", f"Data received from Application Layer. Data size={len(data)}") # from app of this host
        # split the data into chunks of MAX_SEGMENT_DATA bytes (500)
        chunks = [data[i: i + MAX_SEGMENT_DATA] for i in range(0, len(data), MAX_SEGMENT_DATA)]
        for chunk in chunks: # send each chunk one at a time using alternating-bit rdt2.2
            seq = self.next_seq # current seq num for this segment (0 or 1)
            while True: # keep sending this chunk until we get the correct ACK back
                seg = Segment(DEFAULT_SRC_PORT, DEFAULT_DST_PORT, 10 + len(chunk), 0, L4_TYPE_DATA, seq, chunk) # build the DATA segment, length = 10 header + chunk size
                seg.checksum = compute_checksum(seg.src_port, seg.dst_port, seg.length, seg.seg_type, seg.seq_num, seg.data) # compute the checksum for the segment
                log(self.name, "Layer 4", "Checksum computed") # log the checksum computation
                log(self.name, "Layer 4", f"Segment created by adding transport layer header (DATA, seq={seq}) (encapsulation)") # log the DATA segment creation
                log(self.name, "Layer 4", "Segment sent to Network Layer") # to L3 of this host
                print() # blank line between L4 and L3 sections (matches spec example)
                self.send_packet(seg, dst_ip) # send the segment, by the time this returns the ACK has been processed (synchronous)
                if self.last_ack_seq == seq: # correct ACK received, this chunk is done
                    break
                log(self.name, "Layer 4", "Segment retransmitted due to incorrect ACK") # log the retransmit (spec assumes no loss so this never fires)
            self.next_seq = 1 - seq # flip seq for the next chunk

    # called when a segment is received from L3 and delivered to L4, with the sender's IP for ACK return
    def receive_segment(self, segment, src_ip):
        log(self.name, "Layer 4", "Segment received from Network Layer") # L3 of this host to L4 of this host
        if not verify_checksum(segment): # recompute and compare to the segment's stored checksum
            log(self.name, "Layer 4", "Segment discarded due to checksum error") # log the discard (spec assumes no corruption so this never fires)
            return # corrupted segment, discard it and don't send an ACK
        log(self.name, "Layer 4", "Checksum verified") # log the successful checksum verification
        if segment.seg_type == L4_TYPE_DATA: # incoming DATA segment from peer
            if segment.seq_num == self.expected_seq: # fresh DATA matching the expected seq, accept and deliver
                log(self.name, "Layer 4", f"DATA segment delivered to Application Layer. Data size={len(segment.data)}") # to app of this host
                self.expected_seq = 1 - self.expected_seq # flip expected_seq for the next incoming DATA
            # build the ACK with the same seq we just received, so fresh data gets a new ack and duplicate data gets the old ack again
            ack = Segment(segment.dst_port, segment.src_port, 10, 0, L4_TYPE_ACK, segment.seq_num, b"") # 10 = L4 header size, empty data for ACK
            ack.checksum = compute_checksum(ack.src_port, ack.dst_port, ack.length, ack.seg_type, ack.seq_num, ack.data) # compute the checksum for the ACK
            log(self.name, "Layer 4", f"Segment created by adding transport layer header (ACK, seq={ack.seq_num})") # log the ACK creation
            log(self.name, "Layer 4", "Segment sent to Network Layer") # to L3 of this host
            print() # blank line between L4 and L3 sections (matches spec example)
            self.send_packet(ack, src_ip) # send the ACK back to the original sender
        elif segment.seg_type == L4_TYPE_ACK: # incoming ACK segment from peer
            log(self.name, "Layer 4", f"ACK received: seq={segment.seq_num}") # log the ACK with its seq
            self.last_ack_seq = segment.seq_num # remember the ACK seq so the sender can check it after send_packet returns

    # called by L4 to send a segment out: wrap in a packet, do routing, hand to L2
    def send_packet(self, segment, dst_ip):
        src_ip = self.ip
        ttl = INITIAL_TTL # initial TTL for outbound packets from hosts
        log(self.name, "Layer 3", f"Segment received from Transport Layer: SRC_IP={src_ip}, DST_IP={dst_ip}, TTL={ttl}") # L4 of this host to L3 of this host
        log(self.name, "Layer 3", f"Destination IP read: {dst_ip}") # read the destination ip from the segment to start routing
        log(self.name, "Layer 3", "Routing table lookup performed") # look up the routing table to find next-hop and out-iface
        next_hop_ip, _out_iface = routing_lookup(self.routing_table, dst_ip) # hosts only have one interface so out_iface is not needed for send_frame
        log(self.name, "Layer 3", f"Next-hop IP determined: {next_hop_ip}") # log the determined next-hop ip
        log(self.name, "Layer 3", "Outgoing interface selected") # log the outgoing interface (just one for hosts)
        packet = Packet(src_ip, dst_ip, ttl, IP_PROTO_UDP, 12 + segment.length, segment) # build the packet wrapping the segment from L4 and 12 bytes for the L3 header
        log(self.name, "Layer 3", "Packet forwarded to Data Link Layer") # to L2 of this host
        print() # blank line between L3 and L2 sections (matches spec example)
        self.send_frame(packet, next_hop_ip) # Call L2 send_frame with the built packet and the next-hop ip

    # called by L3 when need to send a packet out: do L2 dst mac lookup, build frame, and call peer's L2 receive_frame
    def send_frame(self, packet, next_hop_ip):
        log(self.name, "Layer 2", "Packet received from Network Layer")  # L3 of this host to L2 of this host
        dst_mac = self.mac_table[next_hop_ip] # look up the destination mac for the given next-hop ip using the host's mac table
        log(self.name, "Layer 2", f"Destination MAC lookup for next-hop IP ({next_hop_ip}) → {dst_mac}") # log the result of the mac table lookup
        frame = Frame(dst_mac, self.mac, ETH_TYPE_IPV4, packet) # create a frame with the given packet as payload, and the looked up dst mac and this host's mac as src mac
        log(self.name, "Layer 2", f"Frame created: SRC_MAC={self.mac}, DST_MAC={dst_mac}") # log the creation of the frame with src and dst mac
        log(self.name, "Layer 2", "Frame sent") # to L2 of peer
        print() # blank line between sending host's L2 and receiving peer's L2 (matches spec example)
        self.peer.receive_frame(frame, ingress_iface=self.peer_iface) # Call the L2 of the peer with the created frame, and specify which interface we arrive on at the peer

# Router
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
        print() # blank line between L2 and L3 sections (matches spec example)
        self.receive_packet(frame.payload, ingress_iface) # Call L3 receive_packet with the frame's payload, which is the L3 packet, and the ingress interface

    # called when a packet is received from L2 and delivered to L3, with the ingress interface specified for routing decisions
    def receive_packet(self, packet, ingress_iface):
        log(self.name, "Layer 3", f"Packet received from Data Link Layer: SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}") # L2 of this router to L3 of this router
        log(self.name, "Layer 3", f"Destination IP read: {packet.dst_ip}") # read the dst ip from the packet to start routing
        old_ttl = packet.ttl # remember the old TTL for the decrement log line
        packet.ttl -= 1 # router decrements TTL by 1 at every hop (per spec)
        log(self.name, "Layer 3", f"TTL decremented: {old_ttl} → {packet.ttl}") # log the TTL decrement using the unicode arrow
        if packet.ttl == 0: # if TTL reaches 0 then drop the packet (per spec)
            log(self.name, "Layer 3", "Packet dropped due to TTL expiry") # log the drop event
            return # don't forward the packet any further
        log(self.name, "Layer 3", "Routing table lookup performed") # look up the routing table to find next-hop and out-iface
        next_hop_ip, out_iface = routing_lookup(self.routing_table, packet.dst_ip) # find next-hop ip and outgoing interface for the dst ip
        log(self.name, "Layer 3", f"Next-hop IP determined: {next_hop_ip}") # log the determined next-hop ip
        log(self.name, "Layer 3", f"Outgoing interface selected ({out_iface})") # log the outgoing interface (router has two)
        log(self.name, "Layer 3", "Packet forwarded to Data Link Layer") # to L2 of this router
        print() # blank line between L3 and L2 sections (matches spec example)
        self.send_frame(packet, next_hop_ip, out_iface) # Call L2 send_frame with the packet, next-hop ip, and outgoing interface

    # called when need to forward a frame out a specific interface to other peer
    def send_frame(self, packet, next_hop_ip, out_iface):
        iface = self.interfaces[out_iface] # look up the interface info using the out_iface name
        log(self.name, "Layer 2", "Packet received from Network Layer") # L3 of this router to L2 of this router
        dst_mac = iface["mac_table"][next_hop_ip] # look up the dst mac for the given next-hop ip using this interface's mac table
        log(self.name, "Layer 2", f"Destination MAC lookup for next-hop IP ({next_hop_ip}) → {dst_mac}") # log the result of the mac table lookup
        frame = Frame(dst_mac, iface["mac"], ETH_TYPE_IPV4, packet) # create a frame with the given packet as payload, looked up dst mac, and this interface's mac as src mac
        log(self.name, "Layer 2", f"Frame created: SRC_MAC={iface['mac']}, DST_MAC={dst_mac}") # log the creation of the frame with src and dst mac
        log(self.name, "Layer 2", f"Frame forwarded on {out_iface}") # to L2 of peer via the specified outgoing interface
        print() # blank line between this router's L2 and the receiving peer's L2 (matches spec example)
        iface["peer"].receive_frame(frame, ingress_iface=iface["peer_iface"]) # Call the L2 of the peer with the created frame, and specify which interface we arrive on at the peer
