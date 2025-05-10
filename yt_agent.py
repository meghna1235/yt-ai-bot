import os
import json
import nltk
import torch
import base64
import requests
import numpy as np
from io import BytesIO
from dotenv import load_dotenv
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from nltk.tokenize import sent_tokenize
from moviepy.editor import (
    VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
)
from bark import generate_audio, preload_models
from bark.api import semantic_to_waveform
from bark.generation import SAMPLE_RATE, generate_text_semantic
from scipy.io.wavfile import write as write_wav

load_dotenv()
nltk.download('punkt')

def generate_script(niche):
    prompt = f"Give me a 60-second engaging short video script in the niche: {niche}. Include a hook and a twist."
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a viral short video script writer."},
            {"role": "user", "content": prompt}
        ]
    }
    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    return res.json()["choices"][0]["message"]["content"].strip()

def detect_character_voice(script):
    script = script.lower()
    if "old man" in script or "grandfather" in script:
        return "v2/en_speaker_9"
    elif "woman" in script or "girl" in script or "mother" in script:
        return "v2/en_speaker_1"
    elif "child" in script or "kid" in script:
        return "v2/en_speaker_5"
    elif "british" in script:
        return "v2/en_speaker_7"
    else:
        return "v2/en_speaker_0"

def generate_voice_bark(script):
    speaker = detect_character_voice(script)
    print(f"Using voice: {speaker}")

    preload_models(text_use_gpu=torch.cuda.is_available(), waveform_use_gpu=torch.cuda.is_available())

    sentences = sent_tokenize(script)
    pieces = []

    for sentence in sentences:
        semantic_tokens = generate_text_semantic(sentence, history_prompt=speaker, temp=0.7, min_eos_p=0.05)
        audio_array = semantic_to_waveform(semantic_tokens, history_prompt=speaker)
        pieces.append(audio_array)

    full_audio = np.concatenate(pieces)
    write_wav("voice.wav", SAMPLE_RATE, full_audio)
    return "voice.wav"

def generate_video(text_prompt):
    res = requests.post("https://api.piapi.ai/v1/inference", headers={
        "Authorization": f"Bearer {os.getenv('PIAPI_KEY')}"
    }, json={
        "model": "kling",
        "task_type": "video_generation",
        "input": {
            "prompt": text_prompt,
            "duration": 5
        }
    })
    video_url = res.json().get("output")
    r = requests.get(video_url)
    with open("clip.mp4", "wb") as f:
        f.write(r.content)
    return "clip.mp4"

def generate_captions(script_text, duration):
    lines = sent_tokenize(script_text)
    per_line_duration = duration / len(lines)
    clips = []

    for i, line in enumerate(lines):
        color = "white"
        if "!" in line:
            color = "yellow"
        if any(word in line for word in ["shocked", "danger", "fire"]):
            color = "red"

        txt_clip = (
            TextClip(line, fontsize=90, font='Arial-Bold', color=color, stroke_color="black", stroke_width=3)
            .set_position(("center", "bottom"))
            .set_duration(per_line_duration)
            .set_start(i * per_line_duration)
            .resize(lambda t: 1.1 if t < 0.2 else 1.0)
        )
        clips.append(txt_clip)

    return clips

def make_video(video_path, audio_path, script_text):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    video = video.set_audio(audio).resize((1080, 1920))
    caption_clips = generate_captions(script_text, audio.duration)
    final = CompositeVideoClip([video, *caption_clips])
    filename = f"final_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"
    final.write_videofile(filename, fps=24, threads=4)
    return filename

def generate_playground_thumbnail(prompt, title):
    from selenium import webdriver
    import time
    import undetected_chromedriver as uc

    print("Launching PlaygroundAI...")
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    driver = uc.Chrome(options=options)

    driver.get("https://playgroundai.com/")
    input("Log in manually and press ENTER to continue...")

    driver.get("https://playgroundai.com/create")
    time.sleep(5)
    prompt_box = driver.find_element("xpath", '//textarea')
    prompt_box.clear()
    prompt_box.send_keys(prompt)
    driver.find_element("xpath", '//button[contains(text(), "Generate")]').click()
    time.sleep(20)
    img_url = driver.find_element("xpath", '(//img[contains(@alt,"AI generated")])[1]').get_attribute("src")
    img_data = requests.get(img_url).content
    img = Image.open(BytesIO(img_data)).convert("RGBA").resize((1280, 720))

    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arialbd.ttf", 70)
    except:
        font = ImageFont.load_default()

    text = title.upper()
    w, h = draw.textsize(text, font=font)
    x = (img.width - w) // 2
    y = img.height - 100

    for dx in (-2, 2):
        for dy in (-2, 2):
            draw.text((x+dx, y+dy), text, font=font, fill="black")
    draw.text((x, y), text, font=font, fill="white")

    img.save("playground_thumbnail.png")
    driver.quit()
    return "playground_thumbnail.png"

def upload_to_youtube(video_path, title, description, thumbnail_path):
    print(f"[MOCK] Uploading {video_path} with title: {title} and thumbnail: {thumbnail_path}")


def run_agent(name, niche):
    script = generate_script(niche)
    voice = generate_voice_bark(script)
    video = generate_video(script.split(".")[0])
    final_video = make_video(video, voice, script)
    thumbnail = generate_playground_thumbnail(niche, script.split(".")[0])
    upload_to_youtube(final_video, f"{niche} Short", script, thumbnail)



