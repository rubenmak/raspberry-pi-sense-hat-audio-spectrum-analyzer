"""
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install python-dev python-imaging python-smbus
sudo apt-get install python-alsaaudio
"""

import sys
import alsaaudio as aa
import wave
from struct import unpack
import numpy as np
from sense_hat import SenseHat
import time


# initialize sense HAT
sense = SenseHat()
sense.clear()

# Audio setup
wavfile_path = str(sys.argv[1])
wavfile = wave.open(wavfile_path, 'r')
sample_rate = wavfile.getframerate()
no_channels = wavfile.getnchannels()
chunk = 4096  # Use a multiple of 8

# ALSA
output = aa.PCM(aa.PCM_PLAYBACK, aa.PCM_NORMAL)
output.setchannels(no_channels)
output.setrate(sample_rate)
output.setformat(aa.PCM_FORMAT_S16_LE)
output.setperiodsize(chunk)

# Colours
rotation = 0
sense.set_rotation(rotation)
yellow = (255, 255, 0)  # Yellow
red = (255, 0, 0)  # Red
green = (0, 204, 0)  # Green
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


def calculate_levels(data):
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
    matrix[5] = volume_frequency_range(power, 2500, 2750)
    matrix[6] = volume_frequency_range(power, 2750, 5000)
    matrix[7] = volume_frequency_range(power, 5000, 10000)

    # Tidy up column values for the LED matrix
    matrix = np.divide(np.multiply(matrix, weighting), 1000000)
    # Set floor at 0 and ceiling at 8 for LED matrix
    matrix = matrix.clip(0, 8)
    return matrix


# Start reading .wav file
data = wavfile.readframes(chunk)

# Loop while audio data present
while data != '':
    output.write(data)
    matrix = calculate_levels(data)
    figure = empty[:]
    for y in range(0, 8):
        for x in range(0, matrix[y]):
            figure[y * 8 + x] = spectrum[x]
        sense.set_pixels(figure)
    data = wavfile.readframes(chunk)
