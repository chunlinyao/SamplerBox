"""PyAudio Example: Play a wave file (callback version)"""

import pyaudio
import wave
import time
import sys
import sounddevice
import random
sounddevice.query_devices()

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')

p = pyaudio.PyAudio()
print wf.getnchannels()
def callback(in_data, frame_count, time_info, status):
    data = wf.readframes(frame_count)
    print frame_count
    print frame_count * 2 * 2
    print "--------------------"
    data= chr(random.randint(1,255))*2048
    return (data, pyaudio.paContinue)
print 'XXX'
print wf.getsampwidth()
stream = p.open(format=pyaudio.paInt16, #p.get_format_from_width(2),
                channels=2, #wf.getnchannels(),
                rate=44100,
                frames_per_buffer= 512,
                output=True,
                stream_callback=callback)

stream.start_stream()

while stream.is_active():
    time.sleep(0.1)

stream.stop_stream()
stream.close()
wf.close()

p.terminate()
