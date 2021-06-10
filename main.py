import time
import numpy as np
from scipy import signal

from capture_audio_output import AudioOut
from PySpace.fractal_generator import FractalGen

rms = None
freq_max = None
freq_second = None
bass_drum_power = None
high_hat_drum_power = None
maxi_test = None
mini_test = None
bass_drum_mod_data = []
high_hat_drum_mod_data = []

def audio_receiver(data):
    global rms, freq_max, freq_second, bass_drum_power, high_hat_drum_power

    #get metrics from the audio buffer
    rms = get_rms(data)
    ps, freq = get_freq(data)
    freq_max = float(freq[np.argmax(ps)])
    freq_second = float(freq[np.argsort(ps)[-2]])
    #bass frequency range
    bass_start = 25
    bass_end = 100
    bass_drum_power = float(np.sum(ps[(freq > bass_start) & (freq < bass_end)]))
    #high hat frequency range
    high_hat_start = 3000
    high_hat_end = 5000
    high_hat_drum_power = float(np.sum(ps[(freq > high_hat_start) & (freq < high_hat_end)]))


def slide_buf(arr, data, size):
    """
    arr - byte array
    data - byte array
    """
    arr.append(data)
    arr = arr[-size:]
    return arr

def butter_lowpass(self, cutoff, nyq_freq, order=4):
    normal_cutoff = float(cutoff) / nyq_freq
    b, a = signal.butter(order, normal_cutoff, btype='lowpass')
    return b, a

def butter_lowpass_filter(self, data, cutoff_freq, nyq_freq, order=4):
    # Source: https://github.com/guillaume-chevalier/filtering-stft-and-laplace-transform
    b, a = self.butter_lowpass(cutoff_freq, nyq_freq, order=order)
    y = signal.filtfilt(b, a, data)
    return y

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
    global rms, freq_max, freq_second, bass_drum_power, maxi_test, mini_test, bass_drum_mod_data, high_hat_drum_power, high_hat_drum_mod_data
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
#            param_2_in_mini = 238
#            param_2_in_maxi = 1040
            #param_2_out_mini = 1.38
            #param_2_out_maxi = 1.8
            #bass drum mod
            param_2_in_mini = 238
            param_2_in_maxi = 1040
            #param_2_out_mini = 1.38
            #param_2_out_maxi = 1.8
            param_2_out_mini = -0.15
            param_2_out_maxi = 1.0
            param_2_input = freq_max
            if (param_2_input > param_2_in_maxi) or (param_2_input < param_2_in_mini):
                param_2 = None
            else:
                param_2 = (((param_2_input - param_2_in_mini) / (param_2_in_maxi - param_2_in_mini)) * (param_2_out_maxi - param_2_out_mini)) + param_2_out_mini
            print("MAIN VAR 2 {}".format(param_2))
            #fractal_gen.set_parameters([None, param_2, None, None, None, None])
            #fractal_gen.set_parameters([None, param_2, None, None, None, None])
            #show bass drum frequency range
            bass_maxi_power = 250049633408.59158
            bass_mini_power = 10292767.610073969
            bass_drum_mod = (((bass_drum_power  - bass_mini_power) / (bass_maxi_power - bass_mini_power)) * (param_2_out_maxi - param_2_out_mini)) + param_2_out_mini
            bass_drum_mod_data = slide_buf(bass_drum_mod_data, bass_drum_mod, 2)
            bass_drum_mod_avg = float(np.mean(bass_drum_mod_data))


            print("BASS_DRUM_MOD: {}".format(bass_drum_mod))
            if (maxi_test is None) or (maxi_test < bass_drum_mod):
                maxi_test = bass_drum_mod
            if (mini_test is None) or (mini_test > bass_drum_mod):
                mini_test = bass_drum_mod

            #high hat mod
            high_hat_mod_out_mini = 1.55
            high_hat_mod_out_maxi = 1.75
            print("{} high hat power".format(high_hat_drum_power))
            high_hat_maxi_power = 223692925374.54117
            high_hat_mini_power = 30769546.72759982
            high_hat_drum_mod = (((high_hat_drum_power  - high_hat_mini_power) / (high_hat_maxi_power - high_hat_mini_power)) * (high_hat_mod_out_maxi - high_hat_mod_out_mini)) + high_hat_mod_out_mini
            high_hat_drum_mod_data = slide_buf(high_hat_drum_mod_data, high_hat_drum_mod, 2)
            high_hat_drum_mod_avg = float(np.mean(high_hat_drum_mod_data))

            fractal_gen.set_parameters([None, high_hat_drum_mod_avg, bass_drum_mod_avg, None, None, None])
        time.sleep(0.016)
        print("Maxi: {}. Mini: {}".format(maxi_test, mini_test))

    #end audio object
    audio_out_obj.stop_audio()
    frames = audio_out_obj.get_data_frames()
    audio_out_obj.save_audio()
    audio_out_obj.kill()

if __name__ == "__main__":
    main()
