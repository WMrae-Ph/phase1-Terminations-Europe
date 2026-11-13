"""Optional offline mode for a full re-run without any new download.

Set the environment variable PHASE1_OFFLINE=1 before executing the notebooks. Every network
connection then raises an error, so a re-run can only use the raw data already saved in
data/raw/. Without the variable nothing changes (normal behaviour, downloads allowed).
"""
import os
import socket

OFFLINE = os.environ.get("PHASE1_OFFLINE") == "1"


def activate():
    """Block all network connections if PHASE1_OFFLINE=1; returns True when offline."""
    if OFFLINE:
        def _blocked(*args, **kwargs):
            raise RuntimeError("PHASE1_OFFLINE=1: network access is blocked in this run")
        socket.socket.connect = _blocked
        socket.create_connection = _blocked
        print("OFFLINE run: network access blocked – only saved raw data are used.")
    return OFFLINE
