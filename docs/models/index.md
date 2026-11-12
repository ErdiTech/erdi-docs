---
id: index
title: Models with a published protocol
sidebar_label: Models
description: "22 ERDI laser rangefinder module models with a published UART protocol: frame format, baud rate, unit, pinout and code examples."
---

Twenty-two models have a published UART protocol and a page here: 13 in family A and 9 in family B. Every number on these pages comes from the ERDI datasheet for that model. The other models are listed on [Models with protocol on request](./more-models.md).

:::tip Which family?
Family A modules answer 8-byte `55 AA` commands at 115200 baud (you poll them). Family B modules stream `5C` frames at 460800 baud on their own. The unit of the distance field depends on the model, not the family: see [Units and out-of-range](../protocols/units-and-out-of-range.md).
:::

## Family A (55 AA, polled)

| Model | Baud | Frame (bytes) | Wire unit | Range |
|---|---|---|---|---|
| [LR1000E2](./lr1000e2.mdx) | 115200 | 8 | m | 4–1,000 m |
| [LR1000E4](./lr1000e4.mdx) | 115200 | 8 | m | see specification |
| [LR1200E2](./lr1200e2.mdx) | 115200 | 8 | m | 4–1,200 m |
| [LR1200E4](./lr1200e4.mdx) | 115200 | 8 | m | see specification |
| [LRF1200A1](./lrf1200a1.mdx) | 115200 | 8 | m | see specification |
| [SPD1200N0](./spd1200n0.mdx) | 115200 | 8 | m | 0.2–1,200 m |
| [SPD1200N2](./spd1200n2.mdx) | 115200 | 8 | m | 0.2–1,200 m |
| [SPD1200N4](./spd1200n4.mdx) | 115200 | 8 | m | see specification |
| [LR1500E2](./lr1500e2.mdx) | 115200 | 8 | m | 4–1,500 m |
| [LR1500E4](./lr1500e4.mdx) | 115200 | 8 | m | see specification |
| [LR2000E2](./lr2000e2.mdx) | 115200 | 8 | m | 4–2,000 m |
| [LR2000E4](./lr2000e4.mdx) | 115200 | 8 | m | 4–2,000 m |
| [LRF3000A1](./lrf3000a1.mdx) | 115200 | 8 | m | see specification |

## Family B (5C, streaming)

| Model | Baud | Frame (bytes) | Wire unit | Range |
|---|---|---|---|---|
| [LRF10VB](./lrf10vb.mdx) | 460800 | 4 | mm | 0.05–9 m (90% refl.) · 0.05–5 m |
| [LRF22VB](./lrf22vb.mdx) | 460800 | 4 | mm | 0.05–20 m (90% refl.) · 0.05–10 m |
| [LRF50VB](./lrf50vb.mdx) | 460800 | 4 | mm | 0.05–50 m (90% refl.) · 0.05–20 m |
| [LRF50H](./lrf50h.mdx) | 460800 | 4 | cm | 0.05–50 m (90% refl.) · 0.05–15 m |
| [LRF100H](./lrf100h.mdx) | 460800 | 4 | cm | 0.05–100 m (90% refl.) · 0.05–30 m |
| [LRF200H](./lrf200h.mdx) | 460800 | 4 | cm | 0.05–200 m (90% refl.) · 0.05–70 m |
| [LRF300H](./lrf300h.mdx) | 460800 | 4 | cm | 0.05–300 m (90% refl.) · 0.05–100 m |
| [LRF600H](./lrf600h.mdx) | 460800 | 4 | cm | 0.05–600 m (90% refl.) · 0.05–200 m |
| [LRF1500H](./lrf1500h.mdx) | 460800 | 5 | cm | 0.05–1,500 m (90% refl.) · 0.05–300 m |

Wire unit for family A is metres multiplied by 10; the table shows the unit of the physical value (`m`).
