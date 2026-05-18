# CITS3002 Project - Design Document

**Mini Internet Protocol Stack Simulator**

Group members:

- ZI HAO CHAN - 24116757
- Utkrista Sen - 24145884

---

## 1. Overview

This project is a Python simulator of a small network stack with three layers - the Data Link Layer (L2), the Network Layer (L3), and the Transport Layer (L4). The topology is two hosts connected through one router. The simulator sends a message from Host A to Host B and prints a log line for every layer event so the flow of data is visible.

The implementation is a logical simulation only. No real sockets are used. Devices talk to each other through in-process method calls instead of any networking library. Only the Python standard library is used, with `sys` for reading the command line argument.

## 2. File organisation

The submission follows the file layout required by the spec.

| File | Purpose |
|------|---------|
| `main.py` | Entry point. Reads the message size from the command line, builds the three devices from the constants in `config.py`, wires the peer references between devices to simulate the physical links, and calls `host_a.send_message` to kick off the send. |
| `protocol.py` | Contains the three header classes - `Frame` for L2, `Packet` for L3, and `Segment` for L4. Each class is a simple data holder. Also contains `compute_checksum` and `verify_checksum`, the helper functions used by L4. |
| `devices.py` | Contains the `Host` and `Router` classes which hold all of the L2 to L4 behaviour. Also contains the shared `log` function used by every layer and two L3 helpers, `ip_in_network` and `routing_lookup`. |
| `config.py` | Holds the static topology, the four ip addresses, four mac addresses, three routing tables, four mac tables, and the protocol constants like `MAX_SEGMENT_DATA` and `INITIAL_TTL`. |
| `README.md` | Brief description and how to run. |

## 3. Topology

```
Host A ----L1---- Router R1 ----L2---- Host B
10.0.1.10        10.0.1.1 / 10.0.2.1    10.0.2.20
```

- Network 1 is L1 and uses 10.0.1.0/24
- Network 2 is L2 and uses 10.0.2.0/24

The four ip and mac addresses are taken directly from the spec.

## 4. Design choices

### 4.1 Encapsulation

The three layers are stacked through Python object references. The payload field of each outer object holds the inner object.

```
Frame.payload  = Packet
Packet.payload = Segment
Segment.data   = application bytes
```

This avoids any need to pack bytes manually. On send, each layer constructs the next-larger object. On receive, each layer reads its own fields and hands the payload up.

### 4.2 Inter-device transport

Since `socket` is not allowed, devices exchange frames through direct method calls. Each device holds a reference to the other end of its link in `self.peer`. When a frame is sent, the sender calls `self.peer.receive_frame(frame, ...)` and that call is the transmission itself. The Router stores its peers inside its `interfaces` dict so that each interface has its own peer reference and outgoing mac information.

This choice keeps the simulator fully synchronous and deterministic. When a sender calls `send_packet`, by the time the call returns, the full round trip including the ACK has already happened. That makes the alternating-bit sender logic very simple.

### 4.3 Routing table structure

Each node has a routing table which is a list of tuples in the form `(network, prefix_length, next_hop_ip, outgoing_interface)`. A list of tuples is used because routing tables conceptually need order and a fixed shape per entry. If `next_hop_ip` is `None` the destination network is directly connected, and the L3 routing function then uses the packet's destination ip as the next-hop, matching the spec wording that says "the next-hop IP is set to the destination IP itself" when the destination is on a directly connected network.

Both hosts have their own routing tables in addition to R1, since the spec states that each node must maintain a routing table.

### 4.4 Mac tables and mac learning

Each node has a static mac table that maps next-hop ip to mac. This table is preloaded from `config.py` and used by L2 when an outgoing frame is being built.

In addition to the static table, the Router maintains a learning table that maps source mac to ingress interface. The learning table starts empty and is populated as frames arrive. This satisfies the spec requirement to "learn the incoming source MAC address from received frames" and produces the log line "Source MAC learned: ... on Interface N". In the simulator the learned values are not used for forwarding decisions, since forwarding is driven by L3 routing, but the behaviour and the log line are present as the spec requires.

### 4.5 TTL handling

Outgoing packets are built with TTL of 100 from the spec. The router decrements TTL by 1 on every transit. If TTL reaches 0 after the decrement, the router drops the packet, prints a drop log line, and does not forward. The drop path has been tested by temporarily setting `INITIAL_TTL` to 1 and observing the drop fire correctly.

### 4.6 Checksum

The L4 checksum is a simple 16-bit sum over all of the segment header fields and every byte of the data, masked with `& 0xFFFF` so the result fits in 2 bytes. The spec only specifies that a checksum field is required and that the receiver must verify it and discard corrupted segments. The spec does not mandate the algorithm. A simple byte sum is sufficient because the simulator is deterministic and no corruption is introduced. The verify function recomputes the same sum and compares it against the stored checksum.

### 4.7 Alternating-bit reliable transfer

The L4 sender alternates between sequence number 0 and 1 for each new DATA segment. After calling `send_packet`, by the time the call returns the ACK has been processed in `receive_segment` and `self.last_ack_seq` has been set. If `last_ack_seq` matches the sent seq, the sender flips the bit and moves to the next chunk. If it does not match, the sender prints the retransmit log line and tries again. The receiver acknowledges with whatever seq it just saw, so a fresh segment gets a new ack and a duplicate segment gets the previous ack again, which matches the spec's alternating-bit protocol description.

### 4.8 Segmentation

Messages larger than 500 bytes are split into chunks of `MAX_SEGMENT_DATA` bytes which is 500. Each chunk is sent as its own segment under alternating-bit. For a 1500 byte message three segments are sent with seq 0, 1, and 0. This matches what the spec asks for when the input exceeds the per-segment limit.

## 5. Logging

A single helper `log(device, layer, message)` prints every log line in the format the spec expects. Every layer event on every device goes through this helper so the format stays consistent across the whole trace. Blank lines are printed between layer sections to match the visual grouping in the spec example.

## 6. Testing

The simulator has been tested at the following message sizes.

| Size | Result |
|------|--------|
| 0 | "Data size=0" logged, no segments sent |
| 1 | one DATA segment, single round trip |
| 10 | matches the spec example log line by line |
| 500 | one DATA segment at the boundary, no split |
| 501 | two segments with seq 0 then seq 1 |
| 1500 | three segments with seq 0, 1, 0 |

The TTL drop path was also tested by setting the initial TTL to 1 and observing the router decrement to 0 and drop the packet with the expected log line.
