import os
import re
import argparse
import whisper
import json

# File to store already transcribed recordings
TRANSCRIPTION_LOG = "transcribed_files.json"

# Function to load already transcribed files
def load_transcribed_files():
    if os.path.exists(TRANSCRIPTION_LOG):
        with open(TRANSCRIPTION_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Function to save transcribed file records
def save_transcribed_files(transcribed_files):
    with open(TRANSCRIPTION_LOG, "w", encoding="utf-8") as f:
        json.dump(transcribed_files, f, indent=4)

# Function to extract audio references from markdown
def extract_audio_references(md_content):
    return re.findall(r'!\[\[([^\]]+\.(m4a|webm))\]\]', md_content)

# Function to transcribe an audio file
def transcribe_audio(file_path, model):
    print(f"Transcribing: {file_path} ...")
    result = model.transcribe(file_path)
    return result["text"]

# Main function to process markdown and standalone audio files
def process_files(md_dir, audio_dir, model_size="medium"):
    # Load Whisper model
    model = whisper.load_model(model_size)

    # Load previously transcribed files
    transcribed_files = load_transcribed_files()

    # Ensure directories exist
    if not os.path.exists(md_dir):
        print(f"Error: Markdown directory '{md_dir}' not found.")
        return
    if not os.path.exists(audio_dir):
        print(f"Error: Audio directory '{audio_dir}' not found.")
        return

    # 1. Process Markdown files
    for filename in os.listdir(md_dir):
        if filename.endswith(".md"):
            md_path = os.path.join(md_dir, filename)

            with open(md_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            # Extract referenced audio files
            audio_files = extract_audio_references(md_content)

            if not audio_files:
                continue  # Skip files with no audio references

            transcript_text = ""
            for audio_file, ext in audio_files:
                audio_path = os.path.join(audio_dir, audio_file)

                if os.path.exists(audio_path) and audio_file not in transcribed_files:
                    transcript_text += f"### Transcript for {audio_file}\n\n"
                    transcript_text += transcribe_audio(audio_path, model) + "\n\n"
                    transcribed_files[audio_file] = True
                elif audio_file in transcribed_files:
                    print(f"Skipping {audio_file}, already transcribed.")
                else:
                    print(f"Warning: {audio_file} not found in {audio_dir}.")

            if transcript_text:
                # Save transcription as a new markdown file
                transcript_filename = filename.replace(".md", "_transcript.md")
                transcript_path = os.path.join(md_dir, transcript_filename)
                with open(transcript_path, "w", encoding="utf-8") as transcript_file:
                    transcript_file.write(transcript_text)
                print(f"Transcription saved to {transcript_path}")

    # 2. Process Standalone Audio Files
    for audio_file in os.listdir(audio_dir):
        if audio_file.endswith(".m4a") or audio_file.endswith(".webm"):
            audio_path = os.path.join(audio_dir, audio_file)

            # Check if it has already been transcribed
            if audio_file in transcribed_files:
                print(f"Skipping {audio_file}, already transcribed.")
                continue

            # Transcribe and save as _transcribed.md
            transcript_text = f"### Transcript for {audio_file}\n\n"
            transcript_text += transcribe_audio(audio_path, model) + "\n\n"

            transcript_filename = os.path.splitext(audio_file)[0] + "_transcribed.md"
            transcript_path = os.path.join(audio_dir, transcript_filename)

            with open(transcript_path, "w", encoding="utf-8") as transcript_file:
                transcript_file.write(transcript_text)
            
            print(f"Standalone transcription saved to {transcript_path}")
            transcribed_files[audio_file] = True  # Mark as transcribed

    # Save updated transcribed files list
    save_transcribed_files(transcribed_files)

    print("All markdown files and standalone audio files processed.")

# Command-line argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe audio references from markdown files and standalone audio recordings.")
    parser.add_argument("md_dir", help="Directory containing markdown journal files")
    parser.add_argument("audio_dir", help="Directory containing audio recordings")
    parser.add_argument("--model", default="medium", choices=["tiny", "small", "medium", "large"], help="Whisper model size to use")

    args = parser.parse_args()
    process_files(args.md_dir, args.audio_dir, args.model)

