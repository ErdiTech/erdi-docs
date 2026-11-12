# Feeds synthetic ERDI B-family (0x5C, 4-byte, cm) frames into ArduPilot SITL serial2 (tcp:5770).
# Phase 1: 12.34 m for 12 s at 100 Hz; phase 2: out-of-range marker 65535 for 6 s.
import socket, time, sys
def frame(raw):
    lo, hi = raw & 0xFF, (raw >> 8) & 0xFF
    return bytes([0x5C, lo, hi, (~(lo + hi)) & 0xFF])
s = None
for _ in range(60):
    try:
        s = socket.create_connection(("127.0.0.1", 5770), timeout=2); break
    except OSError:
        time.sleep(0.5)
if s is None: sys.exit("feeder: no connection")
t0 = time.time()
while time.time() - t0 < 18:
    raw = 1234 if time.time() - t0 < 12 else 65535
    s.sendall(frame(raw)); time.sleep(0.01)
print("feeder done", flush=True)
