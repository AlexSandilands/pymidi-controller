import yaml
import os
import shutil
from importlib import resources
from pathlib import Path

XDG = Path.home() / ".config"  if "XDG_CONFIG_HOME" not in __import__("os").environ else Path(__import__("os").environ["XDG_CONFIG_HOME"])
CFG_DIR  = XDG / "pymidi-controller"
CFG_FILE = CFG_DIR / "config.yaml"
FUNC_DIR = CFG_DIR / "functions"

def ensure_config_dir():
    CFG_DIR.mkdir(parents=True, exist_ok=True)

def load_config():
    ensure_config_dir()
    if not CFG_FILE.exists():
        return {}
    with CFG_FILE.open() as f:
        return yaml.safe_load(f)

def save_config(cfg: dict):
    ensure_config_dir()
    # optional backup
    if CFG_FILE.exists():
        shutil.copy(CFG_FILE, CFG_FILE.with_suffix(".yaml.bak"))
    with CFG_FILE.open("w") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)

def init_config():
    ensure_config_dir()
    data = resources.files("pymidi_controller").joinpath("data/default_config.yaml")

    # Ensure the config file exists
    if not CFG_FILE.exists():
        CFG_FILE.write_text(data.read_text())
        os.chmod(CFG_FILE, 0o600)
        print(f"Created {CFG_FILE}, please discover your API keys & set midi mappings.")
    else:
        print(f"{CFG_FILE} already exists, skipping.")

    # Ensure the functions directory exists
    if not FUNC_DIR.exists():
        FUNC_DIR.mkdir(parents=True)
        os.chmod(FUNC_DIR, 0o700)
        print(f"Created {FUNC_DIR}, please add your custom functions here.")
    else:
        print(f"{FUNC_DIR} already exists, skipping.")
    