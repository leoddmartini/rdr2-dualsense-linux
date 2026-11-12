# Troubleshooting

Always start by reading the log at `~/.local/state/rdr2-dualsense.log`.

## The game does not start and a notification appears

The launch wrapper refuses to start the game when the bridge is not ready. Fix the cause shown in the notification:

| Message | Fix |
| --- | --- |
| `USB DualSense not found within 10s` | Connect the controller with a USB cable. Check with `grep -l DualSense /sys/class/hidraw/*/device/uevent`. |
| `UDP port 6969 is in use by another program` | Close the program shown in the message, or check with `ss -ulpn 'sport = :6969'`. |
| `bridge exited during startup` | Read the log. Run `rdr2-dualsense-native --verbose` by hand to see the error. |

## `cannot open /dev/hidrawN: Permission denied`

Your user has no access to the controller's hidraw node. Install the Steam udev rules and reconnect the controller:

```bash
sudo dnf install steam-devices     # Fedora
sudo apt install steam-devices     # Debian/Ubuntu
```

Check the access with `ls -l /dev/hidraw*`. The DualSense node should show a `+` (ACL) or be group-accessible.

## Black screen or crash on launch

- Use the **original Script Hook RDR2** by Alexander Blade. Script Hook RDR2 V2 caused an intermittent black screen on Vulkan and a startup crash on DirectX 12 under Proton.
- Keep the graphics API on **Vulkan**. The setting is stored in `Documents/Rockstar Games/Red Dead Redemption 2/Settings/system.xml` inside the Proton prefix (`compatdata/1174180`).
- To isolate the problem, remove the mods one at a time: `vfs.asi` (LML), `NodixDualSense.asi`, `ScriptHookRDR2.dll`, `dinput8.dll`.
- If the game still does not start, use **Properties → Installed Files → Verify integrity of game files**.

## No trigger effects

1. Run the bridge by hand with `rdr2-dualsense-native --verbose` (remove the wrapper from the launch options first, or close the game so the port is free).
2. In the game, draw a weapon, aim with L2 and fire with R2.
3. You should see `packet: {"instructions": ...}` lines in the output.
   - **No packets:** the mod is not loaded. Check that `dinput8.dll`, `ScriptHookRDR2.dll` and `NodixDualSense.asi` are next to `RDR2.exe`, that the launch options contain `WINEDLLOVERRIDES="dinput8=n,b"`, and that `ScriptHookRDR2.log` mentions `NodixDualSense.asi`.
   - **Packets but no effect:** look for `unsupported trigger instruction` lines and open an issue that includes them.

## Rumble stops working

The bridge writes to the controller only when the trigger or lightbar state changes, and it never sets the rumble flags. If rumble stops, make sure no other tool (DualSenseY, `dualsensectl`, another bridge) is also writing to the controller.

## Xbox button prompts in the game

Install the optional Lenny's Mod Loader and the PlayStation Icons Replacement mod (see the README). In the game, choose the DualSense controller type in the controller settings if the option is shown.
