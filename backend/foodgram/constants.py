"""Project-wide constants: field limits and data paths."""

from pathlib import Path

MAX_NAME_LENGTH = 100
MAX_TEXT_LENGTH = 500

MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 32000
MIN_AMOUNT = 1
MAX_AMOUNT = 32000

CSV_DATA_DIR = Path(__file__).resolve().parent.parent.parent / 'data'
