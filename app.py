import io
import os
import subprocess
import tempfile
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from audio_stego_utils import (
    encode_message_in_wav,
    decode_message_from_wav,
    encode_message_in_mp3,
    decode_message_from_mp3
)

st.set_page_config(page_title="Audio Steganography App", layout="centered")
st.title("🔊 Audio Steganography App with Encryption 🔐")
st.subheader("🔊 Audio Steganography")

menu = st.radio("Choose Operation", ["Encode Audio 🔏", "Decode Audio 🔓"])

def _to_mono(samples):
    if isinstance(samples, np.ndarray) and samples.ndim > 1:
        return samples.mean(axis=1)
    return samples

def _run_ffmpeg(input_path, output_path):
    try:
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, "-f", "wav", output_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
    except FileNotFoundError as e:
        raise ValueError("FFmpeg not found. Add ffmpeg to packages.txt.") from e
    if result.returncode != 0:
        raise ValueError("FFmpeg failed to decode MP3 for waveform plotting.")

def _mp3_bytes_to_wav_samples(file_bytes):
    mp3_path = None
    wav_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as mp3_tmp:
            mp3_tmp.write(file_bytes)
            mp3_path = mp3_tmp.name
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_tmp:
            wav_path = wav_tmp.name
        _run_ffmpeg(mp3_path, wav_path)
        sample_rate, data = wavfile.read(wav_path)
        return sample_rate, _to_mono(data)
    finally:
        for path in (mp3_path, wav_path):
            if path and os.path.exists(path):
                os.remove(path)

def _mp3_path_to_wav_samples(mp3_path):
    wav_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_tmp:
            wav_path = wav_tmp.name
        _run_ffmpeg(mp3_path, wav_path)
        sample_rate, data = wavfile.read(wav_path)
        return sample_rate, _to_mono(data)
    finally:
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)

def _load_samples_from_bytes(file_bytes, file_ext):
    if file_ext == ".wav":
        sample_rate, data = wavfile.read(io.BytesIO(file_bytes))
        return sample_rate, _to_mono(data)
    if file_ext == ".mp3":
        return _mp3_bytes_to_wav_samples(file_bytes)
    raise ValueError("Unsupported audio format for plotting.")

def _load_samples_from_path(path, file_ext):
    if file_ext == ".wav":
        sample_rate, data = wavfile.read(path)
        return sample_rate, _to_mono(data)
    if file_ext == ".mp3":
        return _mp3_path_to_wav_samples(path)
    raise ValueError("Unsupported audio format for plotting.")

def _plot_waveform(samples, sample_rate, title):
    max_seconds = 5
    max_samples = min(len(samples), int(sample_rate * max_seconds))
    if max_samples <= 0:
        raise ValueError("Audio is too short to plot.")
    samples = samples[:max_samples]
    times = np.arange(max_samples) / sample_rate
    fig, ax = plt.subplots(figsize=(7, 2.4))
    ax.plot(times, samples, linewidth=0.6, color="#1f77b4")
    ax.set_title(title)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    return fig

def _plot_before_after(before, after, sr_before, sr_after, title_before, title_after):
    col1, col2 = st.columns(2)
    with col1:
        st.pyplot(_plot_waveform(before, sr_before, title_before))
    with col2:
        st.pyplot(_plot_waveform(after, sr_after, title_after))

# ---------------- Encode ----------------
if menu == "Encode Audio 🔏":
    uploaded_audio = st.file_uploader("Upload a WAV or MP3 file", type=["wav", "mp3"])
    secret_text = st.text_area("Enter the secret message for audio")
    secret_key = st.text_input("Enter a secret key", type="password")

    if uploaded_audio and secret_text and secret_key:
        try:
            file_bytes = uploaded_audio.read()
            file_ext = os.path.splitext(uploaded_audio.name)[1].lower()

            if file_ext == ".wav":
                stego_path = encode_message_in_wav(io.BytesIO(file_bytes), secret_text, secret_key)
            elif file_ext == ".mp3":
                stego_path = encode_message_in_mp3(io.BytesIO(file_bytes), secret_text, secret_key)
            else:
                raise ValueError("Unsupported audio format. Only .wav or .mp3 allowed.")

            with open(stego_path, "rb") as f:
                st.download_button(
                    "⬇️ Download Stego Audio",
                    f,
                    file_name="stego_audio" + uploaded_audio.name[-4:],
                    mime="audio/wav" if stego_path.endswith(".wav") else "audio/mpeg"
                )

            st.audio(
                stego_path,
                format="audio/wav" if stego_path.endswith(".wav") else "audio/mpeg"
            )
            st.success("✅ Message hidden successfully in audio!")
            st.markdown("Waveforms before and after encryption should appear the same to show the audio is not visibly altered.")

            try:
                sr_before, samples_before = _load_samples_from_bytes(file_bytes, file_ext)
                sr_after, samples_after = _load_samples_from_path(stego_path, file_ext)
                _plot_before_after(
                    samples_before,
                    samples_after,
                    sr_before,
                    sr_after,
                    "Before Encryption (Original)",
                    "After Encryption (Stego)"
                )
            except Exception as e:
                st.warning(f"Waveform plot unavailable: {e}")

        except Exception as e:
            st.error(f"❌ Error: {e}")

# ---------------- Decode ----------------
elif menu == "Decode Audio 🔓":
    uploaded_audio = st.file_uploader("Upload stego audio file (WAV or MP3)", type=["wav", "mp3"])
    secret_key = st.text_input("Enter the secret key", type="password")

    if uploaded_audio and secret_key:
        try:
            file_bytes = uploaded_audio.read()
            file_ext = os.path.splitext(uploaded_audio.name)[1].lower()

            if file_ext == ".wav":
                message = decode_message_from_wav(io.BytesIO(file_bytes), secret_key)
            elif file_ext == ".mp3":
                message = decode_message_from_mp3(io.BytesIO(file_bytes), secret_key)
            else:
                raise ValueError("Unsupported audio format. Only .wav or .mp3 allowed.")

            st.success("📝 Hidden Message:")
            st.code(message)
            st.markdown("Decryption extracts the hidden text without changing the audio, so the waveform remains the same.")

            try:
                sr_before, samples_before = _load_samples_from_bytes(file_bytes, file_ext)
                sr_after, samples_after = sr_before, samples_before
                _plot_before_after(
                    samples_before,
                    samples_after,
                    sr_before,
                    sr_after,
                    "Before Decryption (Stego)",
                    "After Decryption (Same Audio)"
                )
            except Exception as e:
                st.warning(f"Waveform plot unavailable: {e}")

        except Exception as e:
            st.error(f"❌ Failed to decode: {e}")

