---
title: STM32 (HAL, circular DMA)
sidebar_label: STM32
sidebar_position: 7
description: "STM32 HAL driver for ERDI UART laser rangefinder modules using circular DMA, so 460800 baud streams need no per-byte interrupt."
---

:::note Status, checked 2026-11-13
The parser is tested on a host computer and the example firmware builds in CI. It has not been run on a bench with a live module by the maintainers yet. Check baud-rate accuracy on your clock tree.
:::

```c
#include "erdi_lrf_hal.h"

static erdi_hal_t lrf;
/* configure the UART as 8N1 at erdi_hal_baud("LRF22VB") and its RX DMA as circular, byte-wide */
erdi_hal_start(&lrf, &huart6, "LRF22VB");

for (;;) {
  erdi_measurement_t m;
  if (erdi_hal_poll(&lrf, &m) && !m.out_of_range) {
    use_distance(m.metres);
  }
}
```

Polled models (family A): call `erdi_hal_request(&lrf)` at your rate, then `erdi_hal_poll()`. Poll at least every `ERDI_HAL_DMA_BUF / (baud / 10)` seconds: 128 bytes at 460800 baud is about 2.8 ms of data.

Wiring: module TX to the UART RX pin, module RX to TX, common ground, own supply. Check the module's TX level against 3.3 V: [wiring and power](../get-started/wiring-and-power.md).

Repository: [ErdiTech/erdi-lrf-stm32-hal](https://github.com/ErdiTech/erdi-lrf-stm32-hal), with a complete PlatformIO example for a Nucleo F411RE.
