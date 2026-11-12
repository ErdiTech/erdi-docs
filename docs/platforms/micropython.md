---
title: MicroPython (ESP32, RP2040)
sidebar_label: MicroPython
sidebar_position: 8
description: "Single-file MicroPython driver for ERDI UART laser rangefinder modules on ESP32, Raspberry Pi Pico and STM32 boards."
---

:::note Status, checked 2026-11-13
The frame parsing is unit-tested under CPython with the datasheet frames. It has not been run on a board with a live module by the maintainers, so it is Untested.
:::

Install on the board with Wi-Fi up, or copy the file with `mpremote`:

```python
import mip
mip.install("github:ErdiTech/erdi-lrf-esp32-micropython")
```

Streaming module (family B):

```python
from erdi_lrf import open_uart
lrf = open_uart("LRF22VB", uart_id=2, tx=17, rx=16)   # baud picked from the model table
print(lrf.read_latest())                               # metres, or None if out of range
```

Polled module (family A):

```python
lrf = open_uart("LRF3000A1")
print(lrf.measure())                # metres, None with no valid echo, OSError on timeout
```

Wiring on an ESP32 (UART2): module TX to GPIO16, module RX to GPIO17, common ground, own supply. Supply voltage is not UART voltage, use a level shifter if they differ: [wiring and power](../get-started/wiring-and-power.md).

Repository: [ErdiTech/erdi-lrf-esp32-micropython](https://github.com/ErdiTech/erdi-lrf-esp32-micropython), single file `erdi_lrf.py` with examples for ESP32 and RP2040.
