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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Cache for Shelly Plug states
        self.shelly_cache = {}
        self.connect(signal=Signals.PageAdd, callback=self.on_page_changed)
        self.connect(signal=Signals.PageDelete, callback=self.on_page_changed)
        self.connect(signal=Signals.PageRename, callback=self.on_page_changed)
        logger.info("ChangePage action initialized.")

    def on_page_changed(self, *args):
        logger.info("Page change detected. Checking button states.")
        self.check_button_states()

    def check_button_states(self):
        button_2_ip = "10.27.46.33"
        button_3_ip = "10.27.46.70"

        def is_shelly_plug_on(ip):
            logger.info(f"Checking state of Shelly Plug at {ip}.")
            if ip in self.shelly_cache:
                logger.info(f"Using cached state for {ip}: {self.shelly_cache[ip]}")
                return self.shelly_cache[ip]

            try:
                response = requests.get(f"http://{ip}/rpc/Switch.GetStatus?id=0", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    is_on = data.get("output", False)  # Access switch state from response
                    self.shelly_cache[ip] = is_on
                    logger.info(f"Shelly Plug {ip} is {'ON' if is_on else 'OFF'}.")
                    return is_on
            except requests.RequestException as e:
                logger.error(f"Error contacting Shelly Plug at {ip}: {e}")

            return False

        state = 1 if is_shelly_plug_on(button_2_ip) and is_shelly_plug_on(button_3_ip) else 2
        logger.info(f"Determined button state: {state}")

        self.update_button_state(2, state)
        self.update_button_state(3, state)

    def update_button_state(self, button_id, state):
        logger.info(f"Updating button {button_id} to state {state}.")
        # Placeholder for setting the button state
        # This should interface with the button control API or system

    def __del__(self):
        # Disconnect all signals to prevent memory leaks
        self.disconnect_by_func(self.on_page_changed)

# Class to handle button state changes
class ChangeState(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("ChangeState action initialized.")

    def set_state(self, button_id, state):
        logger.info(f"Button {button_id} set to state {state}.")
        # Logic to set the state of a button

# Plugin base class
class CustomPlugin(PluginBase):
    def __init__(self):
        super().__init__()

    def activate(self):
        # Ensure `check_button_states` is called only when necessary
        logger.info("Activating plugin. Initializing button states if required.")
        self.test_check_button_states()

    def test_check_button_states(self):
        logger.info("Testing button state check during plugin activation.")
        # Create a temporary instance of ChangePage to manually test the logic
        temp_action = ChangePage(
            action_id="test",
            action_name="Test Page",
            deck_controller=None,
            page=None,
            plugin_base=self,
            state=None,
            input_ident=None,
        )
        temp_action.check_button_states()

    def get_actions(self):
        return [
            {
                "action_base": ChangePage,
                "action_id_suffix": "ChangePage",
                "action_name": "Change Page",
            },
            {
                "action_base": ChangeState,
                "action_id_suffix": "ChangeState",
                "action_name": "Change State",
            },
        ]
