"""Header classes for L2 (Frame), L3 (Packet), L4 (Segment).
Defines the data structures for the headers of each layer
"""

# ---------------------------------------------------------------------------
# Layer 2 - ethernet-like frame
# ---------------------------------------------------------------------------

# layer 2 frame: mac addressing + type + l3 packet as payload
class Frame:
    def __init__(self, dst_mac, src_mac, eth_type, payload):
        self.dst_mac = dst_mac      # Destination MAC (6 bytes)
        self.src_mac = src_mac      # Source MAC (6 bytes)
        self.eth_type = eth_type    # Type (2 bytes) - 0x0800 for IPv4
        self.payload = payload      # Payload (variable length) - typically an L3 packet


# ---------------------------------------------------------------------------
# Layer 3 - ip-like packet
# ---------------------------------------------------------------------------

# layer 3 packet: src/dst ip + ttl + protocol + l4 segment as payload
class Packet:
    def __init__(self, src_ip, dst_ip, ttl, protocol, total_length, payload):
        self.src_ip = src_ip                # Source IP (4 bytes)
        self.dst_ip = dst_ip                # Destination IP (4 bytes)    
        self.ttl = ttl                      # TTL (1 byte) - decremented by each router, discard if 0
        self.protocol = protocol            # Protocol (1 byte) - 17 for UDP
        self.total_length = total_length    # Total length (2 bytes) - header + payload
        self.payload = payload              # Payload (variable length) - typically an L4 segment


# ---------------------------------------------------------------------------
# Layer 4 - udp-like segment with ack (rdt2.2)
# ---------------------------------------------------------------------------

# layer 4 segment: ports + length + checksum + type/seq + data
class Segment:
    def __init__(self, src_port, dst_port, length, checksum, seg_type, seq_num, data):
        self.src_port = src_port    # Source port (2 bytes)
        self.dst_port = dst_port    # Destination port (2 bytes)
        self.length = length        # Length (2 bytes) - header + data
        self.checksum = checksum    # Checksum (2 bytes) - for error detection, can be 0 for simplicity
        self.seg_type = seg_type    # Type (1 byte) - 0 for data, 1 for ACK
        self.seq_num = seq_num      # Sequence number (1 byte) - for rdt2.2, alternates between 0 and 1
        self.data = data            # Data (variable length) - the actual message payload for data segments, empty for ACKs
