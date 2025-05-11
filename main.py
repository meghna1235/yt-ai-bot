import json
import logging
from yt_agent import run_agent

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        with open("channels.json", "r") as f:
            channels = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        logging.error("Failed to load channels.json. Ensure it exists and is valid JSON.")
        return

    for channel in channels:
        name = channel.get("name")
        niche = channel.get("niche")
        uploads = channel.get("uploads_per_day", 1)

        if not name or not niche:
            logging.warning("Skipping incomplete channel config.")
            continue

        for i in range(uploads):
            logging.info(f"Running upload {i+1}/{uploads} for: {name}")
            run_agent(name, niche)

if __name__ == "__main__":
    main()
