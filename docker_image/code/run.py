"""
Simple script reading a parameter file to download a git repo and run an orchestrator from it
"""
import json
import logging
import os
import pathlib
import shutil
import subprocess
import venv

logging.basicConfig(
    format="%(asctime)s %(levelname)s\t%(message)s",
    datefmt="[%Y/%m/%d-%X]", )

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
logger.info(f"Cloning - {repository}")
clone_run = subprocess.run(f"git clone{'' if branch is None else f' -b {branch}'} {repository} distant".split(),
                           check=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           universal_newlines=True)
for l in clone_run.stdout.split('\n'):
    logger.debug(l)

if not pathlib.Path(f"distant/run_templates/{template_name}/run.json").exists():
    logger.error(f"No run template named {template_name} exits in cloned repository")
    exit(4)

logger.info("Checking for requirements in cloned repository")

hl_reqs = pathlib.Path("distant/requirements.txt")
rt_reqs = pathlib.Path(f"distant/run_templates/{template_name}/requirements.txt")
use_venv = hl_reqs.exists() or rt_reqs.exists()
run_cmd = "csm-orc"

if use_venv:
    logger.info("Requirements found, installing")
    venv.create("distant/venv", with_pip=True)
    subprocess.run(["venv/bin/pip", "install", "cosmotech-run-orchestrator"],
                   check=True,
                   stdout=subprocess.PIPE,
                   universal_newlines=True,
                   cwd="distant")
    if hl_reqs.exists():
        subprocess.run(["venv/bin/pip", "install", "-r", hl_reqs.absolute()],
                       check=True,
                       stdout=subprocess.PIPE,
                       universal_newlines=True,
                       cwd="distant")
    if rt_reqs.exists():
        subprocess.run(["venv/bin/pip", "install", "-r", rt_reqs.absolute()],
                       check=True,
                       stdout=subprocess.PIPE,
                       universal_newlines=True,
                       cwd="distant")
    run_cmd = "venv/bin/csm-orc"
    logger.debug("Requirements installed")

logger.info(f"--> Starting run template - {template_name}")
template_run = subprocess.run(f"{run_cmd} run run_templates/{template_name}/run.json".split(),
                              cwd="distant",
                              check=True)
logger.info("--> Run template finished")
