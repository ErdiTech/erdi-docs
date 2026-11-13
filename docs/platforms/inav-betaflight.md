---
title: INAV and Betaflight with an ERDI laser rangefinder
sidebar_label: INAV / Betaflight
sidebar_position: 9
description: "Status of ERDI laser rangefinder modules on INAV and Betaflight: no bridge firmware yet. Working alternatives: ArduPilot with the Lua driver, or a UART to MAVLink bridge on a companion computer."
---

:::caution Status, checked 2026-11-13
There is no ERDI driver or bridge firmware for INAV or Betaflight. Nothing on this page is described as supported by either project.
:::

ERDI modules talk plain UART frames ([family A](../protocols/family-a-55aa.md), [family B](../protocols/family-b-5c.md)). INAV and Betaflight do not parse these frames, and we have not published firmware that translates them into a format either project reads.

## What works today

| Goal | Route | Status |
|---|---|---|
| Altitude hold or terrain following on a fixed-wing or multirotor | Run [ArduPilot with the ERDI Lua driver](./ardupilot.mdx) | Verified in SITL with synthetic frames, no flight test yet |
| Keep a PX4 airframe | [Companion computer sends MAVLink `DISTANCE_SENSOR`](./px4.md) | Software tests only |
| Log or display distance on an INAV or Betaflight craft | Read the module on a companion computer or microcontroller with the [Python](./raspberry-pi-jetson.md) or [Arduino](./arduino-platformio.md) examples and record it there | Uses the published examples, no flight-controller link |

## If you want to build a bridge

A small microcontroller can read the ERDI frame and re-send the distance in a protocol your flight controller accepts. Check your firmware version's own documentation for which rangefinder inputs it supports before you start; this page does not claim that any specific INAV or Betaflight input works with ERDI data.

- Frame formats and checksums: [protocols](../protocols/family-a-55aa.md) and the [checksum tool](../protocols/checksum-tool.mdx).
- Try a module without writing code: [browser serial monitor](../tools/serial-monitor.mdx).
- Tell us what you are building at [erdilrf.com/support](https://erdilrf.com/support/); a bridge with a real user is more likely to be published.
