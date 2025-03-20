import os
import re
import argparse
import whisper

# Function to extract audio references from a markdown file
def extract_audio_references(md_content):
    return re.findall(r'!\[\[([^\]]+\.m4a)\]\]', md_content)

# Function to transcribe an audio file
def transcribe_audio(file_path, model):
    print(f"Transcribing: {file_path} ...")
    result = model.transcribe(file_path)
    return result["text"]

# Main function
def process_markdown_files(md_dir, audio_dir, model_size="medium"):
    # Load Whisper model
    model = whisper.load_model(model_size)

    # Ensure directories exist
    if not os.path.exists(md_dir):
        print(f"Error: Markdown directory '{md_dir}' not found.")
        return
    if not os.path.exists(audio_dir):
        print(f"Error: Audio directory '{audio_dir}' not found.")
        return

    # Process each markdown file in the specified directory
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
            for audio_file in audio_files:
                audio_path = os.path.join(audio_dir, audio_file)
                if os.path.exists(audio_path):
                    transcript_text += f"### Transcript for {audio_file}\n\n"
                    transcript_text += transcribe_audio(audio_path, model) + "\n\n"
                else:
                    print(f"Warning: {audio_file} not found in {audio_dir}.")

            if transcript_text:
                # Save transcription as a new markdown file
                transcript_filename = filename.replace(".md", "_transcript.md")
                transcript_path = os.path.join(md_dir, transcript_filename)
                with open(transcript_path, "w", encoding="utf-8") as transcript_file:
                    transcript_file.write(transcript_text)
                print(f"Transcription saved to {transcript_path}")

    print("All markdown files processed.")

# Command-line argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe audio references from markdown files.")
    parser.add_argument("md_dir", help="Directory containing markdown journal files")
    parser.add_argument("audio_dir", help="Directory containing audio recordings")
    parser.add_argument("--model", default="medium", choices=["tiny", "small", "medium", "large"], help="Whisper model size to use")

    args = parser.parse_args()
    process_markdown_files(args.md_dir, args.audio_dir, args.model)

