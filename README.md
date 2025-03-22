# Whisper Live Transcription Tool

A simple, easy-to-use tool that transcribes your speech in real-time using your microphone. Perfect for converting spoken words to text during meetings, interviews, or personal recordings.

## What This Tool Does

- Creates text transcriptions from your voice in real-time
- Works on your Windows computer (no internet connection needed)
- Saves transcripts automatically to a text file
- Simple to use with minimal technical knowledge required

## Installation Guide for Windows

### Step 1: Install Python

1. Download Python from [python.org](https://www.python.org/downloads/windows/)
2. Click on the latest Python version (Python 3.10 or newer)
3. Scroll down and click on "Windows installer (64-bit)"
4. Run the downloaded file
5. **IMPORTANT**: Check the box that says "Add Python to PATH" before clicking Install
6. Click "Install Now"

### Step 2: Install FFmpeg

1. Download FFmpeg from [this link](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip)
2. Unzip the downloaded file to a location you can find easily (e.g., `C:\ffmpeg`)
3. Add FFmpeg to your PATH:
   - Search for "Environment Variables" in the Windows search bar
   - Click "Edit the system environment variables"
   - Click the "Environment Variables" button
   - In the "System variables" section, find and select the "Path" variable
   - Click "Edit"
   - Click "New"
   - Add the path to the FFmpeg bin folder (e.g., `C:\ffmpeg\bin`)
   - Click "OK" on all windows

### Step 3: Install the Transcription Tool

1. Download this tool by clicking the green "Code" button above and selecting "Download ZIP"
2. Unzip the downloaded file to a folder on your computer
3. Open Command Prompt:
   - Press Windows key + R
   - Type "cmd" and press Enter
4. Navigate to the folder where you unzipped the files:
   - Type `cd C:\path\to\your\folder` (replace with the actual path)
5. Install the required packages by typing:
   ```
   pip install openai-whisper pyaudio numpy
   ```

## How to Use

1. Open Command Prompt (as described above)
2. Navigate to the folder where you unzipped the files
3. Type the following command and press Enter:
   ```
   python transcriber.py
   ```
4. The program will:
   - List available microphones
   - Ask you to select a microphone (usually just press Enter for default)
   - Begin transcribing what you say
5. Speak normally into your microphone
6. The transcription will appear on screen and be saved to a text file
7. To stop, press Ctrl+C

## Troubleshooting

If you encounter issues:

- **"PyAudio not found" error**: Try running `pip install pipwin` followed by `pipwin install pyaudio`
- **No transcription appears**: Make sure your microphone is working and not muted
- **Program crashes**: Ensure you've installed all required components

## About This Tool

This tool uses the Whisper speech recognition system developed by OpenAI. It processes audio locally on your computer, meaning your speech data stays private and doesn't require an internet connection.

The transcription quality depends on:
- Your microphone quality
- Background noise levels
- Speaking clarity

By default, this tool uses the "base.en" model which balances accuracy and performance on most computers.
