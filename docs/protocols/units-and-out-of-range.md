---
title: Units and out-of-range markers
sidebar_position: 3
description: "The distance unit of ERDI laser rangefinder frames depends on the model, not the protocol family. Table of wire units and out-of-range markers for the 22 documented models."
---

The same bytes mean different distances on different models. `5C 02 11 EC` is 4354 counts. On an LRF22VB a count is one millimetre, so that is 4.354 m. On an LRF100H a count is one centimetre, so that is 43.54 m. Guessing the unit from the family is a tenfold error.

| Series | Family | Wire unit | Notes |
|---|---|---|---|
| VB (LRF10VB, LRF22VB, LRF50VB) | B | millimetres | 2-byte distance, little-endian |
| H (LRF50H, 100H, 200H, 300H, 600H) | B | centimetres | 2-byte distance, little-endian |
| LRF1500H | B | centimetres | 3-byte distance, 5-byte frame |
| LR, LRF A1, SPD1200N | A | metres x 10 | 16-bit value, high byte first |

## Out-of-range markers (family B)

When no valid target is found, a family B module outputs a fixed marker instead of a distance. Treat the marker as no target.

| Model | Marker |
|---|---|
| LRF10VB | 65535 |
| LRF22VB | 20000 |
| LRF50VB | 50000 |
| LRF50H, LRF100H, LRF200H, LRF300H, LRF600H | 65535 |
| LRF1500H | 16777215 |

## Family A status byte

A family A reply carries a status byte (`STA`). `STA = 1` means the measurement succeeded, any other value means it failed and the distance field is not valid.

## Verify it yourself

The [serial monitor](../tools/serial-monitor.mdx) applies these rules from the model table, and its source and tests are in the [erdi-docs repository](https://github.com/ErdiTech/erdi-docs). A bench capture on a real LRF22VB and LRF50H at a 1.9 m wall confirms the units: the VB module logs about 1709 (mm) and the H module about 196 (cm). See the [capture notes](https://github.com/ErdiTech/erdi-lrf-drivers/tree/main/docs/evidence/ardupilot-bench-20261105).
