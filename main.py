import time
import numpy as np
import matplotlib.pyplot as plt

from capture_audio_output import AudioOut


def audio_receiver(data):
    #get metrics from the audio buffer
    rms = get_rms(data)
    ps, freq = get_freq(data)
    print("RMS: {}".format(rms))
    freq_max = freq[np.argmax(ps)]
    print("Fundamental Freq: {}".format(freq_max))

def get_freq(data, sf=44100):
    #fft and psd
    ft_out = np.fft.fft(data)
    ps = np.abs(ft_out)**2
    freq_bins = np.fft.fftfreq(len(data),1/sf)

    #order by frequency
    idx = np.argsort(freq_bins)
    ps = ps[idx]
    freq_bins = freq_bins[idx]

    #remove negative frequencies - for now
    ps = ps[freq_bins > 0]
    freq_bins = freq_bins[freq_bins > 0]
#    plt.plot(freq_bins, ps)
#    plt.show()
    return ps, freq_bins

def get_rms(data):
    rms = np.sqrt(np.mean(data**2))
    return rms

def main():
    audio_out_obj = AudioOut(buf_size_seconds=1.5)
    audio_out_obj.setup_audio(audio_receiver)
    audio_out_obj.start_audio()
    while audio_out_obj.is_active():
        time.sleep(60)
        audio_out_obj.stop_audio()
#    data = audio_out_obj.get_data_frames()
#    get_freq(data)
    audio_out_obj.save_audio()
    audio_out_obj.kill()

if __name__ == "__main__":
    main()
