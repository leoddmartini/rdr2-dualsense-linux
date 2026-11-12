# How it works

## Data flow

1. `NodixDualSense.asi` is loaded into RDR2 by the ASI loader and uses Script Hook RDR2 to read the game state.
2. It sends JSON packets over UDP to `127.0.0.1:6969`, the default port of DSX. Proton processes share the host network namespace, so a native Linux process can receive them.
3. `rdr2-dualsense-native` converts each instruction into DualSense trigger-effect bytes and writes a USB output report to the controller's `/dev/hidrawN` node.

## DSX packet format

```json
{"instructions": [
  {"type": 1, "parameters": [0, 2, 17, 0, 8, 6, 6]},
  {"type": 2, "parameters": [0, 44, 255, 0]}
]}
```

| `type` | Name | Parameters |
| --- | --- | --- |
| `1` | TriggerUpdate | `[controller, trigger, mode, ...mode parameters]`, where trigger `1` = L2 and `2` = R2 |
| `2` | RGBUpdate | `[controller, red, green, blue]` |

Other instruction types (player LEDs, mic LED, trigger threshold) are ignored.

## Trigger modes

| Mode | Name | Parameters | Effect |
| --- | --- | --- | --- |
| 0 | Normal | none | No resistance |
| 1 | GameCube | none | Fixed preset |
| 2 to 6 | VerySoft, Soft, Hard, VeryHard, Hardest | none | Fixed presets |
| 7 | Rigid | none | Full resistance |
| 8, 11 | VibrateTrigger, VibrateTriggerPulse | none | Fixed vibration preset |
| 9 | Choppy | none | Fixed preset |
| 10 | Medium | none | Fixed preset |
| 12 | CustomTriggerValue | `customMode, b1..b7` | Raw effect bytes |
| 13, 21 | Resistance, FEEDBACK | `start (0-9), force (1-8)` | Resistance from a zone to the end of travel |
| 14 | Bow | `start, end, force, snapForce` | Builds tension, then snaps |
| 15 | Galloping | `start, end, firstFoot, secondFoot, frequency` | Rhythmic pulses |
| 16, 22 | SemiAutomaticGun, WEAPON | `start (2-7), end, force (1-8)` | Resistance that breaks like a trigger pull |
| 17, 23 | AutomaticGun, VIBRATION | `start, strength (1-8), frequency` | Vibration along the trigger travel |
| 18 | Machine | `start, end, ampA, ampB, frequency, period` | Alternating vibration |
| 19 | VIBRATE_TRIGGER_10Hz | none | 10 Hz vibration |
| 20 | OFF | none | Effect disabled |

The byte encodings are ported from [DualSenseY-v2](https://github.com/WujekFoliarz/DualSenseY-v2) (`scePadCustomTriggers.cpp`).

## USB output report

The report is 48 bytes long. The bridge sets only these bytes:

| Byte | Value |
| --- | --- |
| 0 | Report ID `0x02` |
| 1 | `0x0C`: enables the right and left trigger effects. The rumble bits stay clear so Steam Input's rumble is preserved |
| 2 | `0x04` once a colour has been received: enables the lightbar colour |
| 11 to 21 | R2 effect (mode byte followed by 10 parameter bytes) |
| 22 to 32 | L2 effect |
| 45 to 47 | Lightbar red, green and blue |

Reports are written only when the computed report changes. Writing continuously, for example at 60 Hz, overrides the reports Steam Input sends and stops rumble from working.

## Why not run DSX or the original service under Proton?

- DSX is a Windows application that needs direct HID access and its own virtual controller driver.
- The *DualSense* mod's `controller-service.exe` uses hidapi inside Wine. While Steam Input owns the controller, it reports `No device detected`.
- A native Linux process can open `/dev/hidrawN` directly, because the `steam-devices` udev rules grant access to the logged-in user, and it can do so while Steam Input is running.
