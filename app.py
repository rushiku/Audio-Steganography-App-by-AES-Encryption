import streamlit as st
import numpy as np
import wave
from pydub import AudioSegment   # for MP3 waveform
from audio_stego_utils import (
    encode_message_in_wav, decode_message_from_wav,
    encode_message_in_mp3, decode_message_from_mp3
)

st.set_page_config(page_title="Audio Steganography App", layout="centered")
st.title("🔊 Audio Steganography App with Encryption 🔐")
st.subheader("🔊 Audio Steganography")

menu = st.radio("Choose Operation", ["Encode Audio 🔏", "Decode Audio 🔓"])

# --------- Utility: Plot real waveform ---------
def plot_waveform(audio_file, file_type):
    try:
        if file_type == "wav":
            with wave.open(audio_file, "rb") as wf:
                n_channels = wf.getnchannels()
                n_frames = wf.getnframes()
                signal = wf.readframes(n_frames)

            audio = np.frombuffer(signal, dtype=np.int16)

            if n_channels > 1:
                audio = audio[::n_channels]

        elif file_type == "mp3":
            sound = AudioSegment.from_file(audio_file, format="mp3")
            samples = sound.get_array_of_samples()
            audio = np.array(samples)

            if sound.channels > 1:
                audio = audio[::sound.channels]

        # Downsample for speed
        step = max(1, len(audio) // 2000)
        audio = audio[::step]

        # Plot
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
                file_type = "wav"
            elif uploaded_audio.name.endswith(".mp3"):
                stego_path = encode_message_in_mp3(uploaded_audio, secret_text, secret_key)
                file_type = "mp3"
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

            # 🎶 Plot waveform
            plot_waveform(stego_path, file_type)

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
                file_type = "wav"
            elif uploaded_audio.name.endswith(".mp3"):
                message = decode_message_from_mp3(uploaded_audio, secret_key)
                file_type = "mp3"
            else:
                raise ValueError("Unsupported audio format. Only .wav or .mp3 allowed.")

            st.success("📝 Hidden Message:")
            st.code(message)

            # 🎶 Plot waveform
            plot_waveform(uploaded_audio, file_type)

        except Exception as e:
            st.error(f"❌ Failed to decode: {e}")




