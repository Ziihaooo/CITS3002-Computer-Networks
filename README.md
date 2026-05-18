# CITS3002 Mini Internet Protocol Stack Simulator

A Python simulator for a mini network stack with Layer 2, Layer 3 and Layer 4. Sends a message from Host A to Host B via Router R1.

## How to run

```
python main.py <size>
```

Where size is the message size in bytes.

Examples:

- `python main.py 10` sends a 10-byte message in a single segment
- `python main.py 500` sends a single 500-byte segment
- `python main.py 1500` splits into three 500-byte segments and sends them sequentially

The program uses only the Python standard library, no external dependencies.

## Topology

```
Host A ----L1---- Router R1 ----L2---- Host B
10.0.1.10        10.0.1.1 / 10.0.2.1    10.0.2.20
```

- Network 1 is L1 and uses 10.0.1.0/24
- Network 2 is L2 and uses 10.0.2.0/24

## Files

- `main.py` is the entry point. Builds the devices, wires the peers, and kicks off the send.
- `protocol.py` has the Frame, Packet, and Segment classes for L2, L3, and L4, plus the checksum helpers.
- `devices.py` has the Host and Router classes and all of the L2 to L4 logic.
- `config.py` holds the topology constants like ip addresses, mac addresses, and routing tables.
- `README.md` is this file.

## Group members

- Zi Hao Chan - 24116757
- Utkrista Sen - 24145884
