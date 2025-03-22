import pyaudio
import wave
import numpy as np
import threading
import queue
import tempfile
import os
from datetime import datetime
import time
import whisper  # OpenAI's Whisper library

class RealtimeTranscriber:
    def __init__(self):
        # Load the Whisper model
        print("Loading Whisper model... This may take a moment.")
        self.model = whisper.load_model("large-v3-turbo")  # You can use "tiny", "base", "small", "medium", or "large"
        print("Model loaded successfully!")
        
        # Audio recording parameters
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.RECORD_SECONDS = 3  # Process audio in 3-second chunks
        
        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        
        # Create a queue for audio chunks
        self.audio_queue = queue.Queue()
        
        # Flag to control recording
        self.is_recording = False
        
        # Output file setup
        self.output_filename = f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        print(f"Transcription will be saved to: {self.output_filename}")
        
        # Create the output file with a header
        with open(self.output_filename, 'w') as f:
            f.write(f"--- Transcription started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n\n")

    def callback(self, in_data, frame_count, time_info, status):
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        self.audio_queue.put(audio_data)
        return (in_data, pyaudio.paContinue)

    def process_audio(self):
        while self.is_recording:
            if self.audio_queue.qsize() >= int(self.RATE * self.RECORD_SECONDS / self.CHUNK):
                # Get accumulated audio data
                audio_data = []
                for _ in range(int(self.RATE * self.RECORD_SECONDS / self.CHUNK)):
                    audio_data.extend(self.audio_queue.get())
                
                # Convert to numpy array
                audio_array = np.array(audio_data, dtype=np.int16)
                
                # Save temporary WAV file
                try:
                    temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                    temp_wav_name = temp_wav.name
                    temp_wav.close()  # Close it explicitly for Windows compatibility
                    
                    with wave.open(temp_wav_name, 'wb') as wf:
                        wf.setnchannels(self.CHANNELS)
                        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
                        wf.setframerate(self.RATE)
                        wf.writeframes(audio_array.tobytes())
                    
                    # Transcribe using Whisper Python model
                    try:
                        result = self.model.transcribe(temp_wav_name, fp16=False)
                        transcribed_text = result["text"].strip()
                        
                        if transcribed_text:
                            print(transcribed_text)
                            
                            # Append to output file
                            with open(self.output_filename, 'a') as f:
                                f.write(transcribed_text + "\n")
                    except Exception as e:
                        error_msg = f"Transcription error: {str(e)}"
                        print(error_msg)
                        with open(self.output_filename, 'a') as f:
                            f.write(f"Error: {error_msg}\n")
                
                except Exception as e:
                    error_msg = f"Transcription error: {str(e)}"
                    print(error_msg)
                    with open(self.output_filename, 'a') as f:
                        f.write(f"Error: {error_msg}\n")
                
                # Clean up temporary file
                try:
                    if os.path.exists(temp_wav_name):
                        os.unlink(temp_wav_name)
                except Exception as e:
                    print(f"Error deleting temporary file: {e}")
            else:
                # Sleep a bit to prevent CPU hogging
                time.sleep(0.1)

    def start_transcription(self):
        print("Testing microphone...")
        # Find the correct input device
        info = self.p.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        
        # List all audio devices
        print("\nAvailable input devices:")
        default_input_device = None
        for i in range(num_devices):
            device_info = self.p.get_device_info_by_host_api_device_index(0, i)
            if device_info.get('maxInputChannels') > 0:
                print(f"  Device {i}: {device_info.get('name')}")
                if device_info.get('defaultSampleRate') == self.RATE:
                    default_input_device = i
                    print(f"    (This device supports {self.RATE}Hz - recommended)")
        
        # Let user select input device
        selected_device = None
        while selected_device is None:
            try:
                selection = input(f"\nSelect input device (0-{num_devices-1}) or press Enter for default: ")
                if not selection and default_input_device is not None:
                    selected_device = default_input_device
                elif not selection:
                    selected_device = self.p.get_default_input_device_info()['index']
                else:
                    device_index = int(selection)
                    if 0 <= device_index < num_devices:
                        device_info = self.p.get_device_info_by_host_api_device_index(0, device_index)
                        if device_info.get('maxInputChannels') > 0:
                            selected_device = device_index
                        else:
                            print("Selected device has no input channels. Please select another.")
                    else:
                        print(f"Please enter a number between 0 and {num_devices-1}")
            except ValueError:
                print("Please enter a valid number")
        
        print(f"Using input device: {self.p.get_device_info_by_index(selected_device)['name']}")
        
        print("\nOpening audio stream...")
        stream = self.p.open(format=self.FORMAT,
                           channels=self.CHANNELS,
                           rate=self.RATE,
                           input=True,
                           input_device_index=selected_device,
                           frames_per_buffer=self.CHUNK,
                           stream_callback=self.callback)
        
        print("\nStarting transcription with Whisper... Speak into your microphone!")
        print("The transcription will be shown here and saved to the output file simultaneously.")
        print("Press Ctrl+C to stop.")
        
        self.is_recording = True
        stream.start_stream()
        
        # Start processing thread
        processing_thread = threading.Thread(target=self.process_audio)
        processing_thread.start()
        
        try:
            while True:
                if stream.is_active():
                    threading.Event().wait(1)
        except KeyboardInterrupt:
            print("\nStopping transcription...")
            self.is_recording = False
            processing_thread.join()
            stream.stop_stream()
            stream.close()
            self.p.terminate()
            
            # Add a footer to the output file
            with open(self.output_filename, 'a') as f:
                f.write(f"\n--- Transcription ended at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
            
            print(f"Transcription stopped. Output saved to {self.output_filename}")

if __name__ == "__main__":
    transcriber = RealtimeTranscriber()
    transcriber.start_transcription()
