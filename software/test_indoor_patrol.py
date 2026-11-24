"""Exercise a GPS-free patrol with simulated LiDAR, optical flow, and thermal inputs.

Run: python software/test_indoor_patrol.py
The prototype parts list in the root README names an RPLIDAR A1-class
2D scanner. The custom flight controller BOM covers the PCB only.
This test models a horizontal scan and uses a small known warehouse map.
"""

import argparse
import csv
import math
import random
import sys
import unittest
from collections import deque

MAP = (
    "#########",
    "#...#...#",
    "#.......#",
    "#...#...#",
    "#########",
)
ZONES = {"west": (1, 1), "east": (7, 1), "south": (4, 2)}
DIRECTIONS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def add(cell, offset):
    return cell[0] + offset[0], cell[1] + offset[1]


def is_open(cell):
    x, y = cell
    return 0 <= y < len(MAP) and 0 <= x < len(MAP[y]) and MAP[y][x] == "."


def lidar_scan(cell):
    """Return wall distances along four cardinal bearings from a 2D scan."""
    distances = []
    for direction in DIRECTIONS:
        distance = 1
        cursor = add(cell, direction)
        while is_open(cursor):
            distance += 1
            cursor = add(cursor, direction)
        distances.append(distance)
    return tuple(distances)


def localize(previous, flow_radians, height_m, scan):
    """Predict planar motion from optical flow, then check against the map."""
    prediction = tuple(
        coordinate + angle * height_m
        for coordinate, angle in zip(previous, flow_radians)
    )
    candidates = [
        (x, y)
        for y, row in enumerate(MAP)
        for x in range(len(row))
        if is_open((x, y))
        and math.dist(prediction, (x, y)) <= 1
        and lidar_scan((x, y)) == scan
    ]
    if not candidates:
        raise ValueError("LiDAR scan does not match the optical-flow prediction")
    candidates.sort(key=lambda cell: math.dist(prediction, cell))
    if len(candidates) > 1 and math.isclose(
        math.dist(prediction, candidates[0]), math.dist(prediction, candidates[1])
    ):
        raise ValueError("Ambiguous position")
    return candidates[0]


def next_step(start, goal):
    """Find the first step of a shortest route through free cells."""
    queue = deque([(start, start)])
    seen = {start}
    while queue:
        cell, first = queue.popleft()
        if cell == goal:
            return first
        for direction in DIRECTIONS:
            neighbor = add(cell, direction)
            if neighbor not in seen and is_open(neighbor):
                seen.add(neighbor)
                queue.append((neighbor, neighbor if cell == start else first))
    raise ValueError(f"Unreachable patrol waypoint: {goal}")


def choose_zone(pending, last_visited, tick, rng):
    zones = sorted(pending)
    weights = [tick - last_visited.get(zone, -1) + 1 for zone in zones]
    return rng.choices(zones, weights=weights, k=1)[0]


def person_candidate(frame):
    """Flag a warm region in a synthetic thermal frame."""
    background = sorted(frame)[len(frame) // 2]
    return sum(pixel >= background + 5 for pixel in frame) >= 3


def patrol(observe, rounds, notify, rng):
    position = (1, 1)
    last_visited = {}
    reported = set()
    visited = []
    for _ in range(rounds):
        pending = set(ZONES)
        while pending:
            zone = choose_zone(pending, last_visited, len(visited), rng)
            goal = ZONES[zone]
            while position != goal:
                step = next_step(position, goal)
                flow, height, scan, _ = observe(step)
                position = localize(position, flow, height, scan)
                if position != step:
                    raise ValueError("Drone did not reach the commanded cell")
            _, _, _, frame = observe(position)
            if person_candidate(frame) and zone not in reported:
                notify({"zone": zone, "position_m": position, "thermal_frame": frame})
                reported.add(zone)
            pending.remove(zone)
            last_visited[zone] = len(visited)
            visited.append(zone)
    return visited


class Warehouse:
    """Generate repeatable sensor readings for a stationary person in east."""

    def __init__(self):
        self.position = (1, 1)

    def observe(self, target):
        if not is_open(target) or math.dist(self.position, target) > 1:
            raise ValueError(f"Unsafe simulated step: {target}")
        height_m = 2.0
        # Model a small flow bias so map matching must correct the prediction.
        flow = tuple(
            (new - old) / height_m + 0.1
            for old, new in zip(self.position, target)
        )
        self.position = target
        frame = (21,) * 13 + (32, 33, 32) if target == ZONES["east"] else (21,) * 16
        return flow, height_m, lidar_scan(target), frame


class IndoorPatrolTest(unittest.TestCase):
    def test_patrol_covers_each_zone_and_alerts_once(self):
        for seed in range(8):
            with self.subTest(seed=seed):
                alerts = []
                visited = patrol(Warehouse().observe, 2, alerts.append, random.Random(seed))
                self.assertCountEqual(visited[:len(ZONES)], ZONES.keys())
                self.assertCountEqual(visited[len(ZONES):], ZONES.keys())
                self.assertEqual([alert["zone"] for alert in alerts], ["east"])
                self.assertEqual(alerts[0]["position_m"], ZONES["east"])
                self.assertTrue(person_candidate(alerts[0]["thermal_frame"]))

    def test_inconsistent_scan_stops_localization(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            localize((1, 1), (0, 0), 2.0, (99, 99, 99, 99))

    def test_thermal_filter_ignores_an_isolated_hot_pixel(self):
        self.assertFalse(person_candidate((21,) * 15 + (33,)))


def run_demo(csv_output=None):
    warehouse = Warehouse()
    zone_visits = []
    print("Warehouse map (# = wall, W/E/S = patrol zones)")
    zone_markers = {cell: zone[0].upper() for zone, cell in ZONES.items()}
    for y, row in enumerate(MAP):
        print("".join(zone_markers.get((x, y), tile) for x, tile in enumerate(row)))
    print("Coordinates are (x, y) from the upper-left corner.")
    print()

    def observe(target):
        staying_in_place = target == warehouse.position
        flow, height, scan, frame = warehouse.observe(target)
        if staying_in_place:
            zone = next(zone for zone, cell in ZONES.items() if cell == target)
            candidate = person_candidate(frame)
            peak = max(frame)
            outcome = "person candidate" if candidate else "clear"
            print(f"  Scan {zone}: thermal peak {peak} C, {outcome}")
            east, west, south, north = scan
            zone_visits.append({
                "round": len(zone_visits) // len(ZONES) + 1,
                "zone": zone,
                "x": target[0],
                "y": target[1],
                "lidar_east_cells": east,
                "lidar_west_cells": west,
                "lidar_south_cells": south,
                "lidar_north_cells": north,
                "thermal_peak_c": peak,
                "person_candidate": candidate,
                "alert_sent": False,
            })
        else:
            print(f"Move to {target}: LiDAR wall distances E/W/S/N = {scan} cells")
        return flow, height, scan, frame

    def notify(alert):
        zone_visits[-1]["alert_sent"] = True
        print(f"  ALERT: possible person in {alert['zone']} at {alert['position_m']}")

    rounds = 2
    visited = patrol(observe, rounds, notify, random.Random(0))
    for round_index in range(rounds):
        first = round_index * len(ZONES)
        route = " -> ".join(visited[first:first + len(ZONES)])
        print(f"Round {round_index + 1}: {route}")


    if csv_output is not None:
        with open(csv_output, "w", newline="", encoding="utf-8") as output:
            writer = csv.DictWriter(output, fieldnames=list(zone_visits[0]))
            writer.writeheader()
            writer.writerows(zone_visits)
        print(f"Saved {len(zone_visits)} zone visits to {csv_output}")


if __name__ == "__main__":
    if "--demo" in sys.argv[1:]:
        parser = argparse.ArgumentParser(description="Run the warehouse patrol demo.")
        parser.add_argument("--demo", action="store_true", help="run the simulation")
        parser.add_argument("--csv-output", help="write zone visits to this CSV path")
        args = parser.parse_args()
        run_demo(args.csv_output)
    else:
        unittest.main()
