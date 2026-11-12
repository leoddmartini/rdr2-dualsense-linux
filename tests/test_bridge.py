"""Unit tests for the DSX bridge conversion logic (no hardware required)."""
import importlib.machinery
import importlib.util
import json
import pathlib
import unittest

BRIDGE_PATH = pathlib.Path(__file__).resolve().parent.parent / "bin" / "rdr2-dualsense-native"
_loader = importlib.machinery.SourceFileLoader("bridge", str(BRIDGE_PATH))
_spec = importlib.util.spec_from_loader("bridge", _loader)
bridge = importlib.util.module_from_spec(_spec)
_loader.exec_module(bridge)


def packet(*instructions):
    return json.dumps({"instructions": [
        {"type": t, "parameters": list(p)} for t, p in instructions
    ]})


class TriggerEffectTests(unittest.TestCase):
    def test_effects_are_always_11_bytes(self):
        for mode in list(bridge.FIXED_EFFECTS) + [12, 13, 14, 15, 16, 17, 18]:
            effect = bridge.dsx_trigger_effect(mode, [2, 6, 6, 4, 2, 1, 0, 0, 0])
            if effect is not None:
                self.assertEqual(len(effect), 11, mode)
                self.assertTrue(all(0 <= b <= 255 for b in effect), mode)

    def test_medium(self):
        self.assertEqual(bridge.dsx_trigger_effect(10, [2, 5, 0, 0]),
                         [0x22, 2, 35, 1, 6, 6, 1, 33, 0, 0, 0])

    def test_automatic_gun(self):
        self.assertEqual(bridge.dsx_trigger_effect(17, [0, 8, 6, 6]),
                         [0x26, 0xFF, 0x03, 0xFF, 0xFF, 0xFF, 0x3F, 0, 0, 6, 0])

    def test_resistance_from_zone_5(self):
        effect = bridge.dsx_trigger_effect(13, [5, 8])
        self.assertEqual(effect[0], 0x21)
        self.assertEqual(effect[1] | (effect[2] << 8), 0b1111100000)

    def test_semi_automatic_gun(self):
        self.assertEqual(bridge.dsx_trigger_effect(16, [2, 7, 8]),
                         [0x25, 0x84, 0x00, 7, 0, 0, 0, 0, 0, 0, 0])

    def test_invalid_parameters_rejected(self):
        self.assertIsNone(bridge.dsx_trigger_effect(16, [0, 1, 8]))   # start < 2
        self.assertIsNone(bridge.dsx_trigger_effect(13, [0, 0]))      # force 0
        self.assertIsNone(bridge.dsx_trigger_effect(99, []))          # unknown mode


class ControllerStateTests(unittest.TestCase):
    def test_report_layout(self):
        state = bridge.ControllerState()
        state.apply(packet((1, [0, 1, 7]), (1, [0, 2, 10]), (2, [0, 10, 20, 30])))
        report = state.usb_report()
        self.assertEqual(len(report), 48)
        self.assertEqual(report[0], 0x02)
        self.assertEqual(report[1], 0x0C)             # trigger flags only, no rumble flags
        self.assertEqual(report[2], 0x04)             # lightbar
        self.assertEqual(report[11], 0x22)            # R2 = Medium
        self.assertEqual(report[22], 0x01)            # L2 = Rigid
        self.assertEqual(tuple(report[45:48]), (10, 20, 30))

    def test_no_lightbar_until_requested(self):
        report = bridge.ControllerState().usb_report()
        self.assertEqual(report[2], 0x00)

    def test_garbage_is_ignored(self):
        state = bridge.ControllerState()
        state.apply("not json")
        state.apply(packet((1, [0, 2, "x"])))
        state.apply(packet((1, [0])))
        self.assertEqual(state.right, bridge.EFFECT_OFF)

    def test_reset(self):
        state = bridge.ControllerState()
        state.apply(packet((1, [0, 2, 7])))
        state.reset_triggers()
        self.assertEqual(state.right, bridge.EFFECT_OFF)


if __name__ == "__main__":
    unittest.main()
