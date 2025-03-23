import wave
import struct
import os

def create_silent_wav():
    # Ensure the sounds directory exists
    os.makedirs('assets/sounds', exist_ok=True)
    
    # Create a new WAV file
    with wave.open('assets/sounds/background.wav', 'w') as wav_file:
        # Set parameters
        nchannels = 2  # Stereo
        sampwidth = 2  # 2 bytes per sample
        framerate = 44100  # Standard sample rate
        nframes = framerate * 5  # 5 seconds duration
        comptype = 'NONE'
        compname = 'not compressed'
        
        # Set the parameters
        wav_file.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))
        
        # Write silence (all zeros)
        for _ in range(nframes):
            wav_file.writeframes(struct.pack('h', 0) * nchannels)

if __name__ == "__main__":
    create_silent_wav()