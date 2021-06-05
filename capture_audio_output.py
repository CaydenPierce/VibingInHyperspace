"""
Select an audio device (JACK system) and record it in callback mode using PyAudio
"""

import pyaudio
import wave
import time
import numpy as np
import sys
import struct

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

        #user optional callback on new chunk
        self.user_callback = None

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

        if callback is not None:
            self.user_callback = callback

        #Select JACK system output as device
        port_num = None
        for i in range(0, self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            if (info["name"] == "system"):
                if (self.p.get_host_api_info_by_index(info["hostApi"])["name"] == "JACK Audio Connection Kit"):
                    port_num = i
                    break
        if port_num is None:
            print("\n\nJACK not properly configured. See INSTALL section in README. Exiting.")
            sys.exit()

        self.stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK, 
                        input_device_index=8,
                        stream_callback=self.record_chunk_callback_default)

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

        #pass data to the creator of this class, if they want it
        if self.user_callback is not None:
            self.user_callback(self.parse_data_to_numpy(self.buf_frames))

        return (in_data, pyaudio.paContinue)

    def is_active(self):
        try:
            return self.stream.is_active()
        except:
            return False

    def get_data_frames(self):
        return self.buf_frames

    def parse_data_to_numpy(self, data):
        int_data = struct.unpack_from("<{}h".format(self.CHUNK), data)
        int_data = np.asarray(int_data)
        return int_data

def main():
    audio_out_obj = AudioOut()
    audio_out_obj.setup_audio()
    audio_out_obj.start_audio()
    while audio_out_obj.is_active():
        time.sleep(13)
        audio_out_obj.stop_audio()
    audio_out_obj.save_audio()
    audio_out_obj.kill()

if __name__ == "__main__":
    main()
