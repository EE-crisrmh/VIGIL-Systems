# simulation

The repository contains two simulation baselines.

| Baseline | Run or inspect | Coverage |
| --- | --- | --- |
| PX4 SITL hover | `python software/hover_position_test.py --hover 3` | Arms, takes off, holds, logs local north/east/down positions, then lands. Uses the GPS and home-position readiness checks in PX4. |
| Synthetic warehouse patrol | `python software/test_indoor_patrol.py -v` | Exercises zone coverage, simulated position updates, and a thermal alert in a small grid map. Runs with the Python standard library alone. |

See [software setup](../software/README.md) for the SITL prerequisites.

## Recorded samples

- [Position_Test_1.csv](Position_Test_1.csv) contains 300 local position samples. The maximum horizontal displacement from the first recorded position is approximately 0.050 m. This measures movement within the recorded segment.
- [indoor_patrol_test_data.csv](indoor_patrol_test_data.csv) records two visits to each of three zones and one thermal notification in the east zone.

The December 18 simulation gate still needs an optical-flow-only PX4 position-hold run and validation of the Jetson-to-PX4 link. The warehouse test runs independently of PX4 and Gazebo.
