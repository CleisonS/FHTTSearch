from pathlib import Path

APP_NAME = "UNM Inspector"
ORG_NAME = "Dez Telecom"
ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "output"
LOG_DIR = ROOT_DIR / "logs"
CONFIG_FILE = ROOT_DIR / "config.json"
DEFAULT_UNM_FILTERS = [
    "UNM",
    "UNM2000",
    "NE Manager",
    "FiberHome",
    "FH_",
    "FH-",
]
READINESS_COLUMNS = [
    "ONU Status",
    "Device Name",
    "Device Type",
    "Slot Number",
    "PON Number",
    "ONU Number",
    "Physical Address",
    "ONU Password",
    "Logical ID",
    "Logic SN Password",
]
