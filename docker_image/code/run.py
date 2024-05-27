"""
Simple script reading a parameter file to download a git repo and run an orchestrator from it
"""
import json
import logging
import os
import pathlib
import shutil
import subprocess

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

parameters = dict()
parameters_path = pathlib.Path(os.environ.get("CSM_PARAMETERS_ABSOLUTE_PATH")) / "parameters.json"
data = json.load(parameters_path.open("r"))

for _d in data:
    parameters[_d["parameterId"]] = _d["value"]

repository = parameters.get("git_repository")
branch = parameters.get("git_branch")
template_name = parameters.get("template_name")

if repository is None:
    logger.error("Missing git_repository parameter")
    exit(2)
if template_name is None:
    logger.error("Missing template_name parameter")
    exit(3)

if pathlib.Path("distant").exists():
    shutil.rmtree("distant")
clone_run = subprocess.run(f"git clone{'' if branch is None else f' -b {branch}'} {repository} distant".split(),
                           check=True)

os.environ["CSM_RUN_TEMPLATE_ID"] = template_name

print("=== === === Start sub run === === ===")
template_run = subprocess.run(f"csm-orc run run_templates/{template_name}/run.json".split(), cwd="distant", check=True)
print("=== === === End sub run === === ===")
