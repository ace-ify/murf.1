
import os
from dotenv import load_dotenv
from pathlib import Path

# Load frontend .env.local
env_path = Path("frontend/.env.local")
load_dotenv(dotenv_path=env_path)

keys = [
    "LIVEKIT_URL",
    "LIVEKIT_API_KEY",
    "LIVEKIT_API_SECRET",
    "NEXT_PUBLIC_LIVEKIT_URL"
]

print("Checking FRONTEND environment variables...")
for key in keys:
    value = os.getenv(key)
    if value:
        print(f"{key}: SET (Length: {len(value)})")
        if key == "LIVEKIT_URL" or key == "NEXT_PUBLIC_LIVEKIT_URL":
            print(f"  -> Starts with: {value[:6]}...")
    else:
        print(f"{key}: MISSING")
