# vigil systems

**v.i.g.i.l.: visual indoor guard & intrusion locator**

an autonomous drone that patrols a building at night, so a guard doesn't have to walk it alone.

*working name. the project was previously called port, then lumaway.*

---

## the problem

overnight security is risky and expensive. a guard patrolling a dark building alone can run into an intruder with no backup, and every overnight post is a recurring cost. fixed cameras and alarms can report that something happened, but they can't go and look.

vigil is built to fill that gap: a drone that checks the building for you, verifies what tripped an alarm, and gets a photo to the people who need it.

---

## what vigil does

1. **patrols on its own.** each drone covers one floor. the building is mapped and divided into zones, and a state machine picks the next waypoint at random, weighted toward zones that haven't been visited recently. no fixed route means no predictable gaps.
2. **sees in the dark.** thermal imaging and lidar detect people, and the classifier separates a person from an animal or a misplaced object.
3. **responds.** on a likely intruder, the drone takes a photo, triggers the building's alarm system, and notifies the property manager.
4. **stays supervised.** a remote operator can watch and take over any drone at any time. guards keep their jobs, they just do them from somewhere safe.

indoor only. night only. version 1 uses sight only, with no audio. photos are taken on a trigger, not continuously, and there is no face matching.

---

## why a drone

a drone can cover a whole floor quickly, reach places a fixed camera can't, and investigate an alarm before anyone is dispatched. one remote operator can supervise several drones.

---

## the system

**custom flight controller (hardware)**
a 4-layer custom pcb with two stm32 microcontrollers (stm32f405 for navigation, stm32f103 for i/o) running px4. onboard sensors: dual imus (icm-20689, icm-20602), a barometer (ms5611), and a magnetometer (ist8310), plus a power monitor and flash for black-box logging. designed in kicad and manufactured in-house.

**companion computer (autonomy)**
an nvidia jetson nano runs patrol logic and person detection, and talks to the flight controller over mavlink.

**indoor sensing**
thermal camera and lidar for detection, plus a gps-free position source for indoor flight.

**response and remote operation**
photo capture, alarm-system integration, and an operator link for live view and manual override.

---

## project goals

- stable flight on the custom flight controller
- gps-free indoor position hold
- reliable person detection in the dark, with animals and objects filtered out
- random patrol that covers every zone within a set time window
- photo capture and alarm trigger on detection
- end-to-end demo: patrol, detect, photograph, alert, remote takeover

---

## status

in development. uw bothell electrical engineering capstone, 2026 to 2027.

- flight controller v1.0: built and assembled, bring-up in progress
- test airframe: assembly in progress
- sensing, patrol logic and alerts: planned

---

## team

built by a four-person electrical engineering capstone team at the university of washington bothell, supervised by dr. hannachi.

- cris r. martinez hernandez
- abraham chen
- frank ma
- howard sin

---

## built with

- stm32f405 / stm32f103 (flight controller mcus)
- px4 autopilot
- nvidia jetson nano (onboard compute)
- ros2 and mavlink
- opencv / python (perception)
- kicad (pcb design)
- platformio (firmware)

---

*vigil systems: always watching, so nobody has to.*
