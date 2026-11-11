from pathlib import Path

# Directories
ROOT_DIR = Path(__file__).parent.parent
RESOURCE_DIR = ROOT_DIR / "resource"
OUTPUT_DIR = ROOT_DIR / "output"

# Create output folder if it doesn't exists
Path.mkdir(OUTPUT_DIR, exist_ok=True)

# Files
JSON_OUTPUT_FILE = OUTPUT_DIR / "merged.json"
CSV_OUTPUT_FILE = OUTPUT_DIR / "output.csv"
CSV_CONFIG_FILE = RESOURCE_DIR / "config.csv"

# GUI
ICON_PATH = RESOURCE_DIR / "icon.png"
LABEL_ICON_PATH = RESOURCE_DIR / "ui_icon.png"

# Sizing
BIG_FONT_SIZE = 40
MEDIUM_FONT_SIZE = 24
SMALL_FONT_SIZE = 12
MINIMUM_WIDTH = 1000
TEXT_MARGIN = 10
