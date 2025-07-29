from pathlib import Path
import tomli
import yaml
import os

from scr.util.looper_build import LooperManager

root_path = Path(__file__).parent.parent

with open(root_path/"pyproject.toml", "rb") as file:
    data = tomli.load(file)
    model_version = data["project"]["model_version"]
    plugins = root_path/data["project"]["plugins_path"]

conf_path = root_path/"conf"

with open(conf_path/"heartConf.toml", "rb") as file:
    heart_conf = tomli.load(file)

if os.path.exists(conf_path/"apiConf.private.yaml"):
    with open(conf_path/"apiConf.private.yaml", 'r') as file:
        api_conf = yaml.safe_load(file)
elif os.path.exists(conf_path/"apiConf.yaml"):
    with open(conf_path/"apiConf.yaml", 'r') as file:
        api_conf = yaml.safe_load(file)

looper_manager = LooperManager()

heart_log = root_path/"logs"

__all__ = ["heart_conf","api_conf","heart_log","plugins","looper_manager"]