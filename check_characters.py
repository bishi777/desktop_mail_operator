
import os
import sys
# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from widget import func

def check_chara_names():
    user_data = func.get_user_data()
    if not user_data:
        print("Failed to get user data")
        return

    for platform, items in user_data.items():
        if isinstance(items, list):
            names = [item.get('name') for item in items if isinstance(item, dict)]
            print(f"{platform}: {names}")

if __name__ == "__main__":
    check_chara_names()
