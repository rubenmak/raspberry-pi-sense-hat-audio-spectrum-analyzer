# raspberry-pi-sense-hat-audio-spectrum-analyzer
python code to analyze audio spectrum using the LED matrix of the Raspberry Pi sense HAT

This code is a modification of https://www.rototron.info/raspberry-pi-spectrum-analyzer/.
It's modified to work with the LED matrix of the sense HAT.

You can either play a wav file from the pi, or use a microphone. I used this USB microphone:

http://www.dx.com/p/mi-305-plug-and-play-mini-usb-microphone-black-287434#.WlJ5qt-nFPY

but any mic that works with the Raspberry Pi should be working.

## install dependencies
```
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install python-dev python-imaging python-smbus python-alsaaudio sense-hat python-numpy
```

and for using the microphone:

`sudo apt-get install python-pyaudio`

## running
For playing a wav file:
`python audio_analyzer_wav.py /path/to/wav/file`

This version has a somewhat more creative LED visualisation:
`python audio_analyzer_disco_wav.py /path/to/wav/file`

And this version uses the microphone:
`python audio_analyzer_mic.py`

## orientation
The default orientation of the sense HAT is, with the GPIO 
connection on top, the left side being the bottom of the visualisation.
When mounted on the pi, it means you need point the USB-ports
upward for the correct orientation.

If you want to position differently, change the `rotation = 0` 
in the code to 90, 180 or 270.
