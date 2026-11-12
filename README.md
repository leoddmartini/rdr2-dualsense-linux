# rdr2-dualsense-linux

Adaptive triggers and lightbar effects for **Red Dead Redemption 2** on **Linux (Steam + Proton)** with a **PlayStation 5 DualSense** controller, while keeping Steam Input, rumble and full controller support working.

The core of this project is a small, dependency-free **DSX-compatible UDP bridge**. RDR2 mods that were written for [DSX (DualSenseX)](https://store.steampowered.com/app/1812620/DSX/), a Windows-only application, send their trigger effects to it, and the bridge writes them directly to the controller through `/dev/hidraw`.

> [!WARNING]
> **Never use game mods in Red Dead Online.** Rockstar may ban accounts that go online with modified game files. Script Hook RDR2 closes the game automatically when you try to go online, but you are responsible for removing the mods before playing online.

## Contents

- [How it works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [What did not work](#what-did-not-work)
- [Uninstall](#uninstall)
- [Credits](#credits)
- [License](#license)

## How it works

```
 RDR2 (Proton) ──► NodixDualSense.asi ──UDP 127.0.0.1:6969──► rdr2-dualsense-native ──► /dev/hidrawN ──► DualSense
                    (DSX JSON protocol)                          (Linux host)              (USB output report)
 Steam Input ───────────────────────── buttons, sticks, rumble ─────────────────────────────────────────────►
```

- **Steam Input** keeps handling the controller in-game (RDR2 does not support the DualSense natively).
- **NodixDualSense.asi** reads the game state (current weapon, aiming, health) and sends DSX instructions over UDP. Proton shares the host network stack, so the packets reach a native Linux process.
- **`rdr2-dualsense-native`** translates DSX instructions into DualSense trigger-effect bytes and writes them to the controller. It only sets the trigger and lightbar flags of the output report and only writes on state changes, so Steam's rumble is not overridden.
- **`rdr2-with-triggers`** is a Steam launch wrapper that starts the bridge with the game, refuses to start the game if something is wrong, and stops the bridge when the game exits.

See [docs/how-it-works.md](docs/how-it-works.md) for the protocol and report layout.

## Requirements

| Component | Notes |
| --- | --- |
| Linux with Steam | Tested on Fedora 44 |
| Proton | Tested with Proton Experimental |
| DualSense | **Connected by USB.** Bluetooth uses a different report layout and is not supported yet |
| `steam-devices` udev rules | Gives your user access to the controller's hidraw node (`sudo dnf install steam-devices`) |
| Python | 3.9 or newer, standard library only |
| `iproute2` (`ss`) | Used by the launch wrapper to check the UDP port |

Game mods, which must be downloaded from their official pages (they cannot be redistributed here):

| Mod | Purpose | Download |
| --- | --- | --- |
| ASI Loader (`dinput8.dll`) | Loads `.asi` plugins | [Nexus Mods #1472](https://www.nexusmods.com/reddeadredemption2/mods/1472?tab=files) (file "Mod Loader") |
| Script Hook RDR2 by Alexander Blade | Script API used by the DualSense mod | [dev-c.com](http://www.dev-c.com/rdr2/scripthookrdr2/) |
| NodixDualSense | Sends DSX trigger and lightbar instructions | [Nexus Mods #9297](https://www.nexusmods.com/reddeadredemption2/mods/9297) |
| Lenny's Mod Loader *(optional)* | Required by the PlayStation icons mod | [rdr2mods.com](https://www.rdr2mods.com/downloads/rdr2/tools/76-lennys-mod-loader-rdr/) |
| PlayStation Icons Replacement (PS5) *(optional)* | Shows PlayStation button prompts instead of Xbox | [Nexus Mods #660](https://www.nexusmods.com/reddeadredemption2/mods/660) |

> [!IMPORTANT]
> Use the **original Script Hook RDR2 by Alexander Blade**, not Script Hook RDR2 V2. With V2 the game showed an intermittent black screen on Vulkan and crashed on DirectX 12 under Proton.

## Installation

### 1. Install the bridge

```bash
git clone https://github.com/leoddmartini/rdr2-dualsense-linux.git
cd rdr2-dualsense-linux
./install.sh
```

This copies `rdr2-dualsense-native` and `rdr2-with-triggers` to `~/.local/bin`.

### 2. Install the game mods

The game folder is usually `~/.local/share/Steam/steamapps/common/Red Dead Redemption 2`, next to `RDR2.exe`. Copy these files into it:

| File | From |
| --- | --- |
| `dinput8.dll` | ASI Loader |
| `ScriptHookRDR2.dll` | Script Hook RDR2 (`bin/` folder of the zip) |
| `NodixDualSense.asi` | NodixDualSense |

Optional, for PlayStation button prompts:

1. Copy the **contents** of LML's `ModLoader` folder (`vfs.asi`, `lml.ini` and the DLLs) into the game folder.
2. Create a folder named `lml` in the game folder and copy the `PS Buttons Dualsense` folder into it.

### 3. Configure Steam

In **Red Dead Redemption 2 → Properties**:

1. **General → Launch Options:**
   ```
   WINEDLLOVERRIDES="dinput8=n,b" ~/.local/bin/rdr2-with-triggers %command%
   ```
   `WINEDLLOVERRIDES` makes Wine load the ASI loader instead of its built-in `dinput8`.
2. **Controller:** enable Steam Input for the game.
3. **Compatibility:** Proton Experimental (other recent Proton versions should also work).

Keep the in-game graphics API on **Vulkan**.

## Usage

Connect the DualSense with a USB cable and launch the game from Steam. The bridge starts and stops with it.

The game is **not** started, and a desktop notification explains why, when:

- UDP port 6969 is used by another program (a stale copy of the bridge is restarted automatically);
- the bridge cannot start, or no USB DualSense is found within 10 seconds.

The log is written to `~/.local/state/rdr2-dualsense.log`.

You can also run the bridge by hand, for example for debugging:

```bash
rdr2-dualsense-native --verbose     # Ctrl+C stops it and releases the triggers
```

| Variable | Default | Used by |
| --- | --- | --- |
| `RDR2_DSX_PORT` | `6969` | wrapper |
| `RDR2_DSX_TIMEOUT` | `10` | wrapper (seconds to wait for the controller) |
| `RDR2_DSX_LOG` | `~/.local/state/rdr2-dualsense.log` | wrapper |

## Troubleshooting

See [docs/troubleshooting.md](docs/troubleshooting.md). Most common issues:

- **The game does not start and a notification appears:** read the reason; most often the controller is not connected by USB.
- **Black screen on launch:** make sure you are using the original Script Hook RDR2, not V2.
- **No trigger effects:** run the bridge with `--verbose` and check that packets arrive while you aim or shoot.
- **Xbox button prompts:** install the optional Lenny's Mod Loader and PlayStation icons mod.

## What did not work

These approaches were tried first; they are documented to save others time.

| Approach | Result |
| --- | --- |
| Script Hook RDR2 **V2** | Intermittent black screen on Vulkan and a crash at startup on DirectX 12 under Proton. The original Script Hook works. |
| *DualSense* mod (Nexus #1204) with its `controller-service.exe` under Proton | The service reports `No device detected` while Steam Input owns the controller. Its `.asi` also stops updating its input file shortly after loading on current game versions. |
| Disabling Steam Input | RDR2 does not recognise the DualSense without Steam Input. |

## Uninstall

```bash
./install.sh --uninstall
```

Then remove the mod files listed in [Installation](#2-install-the-game-mods) from the game folder, clear the Steam launch options, and use **Properties → Installed Files → Verify integrity of game files** if needed.

## Credits

- Trigger-effect conversion table ported from [DualSenseY-v2](https://github.com/WujekFoliarz/DualSenseY-v2) by WujekFoliarz (MIT).
- [NodixDualSense](https://www.nexusmods.com/reddeadredemption2/mods/9297) by NodixTech.
- [Script Hook RDR2](http://www.dev-c.com/rdr2/scripthookrdr2/) by Alexander Blade.
- [Lenny's Mod Loader](https://www.rdr2mods.com/downloads/rdr2/tools/76-lennys-mod-loader-rdr/) by the LML contributors.
- [PlayStation Icons Replacement](https://www.nexusmods.com/reddeadredemption2/mods/660) by vStar925.

See [THIRD_PARTY.md](THIRD_PARTY.md). This project is not affiliated with Rockstar Games, Sony Interactive Entertainment, Valve or the DSX developers.

## License

[MIT](LICENSE)
