"""PX4 SITL: take off, hover for three seconds, land, and show telemetry.

Install: python -m pip install mavsdk-grpc
Start PX4 with Gazebo in the PX4-Autopilot directory (Ubuntu/WSL):
    make px4_sitl gz_x500
Run this script in the same environment:
    python Protoype.py --hover 3

PX4 sends MAVLink to UDP port 14540 for MAVSDK by default. If running this
script on Windows separately from WSL, configure PX4's MAVLink destination
to the Windows host IP. Use this script only with the PX4 simulator.
"""

import argparse
import asyncio
import contextlib
import csv
from datetime import datetime
from mavsdk_grpc import System


async def wait_for(stream, predicate, timeout, description):
    async def watch():
        async for value in stream:
            if predicate(value):
                return value
        raise RuntimeError(f"Telemetry ended while waiting for {description}")

    try:
        return await asyncio.wait_for(watch(), timeout)
    except asyncio.TimeoutError as exc:
        raise RuntimeError(f"Timed out waiting for {description}") from exc


async def collect(stream, state, name, format_value):
    async for value in stream:
        state[name] = format_value(value)


async def print_telemetry(state):
    while True:
        print(" | ".join(f"{key}: {value}" for key, value in state.items()), flush=True)
        await asyncio.sleep(1)


async def print_status(drone):
    async for message in drone.telemetry.status_text():
        print(f"[Autopilot] {message.text}", flush=True)


async def land_and_wait(drone):
    print("Landing...")
    await asyncio.wait_for(drone.action.land(), 15)
    await wait_for(drone.telemetry.in_air(), lambda airborne: not airborne,
                   120, "touchdown")
    await wait_for(drone.telemetry.armed(), lambda armed: not armed,
                   30, "automatic disarming")
    print("Landed and disarmed.")

async def log_hover_position(drone, seconds):
    filename = datetime.now().strftime("hover_%Y%m%d_%H%M%S.csv")
    clock = asyncio.get_running_loop()
    rows = 0

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["elapsed_s", "north_m", "east_m", "down_m"])

        async def record():
            nonlocal rows
            async for update in drone.telemetry.position_velocity_ned():
                position = update.position
                writer.writerow([
                    round(clock.time() - start, 3),
                    round(position.north_m, 3),
                    round(position.east_m, 3),
                    round(position.down_m, 3),
                ])
                rows += 1

        start = clock.time()
        try:
            await asyncio.wait_for(record(), timeout=seconds)
        except asyncio.TimeoutError:
            pass  # The requested hover time is over. Continue to landing.

    print(f"Saved {rows} position samples to {filename}")
    if rows == 0:
        print("No local position updates arrived during the hover.")

async def fly(args):
    drone = System()
    tasks = []
    arm_attempted = False
    landed = False
    try:
        print(f"Connecting to PX4 SITL at {args.connection}...")
        try:
            await asyncio.wait_for(drone.connect(system_address=args.connection), 30)
        except asyncio.TimeoutError as exc:
            raise RuntimeError(
                "Connection setup timed out after 30 seconds. Check that SITL "
                "is running (make px4_sitl gz_x500) and PX4 sends MAVLink "
                "to this host on UDP port 14540. "
                "The MAVSDK backend may also have failed to start."
            ) from exc
        await wait_for(drone.core.connection_state(), lambda s: s.is_connected,
                       30, "PX4 SITL connection (check UDP port 14540)")
        print("Connected to SITL.")
        if args.check_connection:
            position = await wait_for(drone.telemetry.position(), lambda p: True,
                                      15, "position telemetry")
            print(f"Telemetry received: relative altitude {position.relative_altitude_m:.2f} m.")
            print("Connection check complete. No flight commands were sent.")
            return

        state = dict(altitude="waiting", mode="waiting", battery="waiting",
                     armed="waiting", in_air="waiting")
        tasks = [
            asyncio.create_task(collect(drone.telemetry.position(), state,
                "altitude", lambda p: f"{p.relative_altitude_m:.2f} m relative")),
            asyncio.create_task(collect(drone.telemetry.flight_mode(), state,
                "mode", lambda mode: mode.name)),
            asyncio.create_task(collect(drone.telemetry.battery(), state,
                "battery", lambda b: f"{b.remaining_percent * 100:.0f}% / {b.voltage_v:.1f} V")),
            asyncio.create_task(collect(drone.telemetry.armed(), state,
                "armed", str)),
            asyncio.create_task(collect(drone.telemetry.in_air(), state,
                "in_air", str)),
            asyncio.create_task(print_telemetry(state)),
            asyncio.create_task(print_status(drone)),
        ]

        print("Waiting for PX4 GPS and home position readiness...")
        await wait_for(drone.telemetry.health(),
                       lambda h: h.is_global_position_ok and h.is_home_position_ok,
                       120, "GPS and home position")
        await wait_for(drone.telemetry.armed(), lambda armed: not armed,
                       5, "a disarmed starting vehicle")
        await asyncio.wait_for(drone.action.set_takeoff_altitude(args.altitude), 15)
        print("Arming...")
        arm_attempted = True
        await asyncio.wait_for(drone.action.arm(), 15)
        print(f"Taking off to {args.altitude:.1f} m...")
        await asyncio.wait_for(drone.action.takeoff(), 15)
        await wait_for(drone.telemetry.in_air(), bool, 30, "liftoff")
        await wait_for(drone.telemetry.position(),
                       lambda p: p.relative_altitude_m >= args.altitude * 0.95,
                       90, "takeoff altitude")
        await asyncio.wait_for(drone.action.hold(), 15)
        print(f"Hovering for {args.hover:.1f} seconds...")
        await log_hover_position(drone, args.hover)
        await land_and_wait(drone)
        landed = True
    finally:
        # Also request landing after a failed takeoff or Ctrl+C. A lost link
        # can prevent delivery; use QGroundControl to command Land if needed.
        if arm_attempted and not landed:
            print("Flight interrupted; requesting landing.")
            try:
                await land_and_wait(drone)
            except Exception as exc:
                print(f"Could not confirm landing: {exc}. Command Land in QGroundControl.")
        for task in tasks:
            task.cancel()
        for task in tasks:
            with contextlib.suppress(asyncio.CancelledError):
                try:
                    await task
                except Exception as exc:
                    print(f"Telemetry error: {exc}")


def positive(value):
    number = float(value)
    if not 0 < number < float("inf"):
        raise argparse.ArgumentTypeError("must be a positive finite number")
    return number

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--connection", default="udpin://127.0.0.1:14540")
    parser.add_argument("--check-connection", action="store_true",
                        help="check connection and telemetry without arming or flying")
    parser.add_argument("--altitude", type=positive, default=5.0, help="metres")
    parser.add_argument("--hover", type=positive, default=3.0, help="seconds (default: 3)")
    try:
        asyncio.run(fly(parser.parse_args()))
    except KeyboardInterrupt:
        print("Stopped.")
    except Exception as exc:
        parser.exit(1, f"Flight failed: {type(exc).__name__}: {exc or 'No additional details'}\n")
