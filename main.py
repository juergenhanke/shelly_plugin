import requests
import logging
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.PluginManager.PluginBase import PluginBase
from src.Signals import Signals

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Class to handle page changes
class ChangePage(ActionBase):
    def __init__(self, action_id, action_name, deck_controller, page, plugin_base, state, input_ident):
        super().__init__(action_id, action_name, deck_controller, page, plugin_base, state, input_ident)
        self.connect(signal=Signals.PageAdd, callback=self.on_page_changed)
        self.connect(signal=Signals.PageDelete, callback=self.on_page_changed)
        self.connect(signal=Signals.PageRename, callback=self.on_page_changed)

        # Cache for Shelly Plug states
        self.shelly_cache = {}

    def on_page_changed(self, *args):
        # Check the state of buttons 2 and 3 after a page change
        self.check_button_states()

    def check_button_states(self):
        button_2_ip = "10.27.46.33"
        button_3_ip = "10.27.46.70"

        def is_shelly_plug_on(ip):
            if ip in self.shelly_cache:
                return self.shelly_cache[ip]

            try:
                response = requests.get(f"http://{ip}/rpc/Switch.GetStatus?id=0", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    is_on = data.get("output", False)  # Access switch state from response
                    self.shelly_cache[ip] = is_on
                    return is_on
            except requests.RequestException as e:
                logger.error(f"Error contacting Shelly Plug at {ip}: {e}")

            return False

        state = 1 if is_shelly_plug_on(button_2_ip) and is_shelly_plug_on(button_3_ip) else 2

        self.update_button_state(2, state)
        self.update_button_state(3, state)

    def update_button_state(self, button_id, state):
        # Placeholder for setting the button state
        logger.info(f"Updating button {button_id} to state {state}")

    def __del__(self):
        # Disconnect all signals to prevent memory leaks
        self.disconnect_by_func(self.on_page_changed)

# Class to handle button state changes
class ChangeState(ActionBase):
    def __init__(self, action_id, action_name, deck_controller, page, plugin_base, state, input_ident):
        super().__init__(action_id, action_name, deck_controller, page, plugin_base, state, input_ident)

    def set_state(self, button_id, state):
        # Logic to set the state of a button
        logger.info(f"Button {button_id} set to state {state}")

# Plugin base class
class CustomPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.change_page = ChangePage(
            action_id="change_page",
            action_name="Change Page",
            deck_controller=None,  # Replace with actual deck controller
            page=None,  # Replace with actual page
            plugin_base=self,
            state=None,
            input_ident=None,
        )
        self.change_state = ChangeState(
            action_id="change_state",
            action_name="Change State",
            deck_controller=None,  # Replace with actual deck controller
            page=None,  # Replace with actual page
            plugin_base=self,
            state=None,
            input_ident=None,
        )

    def activate(self):
        # Ensure `check_button_states` is called only when necessary
        logger.info("Activating plugin. Initializing button states if required.")
        if self.should_check_button_states():
            self.change_page.check_button_states()

    def should_check_button_states(self):
        # Placeholder logic for determining if button state check is needed
        return True
