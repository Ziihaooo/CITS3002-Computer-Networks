"""Mini Internet Protocol Stack Simulator — entry point.

Usage:
    python main.py <message_size_in_bytes>

Example:
    python main.py 100

Builds Host A, Router R1, and Host B according to the topology defined
in config.py, then sends a message of the given size from Host A to
Host B using the simulated L2/L3/L4 stack.
"""
