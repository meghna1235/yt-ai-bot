import requests
import os
import uuid

# === STEP 1: GENERATE TOPIC + SCRIPT ===
def generate_script():
    api_key = os.getenv("OPENROUTER_API_KEY")  # You’ll add this on Render later

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a viral short-form video scriptwriter."},
            {"role": "user", "content": "Give me a unique video title and a 60-second script in a storytelling tone. Topic: A forgotten psychological trick used by ancient leaders."}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    full_text = response.json()['choices'][0]['message']['content']

    # Separate title + script
    lines = full_text.strip().split('\n')
    title = lines[0].replace("Title:", "").strip() if "Title:" in lines[0] else f"AI Short {uuid.uuid4().hex[:5]}"
    script = "\n".join(lines[1:]).strip()
    return title, script
def generate_voice(text, voice="en_US_male"):
    url = "https://api.ttsmaker.com/v1/convert"
    headers = {"Content-Type": "application/json"}
    payload = {
        "text": text,
        "voice": voice,
        "format": "mp3",
        "volume": 0,
        "speed": 1,
        "pitch": 1
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        with open("voice.mp3", "wb") as f:
            f.write(response.content)
        return "voice.mp3"
    else:
        raise Exception(f"TTS failed: {response.status_code} {response.text}")
