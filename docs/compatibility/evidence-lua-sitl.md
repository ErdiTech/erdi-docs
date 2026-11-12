---
title: Evidence, ArduPilot Lua script in SITL
sidebar_label: Evidence, Lua in SITL
sidebar_position: 2
description: "Logs and setup of the ArduPilot SITL run that decodes ERDI family B centimetre frames through the Lua scripting rangefinder backend."
---

This page is the evidence behind the **Verified (SITL)** cells of the [compatibility matrix](index.mdx). Run date 2026-11-13.

## What was run

- ArduPilot SITL (arducopter), built from the pull request branch `pr-rangefinder-erdi`, head `8ce00e7`, based on ArduPilot master commit `802db19de`. Build info: [build-info.txt](pathname:///docs/evidence/lua-sitl/build-info.txt).
- Parameters: [erdi.parm](pathname:///docs/evidence/lua-sitl/erdi.parm) (`SCR_ENABLE 1`, `SCR_HEAP_SIZE 200000`, `SERIAL2_PROTOCOL 28`, `RNGFND1_TYPE 36`, `RNGFND1_MIN 0.05`, `RNGFND1_MAX 50`, `RNGFND1_ORIENT 25`).
- Script: `erdi_lrf.lua` from [ErdiTech/erdi-lrf-pixhawk-ardupilot](https://github.com/ErdiTech/erdi-lrf-pixhawk-ardupilot), unmodified, default script parameters (family B, 4-byte frame, centimetres, out-of-range marker 65535).
- Feeder: [lua_sitl_feeder.py](pathname:///docs/evidence/lua-sitl/lua_sitl_feeder.py) sends **synthetic** `5C` frames to the SITL serial port at 100 Hz: 1234 cm for 12 s, then the marker 65535 for 6 s, then stops. [lua_sitl_smoke.sh](pathname:///docs/evidence/lua-sitl/lua_sitl_smoke.sh) runs the whole test.

## Result

[reader.log](pathname:///docs/evidence/lua-sitl/reader.log), lines that matter:

```text
[ 11.0] DISTANCE_SENSOR: 1234
[ 23.0] DISTANCE_SENSOR: 5100
[ 29.5] STATUSTEXT: PreArm: Rangefinder 1: No Data
counts {'DISTANCE_SENSOR': 184}
```

- 1234 cm in, 1234 cm out.
- The out-of-range marker became 5100 cm, which is `RNGFND1_MAX` plus 1 m: the backend's out-of-range-high value.
- After the stream stopped, the rangefinder was reported as having no data.
- No Lua errors in the run.

Raw logs: [sitl.log](pathname:///docs/evidence/lua-sitl/sitl.log), [feeder.log](pathname:///docs/evidence/lua-sitl/feeder.log).

## What this does not show

- No physical module and no physical flight controller were involved.
- The millimetre frames of the VB series, the 5-byte LRF1500H frame and family A polling were not run.
- CPU and memory use over a long run were not measured.
