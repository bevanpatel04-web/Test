"""Narration voices. A voice turns one caption-sized chunk of text into mono audio samples.

Built in:
- ``none``: no audio. The video is captions-only and the manifest says ``"narration": "none"``.
- ``flite``: CMU Flite, an offline voice that ships as a system library (libflite). It is free and
  needs no network, but it sounds robotic: use it as a scratch track for timing and review, not for release.
- ``espeak-ng``: used only if the ``espeak-ng`` (or ``espeak``) command is installed. Also robotic.

``get_voice("auto")`` picks ``$STUDIO_VOICE`` if set, else the first available offline voice, else ``none``.

Plugging in a paid text-to-speech provider (needs an API key)
------------------------------------------------------------
1. Write a class with a ``name`` (this exact string goes into the manifest's ``narration`` field) and a
   ``synthesize(text) -> (samples, sample_rate)`` method returning mono float32 samples in [-1, 1].
   Most providers accept text and return WAV or raw 16-bit PCM; ask for PCM/WAV so no decoder is needed.
2. Read the key from an environment variable (for example ``PM_TTS_API_KEY``). Never commit it, and never
   send the founder's name or email in the request.
3. Register it: ``PROVIDERS["acme-tts"] = AcmeVoice`` and add an ``available()`` classmethod that
   returns True only when the key is set.
4. Render with ``python -m studio render <slug> --voice acme-tts``. Captions stay in sync automatically,
   because every caption chunk is synthesized separately and timed from its real audio length.

Sketch (standard library only)::

    class AcmeVoice:
        name = "acme-tts"

        @classmethod
        def available(cls):
            return bool(os.environ.get("PM_TTS_API_KEY"))

        def synthesize(self, text):
            req = urllib.request.Request(
                "https://api.acme-tts.example/v1/speech",
                data=json.dumps({"text": text, "voice": "warm-1", "format": "wav", "speed": 0.95}).encode(),
                headers={"Authorization": f"Bearer {os.environ['PM_TTS_API_KEY']}",
                         "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return read_wav(r.read())

Speaking rate: aim for 130-150 words per minute. Pass the provider's speed setting, or check with
``python -m studio render <slug>``, which prints the measured words per minute.
"""
from __future__ import annotations

import ctypes
import io
import os
import re
import shutil
import subprocess
import wave

import numpy as np

# Words the offline voices read badly, and how to say them.
_SAY = [
    (re.compile(r"\b401\(k\)s?", re.I), "four oh one K"),
    (re.compile(r"\b403\(b\)s?", re.I), "four oh three B"),
    (re.compile(r"\bAI\b"), "A.I."),
    (re.compile(r"\bIRAs\b"), "I.R.A.s"),
    (re.compile(r"\bIRA\b"), "I.R.A."),
    (re.compile(r"\bAPR\b"), "A.P.R."),
    (re.compile(r"\bETFs?\b"), lambda m: "E.T.F." + ("s" if m.group(0).endswith("s") else "")),
    (re.compile(r"\be\.g\.", re.I), "for example"),
    (re.compile(r"\bvs\.?", re.I), "versus"),
    (re.compile(r"(\d+)/(\d+)/(\d+)"), r"\1, \2, \3"),
    (re.compile(r"\s*[—–]\s*"), ", "),
    (re.compile(r"…"), "..."),
]


def speakable(text: str) -> str:
    """Narration text as it should be fed to a voice (captions keep the written form)."""
    for rx, rep in _SAY:
        text = rx.sub(rep, text)
    return text


def read_wav(data: bytes) -> tuple[np.ndarray, int]:
    """Decode 16-bit PCM WAV bytes into mono float32 samples."""
    with wave.open(io.BytesIO(data)) as w:
        sr, ch, width = w.getframerate(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(w.getnframes())
    if width != 2:
        raise ValueError("expected 16-bit PCM audio")
    a = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    if ch > 1:
        a = a.reshape(-1, ch).mean(axis=1)
    return a, sr


def trim_silence(a: np.ndarray, sr: int, threshold: float = 0.01, keep: float = 0.03) -> np.ndarray:
    loud = np.flatnonzero(np.abs(a) > threshold)
    if loud.size == 0:
        return a[:0]
    pad = int(keep * sr)
    return a[max(0, loud[0] - pad): loud[-1] + pad]


class NoVoice:
    name = "none"

    @classmethod
    def available(cls) -> bool:
        return True

    def synthesize(self, text: str):
        return None


class _Wave(ctypes.Structure):
    _fields_ = [("type", ctypes.c_char_p), ("sample_rate", ctypes.c_int), ("num_samples", ctypes.c_int),
                ("num_channels", ctypes.c_int), ("samples", ctypes.POINTER(ctypes.c_short))]


class FliteVoice:
    """CMU Flite through ctypes (no command-line tool needed). Voice 'slt' (US English, female)."""

    name = "flite"
    LIB, VOICE_LIB, REGISTER = "libflite.so.1", "libflite_cmu_us_slt.so.1", "register_cmu_us_slt"
    STRETCH = 1.16   # >1 is slower; measured on the sample scripts to land at 130-150 words per minute

    @classmethod
    def available(cls) -> bool:
        try:
            ctypes.CDLL(cls.LIB)
            ctypes.CDLL(cls.VOICE_LIB)
            return True
        except OSError:
            return False

    def __init__(self, stretch: float | None = None):
        P = ctypes.c_void_p
        self.lib = lib = ctypes.CDLL(self.LIB)
        for fn, res, args in [("flite_init", ctypes.c_int, []),
                              ("flite_synth_text", P, [ctypes.c_char_p, P]),
                              ("utt_wave", ctypes.POINTER(_Wave), [P]),
                              ("delete_utterance", None, [P]),
                              ("flite_feat_set_float", None, [P, ctypes.c_char_p, ctypes.c_float])]:
            f = getattr(lib, fn)
            f.restype, f.argtypes = res, args
        lib.flite_init()
        vlib = ctypes.CDLL(self.VOICE_LIB)
        reg = getattr(vlib, self.REGISTER)
        reg.restype, reg.argtypes = P, [ctypes.c_char_p]
        self.voice = reg(None)
        if not self.voice:
            raise RuntimeError("flite voice failed to load")
        # cst_voice is {const char *name; cst_features *features; ...}: the features pointer comes second.
        features = ctypes.cast(self.voice + ctypes.sizeof(P), ctypes.POINTER(P)).contents.value
        lib.flite_feat_set_float(features, b"duration_stretch", stretch or self.STRETCH)

    def synthesize(self, text: str) -> tuple[np.ndarray, int]:
        utt = self.lib.flite_synth_text(speakable(text).encode("utf-8", "ignore"), self.voice)
        try:
            w = self.lib.utt_wave(utt).contents
            n = w.num_samples * max(1, w.num_channels)
            a = np.ctypeslib.as_array(w.samples, shape=(n,)).astype(np.float32) / 32768.0
            if w.num_channels > 1:
                a = a.reshape(-1, w.num_channels).mean(axis=1)
            sr = w.sample_rate
        finally:
            self.lib.delete_utterance(utt)
        return trim_silence(a, sr), sr


class EspeakVoice:
    name = "espeak-ng"

    @staticmethod
    def _bin():
        return shutil.which("espeak-ng") or shutil.which("espeak")

    @classmethod
    def available(cls) -> bool:
        return cls._bin() is not None

    def synthesize(self, text: str) -> tuple[np.ndarray, int]:
        out = subprocess.run([self._bin(), "-v", "en-us", "-s", "140", "--stdout", speakable(text)],
                             capture_output=True, check=True).stdout
        a, sr = read_wav(out)
        return trim_silence(a, sr), sr


PROVIDERS = {"none": NoVoice, "flite": FliteVoice, "espeak-ng": EspeakVoice}
OFFLINE_ORDER = ["flite", "espeak-ng"]


def available() -> list[str]:
    return [name for name, cls in PROVIDERS.items() if cls.available()]


def get_voice(name: str = "auto"):
    if name == "auto":
        name = os.environ.get("STUDIO_VOICE") or next((n for n in OFFLINE_ORDER if PROVIDERS[n].available()), "none")
    if name not in PROVIDERS:
        raise ValueError(f"Unknown voice {name!r}. Choose from: {', '.join(PROVIDERS)}")
    if not PROVIDERS[name].available():
        raise RuntimeError(f"Voice {name!r} is not available on this machine. Available: {', '.join(available())}")
    return PROVIDERS[name]()
