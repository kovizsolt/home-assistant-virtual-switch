import asyncio
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


const = _load("const")
machine_module = _load("state_machine")


def run(coro):
    return asyncio.run(coro)


class VirtualSwitchMachineTests(unittest.TestCase):
    def make_machine(self, online=True, internal=False, reported=False):
        return machine_module.VirtualSwitchStateMachine(
            online=online, internal_state=internal, reported_state=reported
        )

    def test_online_internal_changes_are_reported(self):
        machine = self.make_machine()
        run(machine.handle(const.EVENT_INTERNAL_ON))
        self.assertTrue(machine.internal_state)
        self.assertTrue(machine.reported_state)

    def test_offline_internal_on_is_hidden_until_online(self):
        machine = self.make_machine()
        run(machine.handle(const.EVENT_GO_OFFLINE))
        run(machine.handle(const.EVENT_INTERNAL_ON))
        self.assertFalse(machine.online)
        self.assertTrue(machine.internal_state)
        self.assertFalse(machine.reported_state)
        run(machine.handle(const.EVENT_GO_ONLINE))
        self.assertTrue(machine.reported_state)

    def test_offline_internal_off_is_hidden_until_online(self):
        machine = self.make_machine(online=True, internal=True, reported=True)
        run(machine.handle(const.EVENT_GO_OFFLINE))
        run(machine.handle(const.EVENT_INTERNAL_OFF))
        self.assertFalse(machine.internal_state)
        self.assertTrue(machine.reported_state)
        run(machine.handle(const.EVENT_GO_ONLINE))
        self.assertFalse(machine.reported_state)

    def test_offline_main_command_changes_only_internal_state(self):
        machine = self.make_machine(online=False)
        run(machine.handle(const.EVENT_MAIN_ON))
        self.assertTrue(machine.internal_state)
        self.assertFalse(machine.reported_state)

    def test_online_main_command_changes_both_states(self):
        machine = self.make_machine()
        run(machine.handle(const.EVENT_MAIN_ON))
        self.assertTrue(machine.internal_state)
        self.assertTrue(machine.reported_state)

    def test_repeated_availability_events_are_idempotent(self):
        machine = self.make_machine(online=False, internal=True, reported=False)
        run(machine.handle(const.EVENT_GO_OFFLINE))
        self.assertEqual((False, True, False), machine.snapshot)
        run(machine.handle(const.EVENT_GO_ONLINE))
        run(machine.handle(const.EVENT_GO_ONLINE))
        self.assertEqual((True, True, True), machine.snapshot)

    def test_unknown_event_does_not_change_state(self):
        machine = self.make_machine(online=False, internal=True, reported=False)
        before = machine.snapshot
        with self.assertLogs(level="WARNING"):
            run(machine.handle("unknown_event"))
        self.assertEqual(before, machine.snapshot)


if __name__ == "__main__":
    unittest.main()
