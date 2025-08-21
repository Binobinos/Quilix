import os
import re

from spaceworld import run


def update_version(new_version: str) -> bool:
    """Update the config and README version of the file."""
    config_file = r'core/config/config.py'

    if not os.path.exists(config_file):
        print(f"Error: {config_file} not found")
        return False

    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = re.sub(
        r'__version__ = "Quilix Version .* ENG"',
        f'__version__ = "Quilix Version {new_version} ENG"',
        content
    )

    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Updated version in {config_file} to {new_version}")
    return True


if __name__ == "__main__":
    run(update_version)
