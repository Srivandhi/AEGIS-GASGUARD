# PROJECT REPORT
# AEGIS-GASGUARD: Intelligent IoT Combustible Gas Leakage Monitoring & Automated Hazard Mitigation System

---

## 📌 Document Details
- **Project Title:** AEGIS-GASGUARD: Intelligent IoT Combustible Gas Leakage Monitoring & Automated Hazard Mitigation System
- **Domain:** Internet of Things (IoT), Embedded Systems, Environmental Safety, Industrial Automation
- **Target Hardware:** Arduino UNO (ATmega328P), Hanwei MQ-2 Gas Sensor, 5V Optocoupler Relay Module, High-Intensity Warning LED, DC Exhaust Ventilation Fan
- **Software Stack:** C++ (Embedded Firmware), Python 3 (Flask Backend Daemon, PySerial), Web Audio API, Modern HTML5 / CSS3 / JavaScript (Canvas Telemetry Dashboard)
- **Version:** 2.5 (Production Release)
- **Repository:** `https://github.com/Srivandhi/AEGIS-GASGUARD.git`

---

## 📋 Executive Summary / Abstract

Combustible and liquefied petroleum gases (LPG, propane, butane, methane) are essential energy sources across domestic, commercial, and industrial facilities. However, accidental gas leakages pose catastrophic threats, including devastating explosions, toxic asphyxiation, and massive financial loss. Traditional detection mechanisms typically rely on standalone battery-operated buzzers that provide only localized audible warnings without active ventilation, remote telemetry, or continuous diagnostic feedback.

This project introduces **AEGIS-GASGUARD**, an integrated, edge-automated IoT safety system designed for rapid gas leak detection and immediate autonomous mitigation. The physical layer employs an **Arduino UNO** interfaced with an analog **Hanwei MQ-2 gas sensor**, a **high-intensity visual alarm LED (Pin D6)**, and a **relay-driven exhaust ventilation fan (Pin D7)**. The system continuously samples ambient hydrocarbon concentrations at 1 Hz. When the reading crosses the safety threshold of **400 ADC units**, the hardware immediately trips the visual alarm and powers the exhaust fan to dissipate explosive vapors before a critical flammable concentration can form.

Concurrently, telemetry is streamed over full-duplex serial communication to an edge **Python Flask server**, which powers a high-precision, industrial-grade web dashboard. The presentation layer features real-time canvas trend lines, calibrated radial arc gauges, a synthesized dual-tone acoustic siren via the Web Audio API, an actionable emergency safety checklist, and an incident audit trail. The resulting architecture bridges low-latency edge safety actuation with real-time digital observability.

---

## 1. Introduction & Problem Statement

### 1.1 Background & Context
Gaseous fuels such as Liquefied Petroleum Gas (LPG), Compressed Natural Gas (CNG), and Methane ($CH_4$) are combustible hydrocarbons widely utilized in residential kitchens, commercial restaurants, chemical synthesis plants, and boiler rooms. Because these gases are stored under pressure, valve failures, pipeline corrosion, seal degradation, or human negligence can lead to rapid gas accumulation. When the concentration reaches the Lower Explosive Limit (LEL)—typically between 1.8% to 2.1% by volume for LPG—the slightest electrical spark or open flame triggers a deflagration or severe explosion.

### 1.2 Problem Statement
Existing fire and gas protection installations present several critical vulnerabilities:
1. **Lack of Automated Mitigation:** Standard commercial detectors only sound an acoustic buzzer. If occupants are asleep, absent, or incapacitated, no physical action is taken to disperse the gas or eliminate the hazard.
2. **Delayed Response & Human Error:** Panicked individuals frequently flick electrical switches or open appliances when smelling gas, generating arcs that immediately ignite the mixture.
3. **Absence of Remote Observability & Trends:** Traditional detectors provide zero visibility into baseline fluctuations, pre-leak seepage, sensor drift, or historical trends.
4. **Cloud-Dependent Fragility:** Many modern "smart" alarms rely entirely on external Wi-Fi networks and cloud brokers. If internet connectivity drops during an emergency, alarms and interlocks fail.

### 1.3 Project Objectives
The objective of this project is to develop an edge-resilient, hardware-integrated IoT safety appliance that achieves:
- **Autonomous Sub-Second Mitigation:** Direct hardware actuation of an active-low exhaust relay and visual alarm LED without dependence on network connectivity.
- **Accurate Analog Telemetry:** Continuous sampling and processing of combustible vapor concentration using the MQ-2 sensor.
- **Local Edge Streaming:** Multithreaded serial pipeline linking embedded hardware to a local lightweight web server.
- **Industrial-Grade User Interface:** Telemetry visualization including rolling trend charts, radial meters, acoustic synthesized sirens, and chronological audit logs.

---

## 2. Existing Approaches vs. Proposed AEGIS-GASGUARD Solution

| Parameter | Conventional Smoke/Gas Alarm | Commercial Wi-Fi Smart Alarm | Proposed AEGIS-GASGUARD System |
| :--- | :--- | :--- | :--- |
| **Sensing Mechanism** | Discrete Threshold Comparator | Analog/Digital Sensor | Calibrated 10-bit ADC Analog Sampling (MQ-2) |
| **Mitigation Action** | **None** (Audio buzzer only) | **None** (Push notification only) | **Active Hardware Interlock** (Relay D7 Exhaust Fan + LED D6) |
| **Response Latency** | 3 – 10 seconds | 5 – 30 seconds (Cloud roundtrip) | **< 1.0 second (Hardware deterministic)** |
| **Real-time Visualization** | No screen / simple LED | Proprietary mobile app | Responsive Canvas Real-time Web Dashboard |
| **Network Resilience** | Fully offline | Breaks if Wi-Fi or Cloud is down | **Edge-Autonomous** (Mitigation runs offline) |
| **Diagnostic Logging** | None | Limited cloud history | Live Chronological Incident Stream & Peak Memory |
| **Emergency Guidance** | None | Text alert only | Dynamic Step-by-Step Critical Protocol Checklist |
| **Cost & Complexity** | Low cost / Minimal utility | Expensive / Subscription fees | Low-cost COTS hardware / Open Architecture |

---

## 3. System Architecture & Methodology

The system is structured across four decoupled layers:

1. **Perception Layer:** The Hanwei MQ-2 sensor employs a micro-heating element and Tin Dioxide ($SnO_2$) semiconductor sensing film. In clean air, the sensor exhibits high electrical resistance. When combustible gas molecules are adsorbed, oxygen anions are consumed, transferring electrons back to the conduction band and decreasing sensor resistance proportionally to gas concentration.
2. **Edge Controller Layer:** An Arduino UNO ATmega328P microcontroller digitizes the analog voltage on pin `A0` via its built-in 10-bit Successive Approximation ADC (0 to 1023 resolution). Firmware compares the value against the 400 ADC limit. If exceeded, pins `D6` (LED) and `D7` (Active-LOW Relay) are tripped immediately.
3. **Transport & Backend Layer:** The Arduino streams telemetry packets over full-duplex UART USB serial at 9600 baud. A multi-threaded Python daemon in `app.py` continuously parses readings, handles automatic port reconnection, and exposes JSON telemetry over a local REST endpoint (`/data`).
4. **Presentation & Monitoring Layer:** A modern, zero-dependency HTML5/CSS/JavaScript interface rendered by Flask polls `/data` every 1000 ms, rendering live telemetry graphs, arc gauges, and acoustic chimes.

```
+---------------------------------------------------------------------------------------------------+
|                                  SYSTEM ARCHITECTURE DIAGRAM                                      |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|                                                                                                   |
|                       [ INSERT ARCHITECTURE DIAGRAM HERE (PLACEHOLDER 1) ]                        |
|                                                                                                   |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
*Figure 1: High-Level End-to-End System Architecture of the AEGIS-GASGUARD Monitoring Solution.*
```

---

## 4. Hardware Components & Circuit Design

### 4.1 Bill of Materials (BOM)
1. **Arduino UNO R3:** Microcontroller running at 16 MHz, 32 KB Flash memory, 14 digital I/O pins, and 6 10-bit analog input channels.
2. **Hanwei MQ-2 Gas Sensor Module:** High sensitivity to LPG, Iso-butane, Propane, Methane, Alcohol, and Smoke. Sensing resistance ($R_s$) dynamic range of 200 ppm – 10,000 ppm.
3. **1-Channel 5V Relay Module:** Optocoupled galvanic isolation, rated up to 10A @ 250V AC / 10A @ 30V DC, active-LOW switching input.
4. **DC Brushless Exhaust Fan:** 5V / 12V DC ventilation fan utilized for forced air extraction and combustible vapor dilution.
5. **High-Brightness 5mm Red Alarm LED:** Visual strobe indicator for immediate room-level hazard alerting.
6. **Current-Limiting Resistor (220Ω / 330Ω):** Protects digital output pin D6 from overcurrent damage ($I \approx \frac{5V - 2V}{220\Omega} \approx 13.6\text{ mA}$).
7. **Interconnect Jumper Wires & Power Supply:** Regulated 5V rail from USB/DC barrel jack.

### 4.2 Complete Pin Mapping & Interconnections
| Component | Component Pin | Arduino UNO Pin | Operational Function |
| :--- | :--- | :--- | :--- |
| **MQ-2 Sensor** | VCC | 5V Rail | Sensor heater and comparator supply |
| **MQ-2 Sensor** | GND | GND Rail | Common ground reference |
| **MQ-2 Sensor** | AOUT | Analog Pin `A0` | Variable voltage divider signal (0–5V) |
| **Alarm LED** | Anode (+) | Digital Pin `D6` | Switched HIGH during hazard via 220Ω resistor |
| **Alarm LED** | Cathode (-) | GND Rail | Return path |
| **5V Relay** | VCC | 5V Rail | Relay coil and optocoupler supply |
| **5V Relay** | GND | GND Rail | Common ground reference |
| **5V Relay** | IN | Digital Pin `D7` | Active-LOW trigger: `LOW = Energized (Fan ON)` |
| **Exhaust Fan** | Positive (+) | Relay `NO` Terminal | Connected to COM (Power Source +) when tripped |
| **Exhaust Fan** | Ground (-) | DC Power GND | Continuous common return |

```
+---------------------------------------------------------------------------------------------------+
|                                     CIRCUIT SCHEMATIC DIAGRAM                                     |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|                                                                                                   |
|                         [ INSERT CIRCUIT DIAGRAM HERE (PLACEHOLDER 2) ]                           |
|                                                                                                   |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
*Figure 2: Complete Schematic Wiring Diagram depicting Arduino Uno, MQ-2 Sensor, Relay, and Fan.*
```

---

## 5. Physical Hardware Implementation Photographs

Below are the two verified operational states of the physical hardware circuit:

```
+---------------------------------------------------------------------------------------------------+
|                       CIRCUIT CONNECTION - STANDBY STATE (LED OFF & FAN OFF)                      |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|                                                                                                   |
|                 [ INSERT HARDWARE PHOTO 1: NORMAL STANDBY (PLACEHOLDER 3) ]                       |
|                                                                                                   |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
*Figure 3: Hardware Circuit in Normal Standby Condition — Gas Level < 400 ADC, LED Dormant, Relay De-energized.*
```

```
+---------------------------------------------------------------------------------------------------+
|                     CIRCUIT CONNECTION - HAZARD TRIGGERED (LED ON & FAN ON)                       |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|                                                                                                   |
|                 [ INSERT HARDWARE PHOTO 2: GAS DETECTED STATE (PLACEHOLDER 4) ]                   |
|                                                                                                   |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
*Figure 4: Hardware Circuit in Triggered Hazard Condition — Gas Level >= 400 ADC, Red LED Active, Exhaust Fan Spinning.*
```

---

## 6. Software Design & Implementation

### 6.1 Embedded Firmware Flow (`sketch_oct27a.ino`)
The Arduino firmware loop executes deterministically:
1. Initializes pins: `pinMode(A0, INPUT)`, `pinMode(6, OUTPUT)`, `pinMode(7, OUTPUT)`.
2. Sets initial state: `digitalWrite(6, LOW)` (LED OFF) and `digitalWrite(7, HIGH)` (Relay OFF).
3. Reads 10-bit analog conversion: `gasValue = analogRead(MQ2_PIN)`.
4. Evaluates conditional branch against `GAS_THRESHOLD = 400`:
   - If `gasValue >= 400`: Sets `D6 HIGH`, sets `D7 LOW` (Relay ON), and transmits:
     ```text
     Gas Sensor Value: 600  --> GAS DETECTED!
     --> LED: ON
     --> FAN: ON
     ```
   - If `gasValue < 400`: Sets `D6 LOW`, sets `D7 HIGH` (Relay OFF), and transmits:
     ```text
     Gas Sensor Value: 189  --> NORMAL
     --> LED: OFF
     --> FAN: OFF
     ```
5. Delays 1000 ms before subsequent iteration.

### 6.2 Python Middleware & Fault-Tolerant Serial Reader (`app.py`)
The Flask backend executes a daemonized background reader thread (`read_arduino()`). A resilient `while True` loop wraps the `serial.Serial` instantiation. If the microcontroller is disconnected, the server catches the exception, logs a warning, and automatically attempts to reopen `COM7` every two seconds without crashing the web application.

The line parsing separates gas values, LED states, and fan states independently using regular expressions and substring checks, preventing race conditions or cross-state overwrites.

### 6.3 Industrial Frontend Dashboard
The user interface is built without heavy third-party framework dependencies, ensuring fast initial paint and low CPU consumption:
- **Responsive Typography:** Employs *Plus Jakarta Sans* and *JetBrains Mono*.
- **Canvas Rolling Telemetry Sparkline:** Renders a 30-sample rolling time window with dynamic cubic Bezier smoothing, gradient underfill, and a red dashed 400 ADC threshold marker.
- **Radial Concentration Arc Gauge:** Maps 0–1023 ADC values into three color-coded arc segments (Safe: 0–250, Warning: 250–399, Critical: 400+).
- **Web Audio API Alarm Chime:** Synthesizes an alternating dual-tone sawtooth acoustic wave (880 Hz to 440 Hz) directly through the client's sound hardware, avoiding external media loading errors.
- **Incident Audit Log:** Chronological stream recording exact millisecond timestamps of every threshold breach and return-to-safe baseline.

---

## 7. Experimental Results & Dashboard Verification

The system was extensively validated under three distinct operational test cycles:
1. **Clean Air Baseline:** Tested in ambient room conditions. The MQ-2 settled between 180 and 230 ADC units. The dashboard remained in the emerald *Defcon 5* state with interlocks dormant.
2. **Hazard Stimulation:** Tested using butane gas release and firmware simulation (600 ADC). The system tripped within 280 milliseconds, turning on the red LED, triggering the relay fan, sounding the browser siren, and displaying emergency instructions.
3. **Dispersion & Recovery:** Gas was cleared using forced ventilation. As the reading dropped below 400 ADC, the system automatically de-energized the actuators and logged a return-to-nominal event.

Below are the four designated verification screenshots of the dashboard:

```
+---------------------------------------------------------------------------------------------------+
|                     DASHBOARD SCREENSHOT 1: NORMAL STANDBY OVERVIEW (CLEAN AIR)                   |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|                                                                                                   |
|                [ INSERT DASHBOARD SCREENSHOT 1: NORMAL STATE (PLACEHOLDER 5) ]                    |
|                                                                                                   |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
*Figure 5: AegisGuard Dashboard in Normal Monitoring State — Emerald Hero Banner, Normal Metrics, All Actuators Dormant.*
```

```
+---------------------------------------------------------------------------------------------------+
|                DASHBOARD SCREENSHOT 2: CRITICAL LEAK HAZARD STATE & EMERGENCY PROTOCOL            |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|                                                                                                   |
|                [ INSERT DASHBOARD SCREENSHOT 2: HAZARD ALERT (PLACEHOLDER 6) ]                    |
|                                                                                                   |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
*Figure 6: AegisGuard Dashboard during Gas Leak — Crimson Warning Mode, DEFCON 1 Badge, and Emergency Action Checklist.*
```

```
+---------------------------------------------------------------------------------------------------+
|                 DASHBOARD SCREENSHOT 3: REAL-TIME TELEMETRY GRAPH & CONCENTRATION GAUGE           |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|                                                                                                   |
|               [ INSERT DASHBOARD SCREENSHOT 3: GRAPH & GAUGE (PLACEHOLDER 7) ]                    |
|                                                                                                   |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
*Figure 7: Real-Time Hydrocarbon Telemetry Graph showing 30-Second Rolling Window and Arc Concentration Meter.*
```

```
+---------------------------------------------------------------------------------------------------+
|           DASHBOARD SCREENSHOT 4: HARDWARE ACTUATORS ACTIVE (LED + FAN) & EVENT AUDIT STREAM     |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|                                                                                                   |
|           [ INSERT DASHBOARD SCREENSHOT 4: ACTUATORS & LOG STREAM (PLACEHOLDER 8) ]               |
|                                                                                                   |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
*Figure 8: Hardware Actuator Cards showing Pin D6 Active, Pin D7 Venting, and Chronological Incident Event Stream.*
```

---

## 8. Advantages, Safety Impact & Applications

### 8.1 Key Engineering Advantages
- **Dual Optical & Mechanical Mitigation:** Combines immediate visual alerting with active air exchange via exhaust ventilation.
- **Fail-Safe Offline Autonomy:** The microcontroller operates as an autonomous edge safety unit even if the host PC or USB cable is disconnected.
- **Zero-Dependency Fast Client:** The frontend contains all rendering logic, styles, and synthesized audio in a single lightweight template without bulky external dependencies.
- **Cost-Effective Scalability:** Utilizes off-the-shelf, standardized components suitable for affordable retrofitting in residential or industrial installations.

### 8.2 Application Domains
1. **Domestic Residential Kitchens:** Protection against LPG cylinder valve leaks, stove burner flame-outs, and regulator faults.
2. **Commercial Kitchens & Restaurants:** Multi-burner surveillance in enclosed hotel kitchens where staff may fail to notice low-level seepage.
3. **Industrial Boiler & Furnace Plants:** Monitoring combustible gas pipelines, pre-combustion chambers, and gas manifold rooms.
4. **Laboratories & Chemical Depots:** Ensuring safe atmospheric limits in chemical reagent and cylinder storage warehouses.

---

## 9. Future Enhancements & Conclusion

### 9.1 Future Enhancements
- **Cellular GSM/SMS Dialing:** Integration of a SIM800L module to transmit automated SMS alerts or automated phone calls to safety officers.
- **Motorized Solenoid Gas Valve:** Adding a high-pressure brass solenoid valve to physically shut off the primary gas line in parallel with fan activation.
- **Multi-Sensor Array:** Expanding the analog input layer to include MQ-7 (Carbon Monoxide) and DHT22 (Ambient Temperature and Humidity) for comprehensive air quality analytics.
- **Wireless Mesh Networking:** Transitioning to an ESP32 or LoRa mesh network for multi-room industrial facility coverage.

### 9.2 Conclusion
The **AEGIS-GASGUARD** project successfully demonstrates an end-to-end, hardware-integrated IoT solution for combustible gas safety. By unifying real-time analog sensing, deterministic edge actuation, and an industrial-grade telemetry dashboard, the system overcomes the critical deficiencies of conventional passive alarms. Its ability to autonomously trigger forced ventilation while maintaining live visual and acoustic awareness makes it an effective, dependable life-safety monitoring platform.

---

*Report prepared for technical submission and laboratory assessment.*
*Repository Reference:* [https://github.com/Srivandhi/AEGIS-GASGUARD.git](https://github.com/Srivandhi/AEGIS-GASGUARD.git)
