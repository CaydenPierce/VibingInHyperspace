import time
import numpy as np

from capture_audio_output import AudioOut
from PySpace.fractal_generator import FractalGen

rms = None
freq_max = None
freq_second = None

def audio_receiver(data):
    global rms, freq_max, freq_second
    #get metrics from the audio buffer
    rms = get_rms(data)
    ps, freq = get_freq(data)
    freq_max = float(freq[np.argmax(ps)])
    freq_second = float(freq[np.argsort(ps)[-2]])

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
    return ps, freq_bins

def get_rms(data):
    rms = float(np.sqrt(np.mean(data**2)))
    return rms

def main():
    global rms, freq_max, freq_second
    running = True
    #setup audio recording with callback
    audio_out_obj = AudioOut(buf_size_seconds=0.05)
    audio_out_obj.setup_audio(audio_receiver)
    audio_out_obj.start_audio()

    #setup fractal
    fractal_gen = FractalGen()
    fractal_gen.fractal_setup()

    while running and audio_out_obj.is_active():
        fractal_gen.gen_fractal_frame()
        if rms is not None:
            #param_1 == any value
            #param_3 == between -0.23 and 1.1
            param_2_in_mini = 238
            param_2_in_maxi = 1040
            param_2_out_mini = 1.38
            param_2_out_maxi = 1.8
            param_2_input = freq_max
            if (param_2_input > param_2_in_maxi) or (param_2_input < param_2_in_mini):
                param_2 = None
            else:
                param_2 = (((param_2_input - param_2_in_mini) / (param_2_in_maxi - param_2_in_mini)) * (param_2_out_maxi - param_2_out_mini)) + param_2_out_mini
            print("MAIN VAR 2 {}".format(param_2))
            fractal_gen.set_parameters([None, param_2, None, None, None, None])
        time.sleep(0.016)

    #end audio object
    audio_out_obj.stop_audio()
    frames = audio_out_obj.get_data_frames()
    audio_out_obj.save_audio()
    audio_out_obj.kill()

if __name__ == "__main__":
    main()
