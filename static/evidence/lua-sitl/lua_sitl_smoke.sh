#!/bin/bash
# Lua rangefinder smoke test in ArduPilot SITL (local only). Usage: bash lua_sitl_smoke.sh <dir-with-lua-and-py>
set -u
SRC="$1"; W=/tmp/erdi-lua-sitl; rm -rf $W; mkdir -p $W/scripts; cd $W
cp "$SRC/erdi_lrf.from-github-20261113.lua" scripts/erdi_lrf.lua
cat > erdi.parm <<P
SCR_ENABLE 1
SCR_HEAP_SIZE 200000
SERIAL2_PROTOCOL 28
RNGFND1_TYPE 36
RNGFND1_MIN 0.05
RNGFND1_MAX 50
RNGFND1_ORIENT 25
P
source ~/venv-ap/bin/activate
AP=~/ap/ardupilot
timeout 75 $AP/build/sitl/bin/arducopter --model quad --speedup 1 -I0 --defaults $AP/Tools/autotest/default_params/copter.parm,erdi.parm --serial2=tcp:5770 > sitl.log 2>&1 &
sleep 2
timeout 70 python3 "$SRC/lua_sitl_reader.py" > reader.log 2>&1 &
RP=$!
sleep 12
timeout 40 python3 "$SRC/lua_sitl_feeder.py" > feeder.log 2>&1
wait $RP
echo "=== reader"; cat reader.log | tail -40; echo "=== feeder"; cat feeder.log; echo "=== sitl tail"; tail -15 sitl.log
pkill -f "build/sitl/bin/arducopter" 2>/dev/null; true
