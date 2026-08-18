import importlib.util
import os
import sys
import types
import unittest

_PKG_DIR = os.path.join(os.path.dirname(__file__), "..", "custom_components", "virtual_switch")
_PKG_NAME = "_virtual_switch_under_test"
_pkg = types.ModuleType(_PKG_NAME)
_pkg.__path__ = [_PKG_DIR]
sys.modules[_PKG_NAME] = _pkg


def _load(name):
    full_name = f"{_PKG_NAME}.{name}"
    spec = importlib.util.spec_from_file_location(full_name, os.path.join(_PKG_DIR, f"{name}.py"))
    module = importlib.util.module_from_spec(spec)
    module.__package__ = _PKG_NAME
    sys.modules[full_name] = module
    spec.loader.exec_module(module)
    return module


state = _load("state")


class VirtualSwitchStateTests(unittest.TestCase):
    def test_internal_is_the_only_on_off_state(self):
        device = state.VirtualSwitchState(online=True, internal_state=False)
        device.set_internal(True)
        self.assertTrue(device.internal_state)
        self.assertTrue(device.main_is_on)

    def test_offline_controls_main_availability(self):
        device = state.VirtualSwitchState(online=True, internal_state=True)
        device.set_online(False)
        self.assertFalse(device.main_available)
        self.assertTrue(device.internal_state)

    def test_internal_can_change_while_main_is_offline(self):
        device = state.VirtualSwitchState(online=False, internal_state=False)
        device.set_internal(True)
        self.assertFalse(device.main_available)
        self.assertTrue(device.internal_state)

    def test_main_returns_with_current_internal_state(self):
        device = state.VirtualSwitchState(online=False, internal_state=False)
        device.set_internal(True)
        device.set_online(True)
        self.assertTrue(device.main_available)
        self.assertTrue(device.main_is_on)

    def test_main_command_is_ignored_offline(self):
        device = state.VirtualSwitchState(online=False, internal_state=False)
        self.assertFalse(device.set_from_main(True))
        self.assertFalse(device.internal_state)

    def test_main_command_changes_internal_online(self):
        device = state.VirtualSwitchState(online=True, internal_state=False)
        self.assertTrue(device.set_from_main(True))
        self.assertTrue(device.internal_state)

    def test_repeated_values_are_idempotent(self):
        device = state.VirtualSwitchState(online=False, internal_state=True)
        self.assertFalse(device.set_online(False))
        self.assertFalse(device.set_internal(True))


if __name__ == "__main__":
    unittest.main()

