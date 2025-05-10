import json
from yt_agent import run_agent

def main():
    with open("channels.json", "r") as f:
        channels = json.load(f)

    for channel in channels:
        print(f"Running agent for: {channel['name']}")
        run_agent(channel['name'], channel['niche'])

if __name__ == "__main__":
    main()
