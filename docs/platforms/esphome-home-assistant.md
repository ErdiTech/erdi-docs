---
title: ESPHome and Home Assistant
sidebar_label: ESPHome / Home Assistant
sidebar_position: 4
description: "Read an ERDI UART laser rangefinder module with an ESP32 running ESPHome and show it in Home Assistant as a distance sensor: YAML, options and wiring."
---

:::note Status, checked 2026-11-13
The ESPHome component is an external component pulled from GitHub, no approval needed. Its parser is tested on a host computer. The component has not been compiled and run against a physical module by the maintainers yet, so treat it as Untested.
:::

```yaml
external_components:
  - source: github://ErdiTech/erdi-lrf-home-assistant
    components: [erdi_lrf]

uart:
  id: lrf_uart
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 460800          # 115200 for LR, LRF A1 and SPD1200N models

sensor:
  - platform: erdi_lrf
    uart_id: lrf_uart
    model: LRF22VB
    name: "Laser distance"
    update_interval: 1s
```

Add the node in the ESPHome dashboard. Home Assistant discovers it and shows the distance in metres with the distance device class.

## Options

| Option | Notes |
|---|---|
| `model` | Required. The unit differs by series, so the exact model selects frame format, unit and out-of-range marker. LRF10VB is not in the list yet. |
| `update_interval` | How often the state is published. Polled (family A) modules are requested once per interval. |
| `uart_id` | The UART; a warning is logged if its baud rate does not match the model. |

Out-of-range frames and "no echo" replies publish `unknown`. After three update intervals without a valid frame the sensor also reports `unknown`. Use ESPHome `filters:` (median, sliding window) as usual.

## Wiring

Module TX to the ESP32 RX pin, module RX to the TX pin, common ground, module supply from its own regulator. Check the module's TX level against the 3.3 V GPIO first: [wiring and power](../get-started/wiring-and-power.md). 460800 baud needs a hardware UART; the software UART of an ESP8266 cannot do it.

Repository and tests: [ErdiTech/erdi-lrf-home-assistant](https://github.com/ErdiTech/erdi-lrf-home-assistant).
