"""Network device implementations: Host and Router.

Each device exposes Layer 2, Layer 3, and (for Hosts) Layer 4 behavior.
A shared logging helper at the top of this module is used by every
layer to keep the output format consistent across the simulator.

Sections:
    - log helper (shared across all layers)
    - Host class (runs L2, L3, L4)
    - Router class (runs L2, L3 only)
"""

# ---------------------------------------------------------------------------
# Shared logging helper
# ---------------------------------------------------------------------------

# Print a single layer-event log line in the format required by the spec.
def log(device, layer, message):
    print(f"{device}: {layer}: {message}")


# Print an empty line to visually separate log groups.
def log_blank():
    print()


# ---------------------------------------------------------------------------
# Host
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
