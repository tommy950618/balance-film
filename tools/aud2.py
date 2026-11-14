import sys
import numpy as np, soundfile as sf, librosa
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
x, sr = sf.read(sys.argv[1]); out = sys.argv[2]
if x.ndim > 1:
    L, R = x[:, 0], x[:, 1]
    print('stereo corr L/R %.4f, side/mid energy %.4f' % (np.corrcoef(L, R)[0, 1], np.sum((L - R) ** 2) / max(np.sum((L + R) ** 2), 1e-9)))
    m = x.mean(axis=1)
else:
    m = x
print('duration %.2f s, peak %.3f (%.1f dBFS), rms %.1f dBFS' % (len(m) / sr, np.abs(m).max(), 20 * np.log10(np.abs(m).max() + 1e-9), 20 * np.log10(np.sqrt(np.mean(m ** 2)) + 1e-9)))
hop = int(sr * 0.25)
print('rms per 0.25 s (dBFS):')
print(' '.join('%.0f' % (20 * np.log10(np.sqrt(np.mean(m[i:i + hop] ** 2)) + 1e-9)) for i in range(0, len(m) - hop + 1, hop)))
S_ = np.abs(librosa.stft(m, n_fft=2048, hop_length=512)); f = librosa.fft_frequencies(sr=sr, n_fft=2048); t = librosa.frames_to_time(np.arange(S_.shape[1]), sr=sr, hop_length=512)
H, P = librosa.decompose.hpss(S_, margin=2.0)
print('harmonic share of energy %.2f, percussive %.2f' % ((H ** 2).sum() / (S_ ** 2).sum(), (P ** 2).sum() / (S_ ** 2).sum()))
bands = [(40, 150), (150, 400), (400, 1500), (1500, 4000), (4000, 10000)]
for t0, t1 in [(0, 2.6), (2.7, 5.7), (5.8, 8.0), (8.0, 10.0)]:
    sel = (t >= t0) & (t < t1)
    e = [10 * np.log10((S_[(f >= a) & (f < b)][:, sel] ** 2).mean() + 1e-12) for a, b in bands]
    print('%.1f-%.1f s band levels dB (40-150,150-400,400-1.5k,1.5-4k,4-10k): %s' % (t0, t1, ' '.join('%.0f' % v for v in e)))
fig, ax = plt.subplots(2, 1, figsize=(13, 6.5), gridspec_kw=dict(height_ratios=[3, 1]))
M = librosa.amplitude_to_db(librosa.feature.melspectrogram(S=S_ ** 2, sr=sr, n_mels=128, fmax=12000), ref=np.max)
ax[0].imshow(M, origin='lower', aspect='auto', extent=[0, len(m) / sr, 0, 128], cmap='magma', vmin=-70, vmax=0); ax[0].set_ylabel('mel bin'); ax[0].set_title('mel spectrogram')
tt = np.arange(len(m)) / sr; ax[1].plot(tt, m, lw=0.4); ax[1].set_xlim(0, len(m) / sr); ax[1].set_xlabel('s')
for a in ax: a.set_xticks(np.arange(0, 10.5, 0.5))
plt.tight_layout(); plt.savefig(out, dpi=95); print(out)
