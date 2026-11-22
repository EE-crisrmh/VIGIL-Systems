# vigil systems

**v.i.g.i.l.: visual indoor guard & intrusion locator**

<img width="1273" height="643" alt="Screenshot 2026-11-17 at 6 02 31 PM" src="https://github.com/user-attachments/assets/6ceb16cc-402a-4f83-a684-8e14ea8d4f1f" />

an autonomous drone that patrols a building at night alongside the security guard, so nobody has to walk a dark warehouse alone.

---

## the problem

overnight security is risky and expensive. a guard patrolling a large, dark building alone can run into an intruder with no backup, and at one site we interviewed nobody patrols for 2 to 3 hours between rounds. fixed cameras and alarms can report that something happened, but they can't go and look.

vigil fills that gap: a drone that checks the building, finds people in the dark, and alerts the guard. the guard stays in charge. vigil is an extra layer, not a replacement.

target customer: large warehouses.

---

## what vigil does

1. **patrols on its own.** the building is mapped and divided into zones, and a state machine picks the next waypoint at random, weighted toward zones that haven't been visited recently. no fixed route means no predictable gaps, and every zone gets covered.
2. **sees in the dark.** a thermal camera and lidar feed an ai person detector.
3. **flies without gps.** lidar mapping and optical flow hold position indoors.
4. **alerts a guard.** on a likely person, the drone alerts the guard (alert method is still being decided).

indoor only. no audio. no face matching. photos are taken on a trigger, not continuously. no remote piloting.

---

## scope change (november 2026)

our first custom flight controller (v1.0) failed bring-up on nov 8, 2026: vbat shorted to gnd on all rails. instead of spending the year debugging a board, we changed the plan:

| | before | now |
| --- | --- | --- |
| flight controller | custom stm32f405 + stm32f103 board | commercial pixhawk 6c mini running px4 |
| esc | custom | commercial (readytosky) |
| compute | jetson nano | jetson orin nano super |
| indoor position | bluetooth trilateration | 2d lidar mapping + optical flow (bluetooth kept as an optional experiment) |
| test platform | custom airframe | 450 mm frame (f450 fiberglass now, moving to carbon fiber) |

the custom flight controller files stay in `hardware/old-hardware-stack/` as a record of what we built and what went wrong.

---

## the system

```
battery -> power distribution -> 4 escs -> 4 motors
                |-> pixhawk 6c mini (px4): stabilization, state estimation (ekf2), flight modes, failsafes
                |-> jetson orin nano super (ros 2): mapping, patrol logic, person detection, alerts

rc receiver   -> pixhawk   (manual control, safety override)
h-flow        -> pixhawk   (can bus: optical flow + height, holds position without gps)
2d lidar      -> jetson    (usb: maps the building, finds where the drone is, avoids obstacles)
thermal cam   -> jetson    (usb: sees people in the dark)
jetson <-> pixhawk         (waypoints in, status out, lidar position fed back into ekf2)
jetson -> guard            (alert, method tbd)
```

**flight controller:** pixhawk 6c mini (stm32h7) running px4. handles stabilization, state estimation (ekf2), flight modes and failsafes.

**companion computer:** nvidia jetson orin nano super running ros 2. builds the map from the lidar, runs patrol logic and person detection, and sends waypoints to the flight controller. it also sends its lidar-based position back to px4 so the drone doesn't drift. the link is still being decided: mavsdk (used in our simulation so far) or uxrce-dds (px4's native ros 2 bridge).

**sensing:**
- **thermal camera:** flir lepton 3.5 on a purethermal usb board. 160x120 at about 9 fps, shows up on the jetson as a normal usb webcam. resolution still to be confirmed against our detection goal.
- **2d lidar:** rplidar a1 class, on top of the drone. maps walls, columns and racks.
- **optical flow + rangefinder:** holybro h-flow, pointing down. plugs into the pixhawk can port (dronecan), has its own ir light for low light, reads height from 8 cm to 30 m. replaces the matek 3901-l0x, which px4 doesn't support.

**airframe:** 450 mm frame with br2212 motors and 4 readytosky escs. moving from the f450 fiberglass frame to a carbon fiber 450 mm frame for stiffness (less vibration reaching the flight controller). battery (3s vs 4s) is still being decided from the weight and power budget. estimated all-up weight about 1.7 kg (not yet verified), ceiling 2-3 kg for the prototype.

---

## plan and targets

1. bench-validate the flight hardware
2. first rc hover on the f450
3. indoor flight without gps
4. detect a person and alert a guard
5. communications and location test
6. full patrol demo

targets for the demo (goals, not results): 5-minute stable flight, 0.5 m position hold, 90%+ person detection in the dark, alert in under 2 s, 100% zone coverage per patrol.

key dates:
- dec 11, 2026: parts list and design decisions confirmed (battery, escs, sensors)
- january 2027: parts ordered when the 495 capstone class starts
- jun 4, 2027: full patrol demo

budget: $1,500 total, all in.

---

## top risks

1. **esc or battery overcurrent causing a fire.** sizing the battery voltage, escs and props together, then bench testing current and heat before flight.
2. **carbon fiber side effects.** carbon blocks radio and conducts electricity, so antennas go outside the frame and every power pad gets insulated.
3. **indoor sensors not good enough.** optical flow needs some light and floor texture, and a 2d lidar only sees one slice of the room. tested early in simulation, then on real floors.
4. **jetson to px4 integration.** the lidar position has to reach px4's estimator or the drone drifts.
5. **weight and battery budget not closing.** too heavy means less thrust margin and shorter flights.

---

## status

in development.

- flight controller v1.0 (custom): built, failed bring-up. dropped for the prototype.
- commercial flight controller and compute: selected. parts list being confirmed by dec 11, ordering in january 2027.
- sensors: thermal camera and optical flow sensor chosen (nov 22), pending final confirmation.
- f450 test airframe: assembled. carbon fiber 450 mm frame planned.
- simulation: px4 sitl takeoff, hover and a simulated warehouse patrol running. scripts and test data are in `simulation/` and `software/` (not yet analyzed). optical flow only (no gps) simulation in progress.
- mapping, person detection and alerts: planned.

---

## repo layout

- `hardware/old-hardware-stack/`: custom flight controller v1.0, dropped after failed bring-up (kicad, bom, gerbers, assembly)
- `mechanical/`: cad
- `simulation/`: px4 sitl and ros 2 simulation, test data
- `software/`: companion computer code
- `docs/`: design documents

---

## team

- cris r. martinez hernandez: systems engineer
- howard sin: hardware lead
- abraham chen: ml / software lead
- frank ma: mechanical, power and structures lead

contact: cris0105mh@gmail.com

---

## built with

- px4 autopilot and mavlink
- pixhawk 6c mini
- nvidia jetson orin nano super
- ros 2
- holybro h-flow (dronecan), flir lepton 3.5, rplidar
- opencv / python (perception)
- kicad (pcb design)

---

*vigil systems: always watching, so nobody has to.*
