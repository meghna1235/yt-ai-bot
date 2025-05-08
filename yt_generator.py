import requests
import os
import uuid

# === STEP 1: GENERATE TOPIC + SCRIPT ===
def generate_script():
    api_key = os.getenv("OPENROUTER_API_KEY")

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

    lines = full_text.strip().split('\n')
    title = lines[0].replace("Title:", "").strip() if "Title:" in lines[0] else f"AI Short {uuid.uuid4().hex[:5]}"
    script = "\n".join(lines[1:]).strip()
    return title, script

# === STEP 2: GENERATE VOICEOVER USING TTSMaker ===
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

# === STEP 3: GENERATE IMAGE USING HUGGINGFACE ===
def generate_image(prompt):
    hf_token = os.getenv("HUGGINGFACE_TOKEN")
    headers = {
        "Authorization": f"Bearer {hf_token}"
    }
    payload = {
        "inputs": prompt
    }

    response = requests.post(
        "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        with open("image.jpg", "wb") as f:
            f.write(response.content)
        return "image.jpg"
from moviepy.editor import ImageClip, AudioFileClip

def make_video(image_path, audio_path, output_path="output.mp4"):
    audio_clip = AudioFileClip(audio_path)
    image_clip = ImageClip(image_path).set_duration(audio_clip.duration)

    image_clip = image_clip.set_audio(audio_clip)
    image_clip = image_clip.resize(height=1920)  # for vertical video
    image_clip = image_clip.set_position("center")

    final = image_clip.set_fps(30)
    final.write_videofile(output_path, codec="libx264", audio_codec="aac")

    return output_path
        
    else:
        raise Exception(f"Image generation failed: {response.status_code} {response.text}")


