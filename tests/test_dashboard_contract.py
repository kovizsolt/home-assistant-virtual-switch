import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "virtual_switch"


class DashboardContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.card = (COMPONENT / "www" / "virtual-switch-card.js").read_text()
        cls.init = (COMPONENT / "__init__.py").read_text()
        cls.manifest = json.loads((COMPONENT / "manifest.json").read_text())

    def test_card_is_an_automatic_frontend_resource(self):
        self.assertIn("frontend", self.manifest["dependencies"])
        self.assertIn("lovelace", self.manifest["dependencies"])
        self.assertIn("async_register_static_paths", self.init)
        self.assertIn("async_create_item", self.init)

    def test_card_is_available_in_graphical_picker(self):
        self.assertIn("window.customCards", self.card)
        self.assertIn("getConfigForm", self.card)
        self.assertIn("getStubConfig", self.card)
        self.assertIn("getEntitySuggestion", self.card)
        self.assertIn('integration: "virtual_switch"', self.card)

    def test_card_discovers_all_three_switches(self):
        self.assertIn("_internal", self.card)
        self.assertIn("_online", self.card)
        self.assertIn("loadCardHelpers", self.card)

    def test_main_uses_native_home_assistant_availability(self):
        switch_source = (COMPONENT / "switch.py").read_text()
        self.assertIn("def available(self)", switch_source)
        self.assertIn("return self.controller.online", switch_source)
        self.assertNotIn("reported_state", switch_source)

    def test_no_state_synchronization_loop_exists(self):
        controller_source = (COMPONENT / "controller.py").read_text()
        self.assertNotIn("state_changed", controller_source)
        self.assertNotIn("reported_state", controller_source)
        self.assertNotIn("async_track", controller_source)

    def test_main_command_is_a_method_not_a_property(self):
        controller_source = (COMPONENT / "controller.py").read_text()
        self.assertNotIn("@property\n    async def async_main", controller_source)
        self.assertIn("async def async_main(self, value: bool)", controller_source)


if __name__ == "__main__":
    unittest.main()
