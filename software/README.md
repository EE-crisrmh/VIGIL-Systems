# software

This directory contains Python prototypes for PX4 SITL and a synthetic indoor patrol test. The planned companion computer is the Jetson Orin Nano Super, with ROS 2 for mapping, localization, patrol logic, perception, and guard alerts.

## Run the synthetic patrol test

From the repository root:

```sh
python software/test_indoor_patrol.py -v
```

## Run the PX4 SITL hover test

In Ubuntu or WSL, install the Python dependency with `python -m pip install mavsdk-grpc`. In a separate terminal, start the simulator from the PX4-Autopilot checkout:

```sh
make px4_sitl gz_x500
```

Run these commands from the VIGIL repository root in the same environment:

```sh
python software/hover_position_test.py --check-connection
python software/hover_position_test.py --hover 3
```

The connection check waits for position telemetry without sending flight commands. The hover run uses PX4 SITL on UDP port 14540 by default and writes a timestamped CSV in the current directory. `software/Protoype.py` is the earlier takeoff, hover, and landing script. Use the flight scripts with the simulator.

See [simulation baselines and data](../simulation/README.md).
