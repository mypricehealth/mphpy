import sys
from pathlib import Path

from dotenv import load_dotenv


def load_env():
    path = Path(__file__)
    root_dir = None
    env_file = None
    for parent in path.parents:
        root_dir = parent
        env_file = root_dir.joinpath(".env")
        if env_file.exists():
            break

    if root_dir is None:
        print("No .env file found", file=sys.stderr)
        return

    print(f"Using .env from {repr(str(root_dir))}.")

    load_dotenv(root_dir.joinpath(".env"))
    load_dotenv(root_dir.joinpath(".env.local"))
