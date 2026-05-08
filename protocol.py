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


# ---------------------------------------------------------------------------
# Layer 3: Network (IP-like Packet)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Layer 4: Transport (UDP-like Segment with ACK — rdt2.2)
# ---------------------------------------------------------------------------
