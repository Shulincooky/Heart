from pathlib import Path
import tomli
import yaml
import os

root_path = Path(__file__).parent.parent

with open(root_path/"pyproject.toml", "rb") as file:
    data = tomli.load(file)
    model_version = data["project"]["model_version"]
    plugins = root_path/data["project"]["plugins_path"]

model_path = root_path/"model"
conf_path = root_path/"conf"

model = model_path/f"emotion_model-V{model_version}.pth"
final_model = model_path/f"emotion_model_final-V{model_version}.pth"

with open(conf_path/"heartConf.toml", "rb") as file:
    heart_conf = tomli.load(file)

if os.path.exists(conf_path/"apiConf.private.yaml"):
    with open(conf_path/"apiConf.private.yaml", 'r') as file:
        api_conf = yaml.safe_load(file)
elif os.path.exists(conf_path/"apiConf.yaml"):
    with open(conf_path/"apiConf.yaml", 'r') as file:
        api_conf = yaml.safe_load(file)

heart_log = root_path/"logs"

__all__ = ["model","final_model","heart_conf","api_conf","heart_log","plugins"]