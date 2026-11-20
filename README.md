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
| test platform | custom airframe | f450 frame |

the custom flight controller files stay in `hardware/old-hardware-stack/` as a record of what we built and what went wrong.

---

## the system

**flight controller:** pixhawk 6c mini (stm32h7) running px4. handles stabilization and flight modes.

**companion computer:** nvidia jetson orin nano super. runs ros 2, person detection and patrol logic, and talks to the flight controller over mavlink.

**sensing:** thermal camera (lepton class, model tbd), 2d lidar (rplidar a1 class), optical flow + rangefinder (matek 3901-l0x class).

**airframe:** f450 (about 450 mm) with racerstar br2212 motors and 4 escs. estimated all-up weight about 1.7 kg, ceiling 2-3 kg for the prototype.

---

## plan and targets

1. bench-validate the flight hardware
2. first rc hover on the f450
3. indoor flight without gps
4. detect a person and alert a guard
5. communications and location test
6. full patrol demo

targets for the demo (goals, not results): 5-minute stable flight, 0.5 m position hold, 90%+ person detection in the dark, alert in under 2 s, 100% zone coverage per patrol.

budget: $1,500 total, all in.

---

## status

in development.

- flight controller v1.0 (custom): built, failed bring-up. dropped for the prototype.
- commercial flight controller and compute: selected, parts being ordered.
- f450 test airframe: assembled.
- early position test data and scripts are in `simulation/` and `software/` (not yet analyzed).
- sensing, patrol logic and alerts: planned.

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
- opencv / python (perception)
- kicad (pcb design)

---

*vigil systems: always watching, so nobody has to.*
