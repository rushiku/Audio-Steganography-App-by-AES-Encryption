import streamlit as st
import numpy as np
import wave
from audio_stego_utils import (
    encode_message_in_wav, decode_message_from_wav,
    encode_message_in_mp3, decode_message_from_mp3
)

st.set_page_config(page_title="Audio Steganography App", layout="centered")
st.title("🔊 Audio Steganography App with Encryption 🔐")
st.subheader("🔊 Audio Steganography")

menu = st.radio("Choose Operation", ["Encode Audio 🔏", "Decode Audio 🔓"])

# --------- Utility: Plot real waveform from WAV ---------
def plot_waveform(audio_file):
    try:
        with wave.open(audio_file, "rb") as wf:
            n_channels = wf.getnchannels()
            n_frames = wf.getnframes()
            framerate = wf.getframerate()
            signal = wf.readframes(n_frames)

        # Convert bytes to numpy array
        audio = np.frombuffer(signal, dtype=np.int16)

        # If stereo, take one channel
        if n_channels > 1:
            audio = audio[::n_channels]

        # Downsample for performance
        step = max(1, len(audio) // 2000)
        audio = audio[::step]

        # Plot waveform
        st.line_chart(audio)
    except Exception as e:
        st.warning(f"⚠️ Could not plot waveform: {e}")

# --------- Encode ---------
if menu == "Encode Audio 🔏":
    uploaded_audio = st.file_uploader("Upload a WAV or MP3 file", type=["wav", "mp3"])
    secret_text = st.text_area("Enter the secret message for audio")
    secret_key = st.text_input("Enter a secret key", type="password")

    if uploaded_audio and secret_text and secret_key:
        try:
            if uploaded_audio.name.endswith(".wav"):
                stego_path = encode_message_in_wav(uploaded_audio, secret_text, secret_key)
            elif uploaded_audio.name.endswith(".mp3"):
                stego_path = encode_message_in_mp3(uploaded_audio, secret_text, secret_key)
            else:
                raise ValueError("Unsupported audio format. Only .wav or .mp3 allowed.")

            with open(stego_path, "rb") as f:
                st.download_button(
                    "⬇️ Download Stego Audio",
                    f,
                    file_name="stego_audio" + uploaded_audio.name[-4:],
                    mime="audio/wav" if stego_path.endswith(".wav") else "audio/mpeg"
                )

            st.audio(stego_path, format="audio/wav" if stego_path.endswith(".wav") else "audio/mpeg")
            st.success("✅ Message hidden successfully in audio!")

            # 🎶 Plot waveform (only works for .wav)
            if stego_path.endswith(".wav"):
                plot_waveform(stego_path)

        except Exception as e:
            st.error(f"❌ Error: {e}")

# --------- Decode ---------
elif menu == "Decode Audio 🔓":
    uploaded_audio = st.file_uploader("Upload stego audio file (WAV or MP3)", type=["wav", "mp3"])
    secret_key = st.text_input("Enter the secret key", type="password")

    if uploaded_audio and secret_key:
        try:
            if uploaded_audio.name.endswith(".wav"):
                message = decode_message_from_wav(uploaded_audio, secret_key)
            elif uploaded_audio.name.endswith(".mp3"):
                message = decode_message_from_mp3(uploaded_audio, secret_key)
            else:
                raise ValueError("Unsupported audio format. Only .wav or .mp3 allowed.")

            st.success("📝 Hidden Message:")
            st.code(message)

            # 🎶 Plot waveform (only works for .wav)
            if uploaded_audio.name.endswith(".wav"):
                plot_waveform(uploaded_audio)

        except Exception as e:
            st.error(f"❌ Failed to decode: {e}")
