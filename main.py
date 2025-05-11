import json
from yt_agent import run_agent

def main():
    with open("channels.json", "r") as f:
        channels = json.load(f)

    for channel in channels:
        for i in range(channel["uploads_per_day"]):
            print(f"Running upload {i+1}/{channel['uploads_per_day']} for: {channel['name']}")
            run_agent(channel["name"], channel["niche"])

if __name__ == "__main__":
    main()
