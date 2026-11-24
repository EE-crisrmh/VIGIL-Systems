# software

This directory contains Python prototypes for PX4 SITL and a synthetic indoor patrol test. The planned companion computer is the Jetson Orin Nano Super, with ROS 2 for mapping, localization, patrol logic, perception, and guard alerts.

## Run the synthetic patrol test

From the repository root:

```sh
python software/test_indoor_patrol.py -v
```

## Watch the synthetic warehouse patrol

From the repository root, run this with Python 3.8 or later. No packages are required.

```sh
python software/test_indoor_patrol.py --demo
```

The demo prints a warehouse grid and patrols three zones twice using a fixed random seed. The route goes around walls. A simulated LiDAR scan reports distances to walls in four directions, and simulated optical flow predicts the next position. At each zone, the patrol checks a synthetic thermal frame and reports a warm cluster in the east zone once. The thermal threshold is a stand-in for person detection.

To export one row per zone visit, including the four LiDAR wall distances, the thermal peak, and whether the patrol sent an alert:

```sh
python software/test_indoor_patrol.py --demo --csv-output patrol_results.csv
```

This writes or replaces `patrol_results.csv` in the current directory.

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
