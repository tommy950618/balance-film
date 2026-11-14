"""ASR for one wav: python asr2.py in.wav  -> prints VAD segments with text/lang/emotion/event."""
import sys, wave
import numpy as np
import sherpa_onnx
S = '/tmp/claude-0/-home-claude/aa3a062b-30d6-5b6d-b0fb-3d0d2e95938b/scratchpad'
M = S + '/asr_model/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17'
w = wave.open(sys.argv[1]); sr = w.getframerate()
x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
rec = sherpa_onnx.OfflineRecognizer.from_sense_voice(model=M + '/model.int8.onnx', tokens=M + '/tokens.txt', num_threads=1, use_itn=True, language='auto')
cfg = sherpa_onnx.VadModelConfig()
cfg.silero_vad.model = S + '/asr_model/silero_vad.onnx'
cfg.silero_vad.min_silence_duration = 0.25
cfg.silero_vad.min_speech_duration = 0.15
cfg.silero_vad.max_speech_duration = 12
cfg.silero_vad.threshold = 0.35
cfg.sample_rate = sr
vad = sherpa_onnx.VoiceActivityDetector(cfg, buffer_size_in_seconds=60)
win = cfg.silero_vad.window_size
def drain():
    while not vad.empty():
        seg = vad.front
        st = rec.create_stream(); st.accept_waveform(sr, seg.samples); rec.decode_stream(st)
        r = st.result
        print('VAD %.2f-%.2f | %s | lang=%s emo=%s event=%s' % (seg.start / sr, (seg.start + len(seg.samples)) / sr, r.text, getattr(r, 'lang', ''), getattr(r, 'emotion', ''), getattr(r, 'event', '')))
        vad.pop()
for i in range(0, len(x) - win, win):
    vad.accept_waveform(x[i:i + win]); drain()
vad.flush(); drain()
# whole clip in one pass too (catches quiet speech the VAD drops)
st = rec.create_stream(); st.accept_waveform(sr, x); rec.decode_stream(st)
r = st.result
print('WHOLE | %s | lang=%s emo=%s event=%s' % (r.text, getattr(r, 'lang', ''), getattr(r, 'emotion', ''), getattr(r, 'event', '')))
