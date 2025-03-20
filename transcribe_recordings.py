import os
import re
import whisper

# Load Whisper model
model = whisper.load_model("medium")  # can be "small" or "large" as needed

# Function to extract audio references from a markdown file
def extract_audio_references(md_content):
    return re.findall(r'!\[\[([^\]]+\.m4a)\]\]', md_content)

# Function to transcribe an audio file
def transcribe_audio(file_path):
    print(f"Transcribing: {file_path} ...")
    result = model.transcribe(file_path)
    return result["text"]

# Process all markdown files in the directory
for filename in os.listdir("."):
    if filename.endswith(".md"):  # Only process markdown files
        with open(filename, "r", encoding="utf-8") as f:
            md_content = f.read()

        # Extract audio file references
        audio_files = extract_audio_references(md_content)
        
        if not audio_files:
            continue  # Skip if no audio files are referenced

        transcript_text = ""
        for audio_file in audio_files:
            if os.path.exists(audio_file):  # Ensure audio file exists
                transcript_text += f"### Transcript for {audio_file}\n\n"
                transcript_text += transcribe_audio(audio_file) + "\n\n"
            else:
                print(f"Warning: {audio_file} not found.")

        if transcript_text:
            # Create transcript file with "_transcript" appended to the original filename
            transcript_filename = filename.replace(".md", "_transcript.md")
            with open(transcript_filename, "w", encoding="utf-8") as transcript_file:
                transcript_file.write(transcript_text)
            print(f"Transcription saved to {transcript_filename}")

print("All markdown files processed.")

