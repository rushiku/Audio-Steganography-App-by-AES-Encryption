import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import io

# Assume your steganography functions for WAV are in this file
# We only need the WAV functions now.
from audio_stego_utils import (
    encode_message_in_wav,
    decode_message_from_wav
)

# --- Plotting Helper Function (Simplified for WAV) ---
def plot_waveform(audio_file, title="Audio Waveform"):
    """Reads a WAV audio file (from path or buffer) and plots its waveform."""
    try:
        fig, ax = plt.subplots(figsize=(10, 3))
        
        # Ensure buffer is at the beginning
        if hasattr(audio_file, 'seek'):
            audio_file.seek(0)

        sample_rate, data = wavfile.read(audio_file)
        
        # If stereo, take only one channel for plotting
        if data.ndim > 1:
            data = data[:, 0]
            
        duration = len(data) / sample_rate
        time = np.linspace(0., duration, len(data))
        ax.plot(time, data, label="Waveform")

        ax.set_title(title, fontsize=14)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.grid(True, linestyle='--', alpha=0.6)
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error plotting WAV waveform: {e}")

# --- Streamlit App ---
st.set_page_config(page_title="Audio Steganography App", layout="wide")
st.title("🔊 Audio Steganography App (WAV Files) 🔐")
st.markdown("Hide your secret messages inside WAV audio files. This tool visualizes the audio waveforms to show how little the file is altered.")

menu = st.radio("Choose Operation", ["Encode Audio 🔏", "Decode Audio 🔓"], horizontal=True)

# --- ENCODE SECTION ---
if menu == "Encode Audio 🔏":
    st.subheader("Hide a Message in a WAV File")
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_audio = st.file_uploader("Upload a WAV file", type=["wav"])
        if uploaded_audio:
            st.audio(uploaded_audio, format="audio/wav")
            plot_waveform(uploaded_audio, "Original Audio Waveform")
            
    with col2:
        secret_text = st.text_area("Enter the secret message", height=150)
        secret_key = st.text_input("Enter a secret key for encryption", type="password")

        if st.button("Hide Message Now 🔏", use_container_width=True):
            if uploaded_audio and secret_text and secret_key:
                with st.spinner("Embedding message... please wait."):
                    try:
                        stego_path = encode_message_in_wav(uploaded_audio, secret_text, secret_key)

                        st.success("✅ Message hidden successfully!")
                        st.subheader("Download Your Stego Audio")
                        
                        with open(stego_path, "rb") as f:
                            st.download_button(
                                "⬇️ Download Stego Audio", 
                                f, 
                                file_name="stego_audio.wav",
                                mime="audio/wav",
                                use_container_width=True
                            )
                        
                        st.audio(stego_path, format="audio/wav")
                        plot_waveform(stego_path, "Stego (Encoded) Audio Waveform")

                    except Exception as e:
                        st.error(f"❌ Error during encoding: {e}")
            else:
                st.warning("Please provide all inputs: audio file, message, and key.")

# --- DECODE SECTION ---
elif menu == "Decode Audio 🔓":
    st.subheader("Reveal a Message from a WAV File")
    
    col1, col2 = st.columns(2)

    with col1:
        uploaded_audio = st.file_uploader("Upload the stego WAV file", type=["wav"])
        if uploaded_audio:
            st.audio(uploaded_audio, format="audio/wav")
            plot_waveform(uploaded_audio, "Uploaded Stego Audio Waveform")
            
    with col2:
        secret_key = st.text_input("Enter the secret key to decode", type="password")
        
        if st.button("Reveal Hidden Message 🔓", use_container_width=True):
            if uploaded_audio and secret_key:
                with st.spinner("Decoding message..."):
                    try:
                        message = decode_message_from_wav(uploaded_audio, secret_key)
                        
                        if message:
                            st.success("📝 Hidden Message Found:")
                            st.code(message, language=None)
                        else:
                            st.warning("No message found, or the key is incorrect.")

                    except Exception as e:
                        st.error(f"❌ Failed to decode: {e}")
            else:
                st.warning("Please upload a file and provide the secret key.")
