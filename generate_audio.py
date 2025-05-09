from pydub import AudioSegment
from pydub.generators import Sine


def warm_chime(freq, duration=300, shimmer=True):
    base = Sine(freq).to_audio_segment(duration=duration)
    overtone1 = Sine(freq * 2).to_audio_segment(duration=duration).apply_gain(-9)
    tone = base.overlay(overtone1)

    if shimmer:
        shimmer = Sine(3000).to_audio_segment(duration=duration).apply_gain(-18)
        tone = tone.overlay(shimmer)

    return tone.fade_in(100).fade_out(200)


# Use major 3rd interval for harmony (e.g. 660 Hz and ~528 Hz)
ding = warm_chime(660)      # Slightly brighter "ding"
dong = warm_chime(528)      # Slightly deeper, harmonic "dong"

# Combine with natural pacing
pause = AudioSegment.silent(duration=100)
dingdong = ding + pause + dong

# Optional: very soft echo
echo = dingdong - 25
dingdong = dingdong.overlay(echo, position=600)

# Export
dingdong.export("welcoming_dingdong.mp3", format="mp3")
