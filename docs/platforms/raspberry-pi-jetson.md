---
title: Python, Raspberry Pi and Jetson
sidebar_label: Python / Raspberry Pi / Jetson
sidebar_position: 6
description: "Read ERDI UART laser rangefinder modules from Python on a PC, Raspberry Pi or Jetson: pip install erdi-lrf, CSV logging, MQTT publishing and a MAVLink bridge."
---

:::note Status, checked 2026-11-13
The Python package `erdi-lrf` (PyPI, MIT) and the Raspberry Pi tools have software tests using a virtual serial port and golden frames from the datasheets. They are Untested against hardware on the [compatibility page](../compatibility/index.mdx). The only real-module evidence is the factory capture of LRF22VB and LRF50H made with the vendor tool, see [units and out-of-range](../protocols/units-and-out-of-range.md).
:::

## erdi-lrf

```bash
pip install erdi-lrf
erdi-lrf models
erdi-lrf --port /dev/ttyUSB0 --model LRF22VB stream --count 20
```

```python
from erdi_lrf import ErdiLRF

with ErdiLRF("/dev/ttyUSB0", "LRF3000A1") as lrf:
    print(lrf.measure().metres)
```

Pass the exact model name. The unit, frame format and default baud rate come from it.

## Raspberry Pi tools

[erdi-lrf-raspberry-pi-python](https://github.com/ErdiTech/erdi-lrf-raspberry-pi-python) adds a serial reader, a CSV logger, an MQTT publisher and a MAVLink bridge:

```bash
pip install "git+https://github.com/ErdiTech/erdi-lrf-raspberry-pi-python"
erdi-lrf-log  --port /dev/serial0 --model LRF22VB --csv log.csv --decimate 20
erdi-lrf-mqtt --port /dev/serial0 --model LRF100H --host 192.168.1.10 --topic erdi_lrf/distance
```

Use `/dev/serial0` for the Raspberry Pi header UART after enabling it, or `/dev/ttyUSB0` for a USB-TTL adapter. The same code runs on a Jetson or any Linux board with a serial port. The MAVLink bridge is described on the [PX4](px4.md) page.

## Related tutorials on erdilrf.com

- [Raspberry Pi tutorial](https://erdilrf.com/knowledge/) and [Jetson tutorial](https://erdilrf.com/knowledge/) in the knowledge base.
