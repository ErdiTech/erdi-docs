---
title: First reading with a USB-TTL adapter
sidebar_position: 3
description: "Get the first distance reading from an ERDI laser rangefinder module with a USB to TTL adapter: pip install erdi-lrf, one command, or the browser serial monitor."
---

You need a module, a USB-TTL adapter whose logic level matches the module (check [wiring and power](wiring-and-power.md)), and a supply for the module.

## Option 1: the browser serial monitor

Open the [serial monitor](../tools/serial-monitor.mdx) in Chrome or Edge on a desktop computer, pick the model, press Connect serial port. You get the distance, a live chart and a CSV export. Nothing is installed and nothing leaves your computer.

## Option 2: Python

```bash
pip install erdi-lrf
erdi-lrf models                                    # list the models and their defaults
erdi-lrf --port COM3 --model LRF22VB stream --count 20      # streaming modules (family B)
erdi-lrf --port COM3 --model LRF3000A1 measure              # polled modules (family A)
```

Use `/dev/ttyUSB0` instead of `COM3` on Linux. In code:

```python
from erdi_lrf import ErdiLRF

with ErdiLRF("COM3", "LRF22VB") as lrf:
    for r in lrf.stream():
        print("out of range" if r.out_of_range else f"{r.metres:.3f} m")
```

The package takes the baud rate, frame length and unit from the model name, so use the exact model.

## If nothing arrives

1. Swap TX and RX.
2. Check the baud rate against the model page.
3. Measure the supply at the module while it is running; a weak supply resets the module.
4. For family B, remember that frames start on their own. For family A, nothing arrives until you send a command.
5. Work through [field troubleshooting](../guides/field-troubleshooting.md).
