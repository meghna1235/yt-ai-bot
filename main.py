from yt_generator import generate_script, generate_voice, generate_image, make_video, upload_to_youtube

def main():
    print("Running bot...")

    topic, script = generate_script()
    print(f"Topic: {topic}")
    
    voice_path = generate_voice(script)
    print(f"Voiceover saved at: {voice_path}")
    
    image_path = generate_image(topic)
    print(f"Image saved at: {image_path}")
    
    video_path = make_video(image_path, voice_path)
    print(f"Video created at: {video_path}")
    
    upload_to_youtube(video_path, topic, script)
    print("Uploaded successfully.")

if __name__ == "__main__":
    main()
