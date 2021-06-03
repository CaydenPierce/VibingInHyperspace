"""
Monitor a loopback monitor so we get a signal which is the computer's audio output.

This code based on : https://stackoverflow.com/questions/26573556/record-speakers-output-with-pyaudio

Must first set things up by running:
`pacmd load-module module-loopback latency_msec=5`
Then go to `pavucontrol`, input devices, uncheck default and check the monitor of the default.
That's it. More detailed instructions available in the SO link above
"""


import pyaudio
import wave
import time
import numpy as np

class AudioOut:
    def __init__(self, buf_size_seconds=3):
        #settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.sample_size = pyaudio.get_sample_size(self.FORMAT)
        self.BUF_SIZE = int(self.RATE * buf_size_seconds * self.sample_size)

        #data savers
        self.buf_frames = bytearray()

        #pyaudio objects
        self.p = None
        self.stream = None

    def slide_buf(self, arr, data):
        """
        arr - byte array
        data - byte array
        """
        arr.extend(data)
        arr = arr[-self.BUF_SIZE:]
        return arr

    def setup_audio(self, callback=None):
        self.p = pyaudio.PyAudio()

        if callback is None:
            callback = self.record_chunk_callback_default

        self.stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK, 
                        stream_callback=callback)

    def start_audio(self):
        self.stream.start_stream()

    def record_audio(self, num_seconds=1):
        frames = []
        for i in range(0, int(self.RATE / self.CHUNK * num_seconds)):
            data = self.stream.read(self.CHUNK)
            frames.append(data)
        return frames

    def stop_audio(self):
        self.stream.stop_stream()

    def kill(self):
        self.stream.close()
        self.p.terminate()

    def save_audio(self, output_filename="output.wav"):
        wf = wave.open(output_filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        #wf.writeframes(b''.join(self.buf_frames))
        wf.writeframes(self.buf_frames)
        wf.close()

    def record_chunk_callback_default(self, in_data, frame_count, time_info, status):
        self.buf_frames = self.slide_buf(self.buf_frames, in_data)
        return (in_data, pyaudio.paContinue)

    def is_active(self):
        try:
            return self.stream.is_active()
        except:
            return False

    def get_data_frames(self):
        return self.buf_frames

def main():
    audio_out_obj = AudioOut()
    audio_out_obj.setup_audio()
    audio_out_obj.start_audio()
    while audio_out_obj.is_active():
        time.sleep(10)
        audio_out_obj.stop_audio()
    audio_out_obj.save_audio()
    audio_out_obj.kill()

if __name__ == "__main__":
    main()
