import json
from pathlib import Path

_config_path = Path(__file__).parent / "config.json"

_required_keys = (
    "printer_name", 
    "currency", 
    "logo_path"
    )

if not _config_path.exists():
    print(f"❗Error: Configuration file not found: {_config_path}")
    raise FileNotFoundError(f"Configuration file not found: {_config_path}")

with open(_config_path, "r") as f:
    app_config = json.load(f)

for k in app_config:
    if k not in _required_keys:
        print(f"❗Error: Unrecognized config name '{k}' in {app_config}")
        print(f"Expected keys: {', '.join(_required_keys)}")
        raise KeyError(f"Unrecognized config name '{k}' in {app_config}")
    if app_config[k] is None:
        print(f"❗Error: Config name '{k}' is set to null in {app_config}")
        raise KeyError(f"Config name '{k}' is set to null in {app_config}")
