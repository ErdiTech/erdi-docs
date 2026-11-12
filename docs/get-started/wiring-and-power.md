---
title: Wiring and power
sidebar_position: 2
description: "Wire an ERDI laser rangefinder module to a UART host: cross TX and RX, common ground, supply voltage versus UART logic level, and the supply ranges that differ between series."
---

Every ERDI module in this documentation talks plain UART: TX, RX, ground and a supply pin. The pin order and connector differ by model, so take the pin table from the [model page](../models/index.md).

```text
Module TX  ---->  Host RX
Module RX  <----  Host TX
Module GND ----   Host GND   (one common ground)
Module VCC <----  its own supply, as the datasheet says
```

## Rules that save a day

- **Cross TX and RX.** Module TX goes to host RX. Some datasheets label the pins from the host's point of view; the model pin tables say which.
- **Share ground.** Without a common ground the data is garbage or missing.
- **Supply voltage is not UART logic level.** A module that runs from 5 V may still use 3.3 V signals. Most datasheets list only the supply range. If the logic level is not written for your model, ask before connecting a 3.3 V host. See [UART hardware notes](../guides/uart-hardware-notes.md).
- **Check the supply range for your series.** From the datasheets: LRF10VB runs from 4.5 to 5.5 V DC, LRF22VB from 3.0 to 3.6 V DC, LRF50VB from 3.3 to 5 V, the LR and SPD1200N modules and LRF3000A1 from 3.3 to 5 V, LRF1200A1 from 3.3 V ± 0.1 V. The H series (LRF50H to LRF1500H) needs 9 to 36 V, so power it from its own supply, not from the 5 V pin of a flight controller.
- **Streaming modules need a hardware UART.** Family B runs at 460800 baud. AVR SoftwareSerial cannot reach that. Use a hardware UART or set a lower documented baud rate first.
- **Enable pins.** Several family A modules have an enable pin (active high on the SW-SHOT pin, or power-on at low level on LRF3000A1). The pin tables say which.

## Which UART settings

8 data bits, no parity, 1 stop bit. Baud rate by family: 115200 for family A, 460800 for family B (adjustable by command, see [Family B protocol](../protocols/family-b-5c.md)).

## Power budget

Peak and average current are in the specification table of each model. Size the supply for the peak current, not the average.
