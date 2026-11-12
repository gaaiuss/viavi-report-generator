from pathlib import Path

# Directories
ROOT_DIR = Path(__file__).parent
RESOURCE_DIR = ROOT_DIR / "resource"
OUTPUT_DIR = ROOT_DIR / "output"

# Create output folder if it doesn't exists
Path.mkdir(OUTPUT_DIR, exist_ok=True)

# Files
JSON_OUTPUT_FILE = OUTPUT_DIR / "merged.json"
CSV_OUTPUT_FILE = OUTPUT_DIR / "output.csv"
CSV_CONFIG_FILE = RESOURCE_DIR / "config.csv"
JSON_TEST_DATA_FOLDER = ROOT_DIR / "test_data"
