---
title: PX4 laser rangefinder (MAVLink bridge)
sidebar_label: PX4
sidebar_position: 2
description: "ERDI laser rangefinder modules with PX4: there is no native PX4 driver, so use a companion computer that sends MAVLink DISTANCE_SENSOR. Limits and status."
---

:::caution Status, checked 2026-11-13
There is no ERDI driver in PX4 and none is submitted. Nothing on this page is described as supported by PX4. The bridge below has software tests but no flight-controller test yet.
:::

PX4 accepts rangefinder data as MAVLink `DISTANCE_SENSOR` messages. A companion computer that reads the ERDI module and sends those messages therefore works without any PX4 driver.

## Bridge with erdi-lrf-raspberry-pi-python

The [erdi-lrf-raspberry-pi-python](https://github.com/ErdiTech/erdi-lrf-raspberry-pi-python) project includes `erdi-lrf-mavlink`:

```bash
pip install "erdi-lrf-pi[mavlink] @ git+https://github.com/ErdiTech/erdi-lrf-raspberry-pi-python"
erdi-lrf-mavlink --port /dev/serial0 --model LRF22VB --mav udpout:127.0.0.1:14550
```

It sends `DISTANCE_SENSOR` in centimetres, laser type, downward orientation by default, with the model's published minimum and maximum range. Point it at the MAVLink endpoint of your flight controller connection.

## Limits

- `DISTANCE_SENSOR` carries distance as a 16-bit centimetre value, so the largest value is about 655 m. Longer-range modules cannot report beyond that through this message.
- The companion computer adds latency and one more thing that can fail. Test the link before flight.
- The H series modules need 9 to 36 V; see [wiring and power](../get-started/wiring-and-power.md).

## INAV and Betaflight

There is no ERDI driver for INAV or Betaflight and no bridge firmware yet. The alternatives (ArduPilot Lua driver, or a companion computer bridge) are on the [INAV and Betaflight page](./inav-betaflight.md).
