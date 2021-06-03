import time

from capture_audio_output import AudioOut

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
