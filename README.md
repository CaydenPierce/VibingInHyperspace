# V I B I N  I N  H Y P E R S P A C E

### Description  

This repo is a vision of a musical expression environment where music becomes a multi-sensory experience, where the audience becomes the musician, where the musical expression becomes an object.

## Technical Description  

Live modulating virtual reality 3D hyperdimensional fractals with multiple streams of audio and brain wave data.

## Install

This runs in Ubuntu 20 with Python 3.8.

```
sudo apt install portaudio19-dev python3-pyaudio
pip3 install -r requirements.txt
```

To get MIDI devices to work in DAW and to record output with PyAudio at the same time, some setup is required.

1. Install linux low latency kernel
2. Install JACK - `sudo apt-get install jackd2 qjackctl`
3. Configure JACK to use low latency - https://jackaudio.org/faq/linux_rt_config.html
4. Configure pulseaudio to send audio through JACK by running `qjackctl` -> Settings -> 'Execute on startup' -> Paste the line `pacmd set-default-sink jack_out; a2jmidid -e &`
5. Setup pulseaudio to use the JACK sink as the input device (so we can record our computer outpuit). Run `pavucontrol` -> Input Devices -> Uncheck the default and check 'Monitor of JACK sink'
6. Start JACK -> `qjackctl` -> Start

## Run 

```
python3 main.py
```

## Credit

PySpace: https://github.com/HackerPoet/PySpace - Thanks to HackerPoet for building the beautiful ray marching 3D fractal implementation that is driving the fractal generation.

## TODO

What works now:
- receive input from all sinks and sources in JACK and pulseaudio, including MIDI devices
- generate a 3d fractal using PySpace
- modulate the fractal with simple metrics from the music like RMS, bass freq range power, hi hat freq range power

What we need:
- signal processing pipeline that holds a rolling window of the last n seconds of the song, constantly recomputes metrics on that (fundamental frequency, RMS, bass freq power, hi hat freq power, etc) and their respective maximums and minimums over the last n seconds, and 
- "art" classes - need to abstract a fractals definition (i.e. it's pyspace function, number of available editable variables/parameters, and the range of the values that each parameters can take on 
- connect BCI to also visualize the audience/musician's RESPONSE to the music
