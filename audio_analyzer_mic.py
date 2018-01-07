"""
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install python-dev python-imaging python-smbus python-alsaaudio python-pyaudio
"""

import sys
import pyaudio
from struct import unpack
import numpy as np
from sense_hat import SenseHat
import time


sense = SenseHat()
sense.clear()

sense = SenseHat()

def list_devices():
    # List all audio input devices
    p = pyaudio.PyAudio()
    i = 0
    n = p.get_device_count()
    while i < n:
        dev = p.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0:
           print(str(i)+'. '+dev['name'])
        i += 1


# Audio setup
no_channels = 1
sample_rate = 44100

# Chunk must be a multiple of 8
# NOTE: If chunk size is too small the program will crash
# with error message: [Errno Input overflowed]
chunk = 3072

list_devices()
# Use results from list_devices() to determine your microphone index
device = 2

p = pyaudio.PyAudio()
stream = p.open(format = pyaudio.paInt16,
                channels = no_channels,
                rate = sample_rate,
                input = True,
                frames_per_buffer = chunk,
                input_device_index = device)


# Colours
rotation = 0
yellow = (255, 255, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 204, 0)
e = (0, 0, 0)  # Empty
empty = [
 e, e, e, e, e, e, e, e,
 e, e, e, e, e, e, e, e,
 e, e, e, e, e, e, e, e,
 e, e, e, e, e, e, e, e,
 e, e, e, e, e, e, e, e,
 e, e, e, e, e, e, e, e,
 e, e, e, e, e, e, e, e,
 e, e, e, e, e, e, e, e,
 ]
spectrum = [green, green, green, yellow, yellow, yellow, red, red]
matrix = [0, 0, 0, 0, 0, 0, 0, 0]
power = []
weighting = [2, 8, 8, 16, 16, 32, 32, 64]
weighting = [x*8 for x in weighting]


# Return power array index corresponding to a particular frequency
def piff(val):
    return int(2 * chunk * val / sample_rate)


# Return int value for volume for fregquency range
def volume_frequency_range(power, freq_low, freq_high):
    try:
        volume = int(np.mean(power[piff(freq_low):piff(freq_high):1]))
        return volume
    except:
        return 0


def calculate_levels(data, chunk, sample_rate):
    global matrix

    # Convert raw data (ASCII string) to numpy array
    data = unpack("%dh" % (len(data) / 2), data)
    data = np.array(data, dtype='h')

    # Apply FFT - real data
    fourier = np.fft.rfft(data)
    # Remove last element in array to make it the same size as chunk
    fourier = np.delete(fourier, len(fourier) - 1)
    # Find average 'amplitude' for specific frequency ranges in Hz
    power = np.abs(fourier)
    matrix[0] = volume_frequency_range(power, 0, 156)
    matrix[1] = volume_frequency_range(power, 156, 313)
    matrix[2] = volume_frequency_range(power, 313, 625)
    matrix[3] = volume_frequency_range(power, 625, 1250)
    matrix[4] = volume_frequency_range(power, 1250, 2500)
    matrix[5] = volume_frequency_range(power, 2500, 5000)
    matrix[6] = volume_frequency_range(power, 5000, 10000)
    matrix[7] = volume_frequency_range(power, 10000, 20000)

    # Tidy up column values for the LED matrix
    matrix = np.divide(np.multiply(matrix, weighting), 1000000)
    # Set floor at 0 and ceiling at 8 for LED matrix
    # matrix = matrix.clip(0, 8)
    matrix = matrix.clip(0, 24)
    return matrix

# Main loop
while 1:
    try:
        # Get microphone data
        data = stream.read(chunk)
        matrix = calculate_levels(data, chunk, sample_rate)
        figure = empty[:]
        for y in range(0, 8):
            if matrix[y] <= 8:
                for x in range(0, matrix[y]):
                    figure[y * 8 + x] = green
            elif matrix[y] <= 16:
                for x in range(4 - (matrix[y] - 8) / 2, 4 + (matrix[y] - 8) / 2):
                    figure[y * 8 + (x - 8)] = blue
            else:
                for x in range(matrix[y], 24):
                    figure[y * 8 + (x - 16)] = red
        time.sleep(chunk / sample_rate)  # is this needed?
        sense.set_rotation(rotation)
        sense.set_pixels(figure)
    except KeyboardInterrupt:
        print("Ctrl-C Terminating...")
        stream.stop_stream()
        stream.close()
        p.terminate()
        sys.exit(1)
    except Exception, e:
        print(e)
        print("ERROR Terminating...")
        stream.stop_stream()
        stream.close()
        p.terminate()
        sys.exit(1)