import os

__version__ = "2.0.0"
API_ROOT = "https://v3.openstates.org"
DEFAULT_USER_AGENT = f"pyopenstates/{__version__}"
API_KEY_ENV_VAR = "OPENSTATES_API_KEY"
ENVIRON_API_KEY = os.environ.get("OPENSTATES_API_KEY")
