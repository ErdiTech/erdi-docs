---
title: Arduino and PlatformIO
sidebar_label: Arduino / PlatformIO
sidebar_position: 5
description: "ErdiLRF Arduino library for ERDI UART laser rangefinder modules: install from the Library Manager, PlatformIO or Git, wiring and a first sketch."
---

:::note Status, checked 2026-11-13
The library has host-side tests of the frame parsing. A library entry for a model is not a hardware-compatibility guarantee, so every model is Untested on the [compatibility page](../compatibility/index.mdx). LRF10VB is not in the library yet.
:::

## Install

- **Arduino IDE or Arduino CLI:** search for `ErdiLRF` in the Library Manager. If your local index is out of date, refresh it or install from Git.
- **From Git:** `arduino-cli lib install --git-url https://github.com/ErdiTech/ErdiLRF`
- **PlatformIO**, in `platformio.ini`:

```ini
lib_deps =
    erdi-tech/ErdiLRF
```

## First sketch

```cpp
#include <ErdiLRF.h>

ErdiLRF lrf(Serial1, ERDI_LRF3000A1);

void setup() {
  Serial.begin(115200);
  Serial1.begin(erdiDefaultBaud(ERDI_LRF3000A1));   // ESP32: Serial1.begin(baud, SERIAL_8N1, RX_PIN, TX_PIN)
  lrf.setTimeout(1000);
}

void loop() {
  ErdiMeasurement m;
  if (lrf.measure(&m) == ERDI_OK) {
    Serial.println(m.metres, 3);
  }
  delay(200);
}
```

Change the model constant to yours (`ERDI_LRF22VB`, `ERDI_LRF100H` and so on). The baud rate comes from the model table.

## Notes

- Family B modules run at 460800 baud and need a hardware UART. AVR SoftwareSerial cannot reach that rate.
- Cross TX and RX, share ground, power the module from its own supply: [wiring and power](../get-started/wiring-and-power.md).
- Repository: [ErdiTech/ErdiLRF](https://github.com/ErdiTech/ErdiLRF). Examples: BasicMeasure and ContinuousStream.
