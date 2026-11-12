---
title: ROS 2 driver (sensor_msgs/Range)
sidebar_label: ROS 2
sidebar_position: 3
description: "Use an ERDI UART laser rangefinder module in ROS 2 with the erdi_lrf_driver package: build from source, launch, parameters and the topic it publishes."
---

:::note Status, checked 2026-11-13
`erdi_lrf_driver` is built from source. It is not in the ROS distribution packages yet: the [rosdistro pull request #55265](https://github.com/ros/rosdistro/pull/55265) is open with changes requested, so `apt install` is not available. The package has tests against a fake serial port but has not been tested with a physical module on a robot.
:::

The package publishes `sensor_msgs/msg/Range` on `/range`, so the module can feed nav2, robot_localization or your own altitude logic. Both ERDI protocol families are supported. LRF10VB is not in this driver's model list yet.

## Install

```bash
cd ~/ros2_ws/src
git clone https://github.com/ErdiTech/erdi_lrf_driver.git
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -y
colcon build --packages-select erdi_lrf_driver
source install/setup.bash
sudo usermod -aG dialout $USER     # then log in again
```

## Run

```bash
ros2 launch erdi_lrf_driver erdi_lrf.launch.py port:=/dev/ttyUSB0 model:=LRF3000A1 rate:=10.0
ros2 topic echo /range
```

## Parameters

| Name | Default | Description |
|---|---|---|
| `port` | `/dev/ttyUSB0` | Serial device |
| `model` | `LRF3000A1` | Exact model name; frame format, unit and default baud come from it |
| `baud` | `0` | 0 means the model's documented default |
| `frame_id` | `erdi_lrf_link` | Header frame |
| `rate` | `10.0` | Polling rate in Hz |
| `min_range`, `max_range` | `0.0` | Metres, 0 takes the model table value |
| `field_of_view` | `0.0` | Radians; for models without a published divergence set it yourself |
| `continuous` | `false` | Stream continuously for polled models |

Out-of-range readings follow REP-117: negative infinity below the minimum, positive infinity beyond the maximum or with no target, NaN for an invalid measurement.

More worked examples: [erdi-lrf-ros2-examples](https://github.com/ErdiTech/erdi-lrf-ros2-examples). Repository: [ErdiTech/erdi_lrf_driver](https://github.com/ErdiTech/erdi_lrf_driver).
