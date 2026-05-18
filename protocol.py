"""Header classes for L2 (Frame), L3 (Packet), L4 (Segment).
Defines the data structures for the headers of each layer
"""

# layer 2 frame: mac addressing + type + L3 packet as payload
class Frame:
    def __init__(self, dst_mac, src_mac, eth_type, payload):
        self.dst_mac = dst_mac      # Destination MAC (6 bytes) - typically looked up from the next-hop IP using the mac table
        self.src_mac = src_mac      # Source MAC (6 bytes) - the sender's MAC address
        self.eth_type = eth_type    # Type (2 bytes) - 0x0800 for IPv4
        self.payload = payload      # Payload (variable length) - typically an L3 packet

# layer 3 packet: src/dst ip + ttl + protocol + L4 segment as payload
class Packet:
    def __init__(self, src_ip, dst_ip, ttl, protocol, total_length, payload):
        self.src_ip = src_ip                # Source IP (4 bytes) - the sender's IP address
        self.dst_ip = dst_ip                # Destination IP (4 bytes) - the final destination IP address
        self.ttl = ttl                      # TTL (1 byte) - decremented by each router, discard if 0
        self.protocol = protocol            # Protocol (1 byte) - 17 for UDP
        self.total_length = total_length    # Total length (2 bytes) - header + payload
        self.payload = payload              # Payload (variable length) - typically an L4 segment

# layer 4 segment: ports + length + checksum + type/seq + data
class Segment:
    def __init__(self, src_port, dst_port, length, checksum, seg_type, seq_num, data):
        self.src_port = src_port    # Source port (2 bytes) - the sender's port number (for our purposes, can be a fixed value like 12345)
        self.dst_port = dst_port    # Destination port (2 bytes) - the receiver's port number (for our purposes, can be a fixed value like 80)
        self.length = length        # Length (2 bytes) - header + data
        self.checksum = checksum    # Checksum (2 bytes) - for error detection, can be 0 for simplicity
        self.seg_type = seg_type    # Type (1 byte) - 0 for data, 1 for ACK
        self.seq_num = seq_num      # Sequence number (1 byte) - for rdt2.2, alternates between 0 and 1
        self.data = data            # Data (variable length) - the actual message payload for data segments, empty for ACKs


# simple 16-bit checksum over all the segment fields and data bytes (kept to 2 bytes with & 0xFFFF)
def compute_checksum(src_port, dst_port, length, seg_type, seq_num, data):
    return (src_port + dst_port + length + seg_type + seq_num + sum(data)) & 0xFFFF # simple checksum: sum of all fields and data bytes, modulo 2^16 to fit in 2 bytes

# recompute and compare against the value stored in the segment header
def verify_checksum(segment):
    expected = compute_checksum(segment.src_port, segment.dst_port, segment.length,
                                segment.seg_type, segment.seq_num, segment.data)
    return expected == segment.checksum # recompute the checksum and compare to the value in the segment header
