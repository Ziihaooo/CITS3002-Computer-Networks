"""Protocol header definitions for Layers 2, 3, and 4.

This module defines the data classes used to represent each layer's
header and payload. The classes are intentionally simple data holders;
all encapsulation/decapsulation logic lives in devices.py.

Sections:
    - Layer 2: Ethernet-like frame
    - Layer 3: IP-like packet
    - Layer 4: UDP-like segment with ACK support (rdt2.2)
"""

# ---------------------------------------------------------------------------
# Layer 2: Data Link (Ethernet-like Frame)
# ---------------------------------------------------------------------------

# Ethernet-like frame: MAC addressing + type field + L3 packet payload.
class Frame:
    def __init__(self, dst_mac, src_mac, eth_type, payload):
        self.dst_mac = dst_mac      # destination MAC address (string)
        self.src_mac = src_mac      # source MAC address (string)
        self.eth_type = eth_type    # 0x0800 for IPv4
        self.payload = payload      # the Layer 3 packet


# ---------------------------------------------------------------------------
# Layer 3: Network (IP-like Packet)
# ---------------------------------------------------------------------------

# IP-like packet: source/destination IP + TTL + protocol + L4 segment payload.
class Packet:
    def __init__(self, src_ip, dst_ip, ttl, protocol, total_length, payload):
        self.src_ip = src_ip                # source IP address (string)
        self.dst_ip = dst_ip                # destination IP address (string)
        self.ttl = ttl                      # decremented at each router
        self.protocol = protocol            # 17 = UDP
        self.total_length = total_length    # header + payload size in bytes
        self.payload = payload              # the Layer 4 segment


# ---------------------------------------------------------------------------
# Layer 4: Transport (UDP-like Segment with ACK — rdt2.2)
# ---------------------------------------------------------------------------

# UDP-like segment: ports + length + checksum + rdt2.2 type/seq + app data.
class Segment:
    def __init__(self, src_port, dst_port, length, checksum, seg_type, seq_num, data):
        self.src_port = src_port    # source port (e.g. 5000)
        self.dst_port = dst_port    # destination port (e.g. 80)
        self.length = length        # header + data size in bytes
        self.checksum = checksum    # computed for error detection
        self.seg_type = seg_type    # 0 = DATA, 1 = ACK
        self.seq_num = seq_num      # 0 or 1 (alternating bit)
        self.data = data            # application bytes (empty for ACK)
