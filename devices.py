"""Host and Router classes.

Host runs L2/L3/L4, Router runs L2/L3 only.
Shared log helper at the top so every layer prints in the same format.
"""

# ---------------------------------------------------------------------------
# logging helper
# ---------------------------------------------------------------------------

# prints one log line in the format the spec expects
def log(device, layer, message):
    print(f"{device}: {layer}: {message}")


# blank line between sections so the output is easier to read
def log_blank():
    print()


# ---------------------------------------------------------------------------
# Host
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
