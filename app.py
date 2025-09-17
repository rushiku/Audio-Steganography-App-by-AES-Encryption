import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from pydub import AudioSegment
import io

# Assume your steganography functions are in this file
from audio_stego_utils import (
    encode_message_in_wav,
    decode_message_from_wav,
    encode_message_in_mp3,
    decode_message_from_mp3
)

# --- Plotting Helper Function ---
def plot_waveform(audio_file, title="Audio Waveform"):
    """Reads an audio file (from path or buffer) and plots its waveform."""
    try:
        # Create a figure for the plot
        fig, ax = plt.subplots(figsize=(10, 3))
        
        file_extension = ""
        if hasattr(audio_file, 'name'): # Streamlit UploadedFile
            file_extension = audio_file.name.split('.')[-1].lower()
            audio_file.seek(0) # Reset buffer pointer
        elif isinstance(audio_file, str): # File path
            file_extension = audio_file.split('.')[-1].lower()

        if file_extension == 'wav':
            sample_rate, data = wavfile.read(audio_file)
            # If stereo, take only one channel
            if data.ndim > 1:
                data = data[:, 0]
            duration = len(data) / sample_rate
            time = np.linspace(0., duration, len(data))
            ax.plot(time, data, label="Waveform")
            
        elif file_extension == 'mp3':
            audio = AudioSegment.from_file(audio_file, format="mp3")
            data = np.array(audio.get_array_of_samples())
            sample_rate = audio.frame_rate
            duration = len(data) / (sample_rate * audio.channels) # Adjust duration for channels
            time = np.linspace(0., duration, len(data))
             # If stereo, plot one channel
            if audio.channels > 1:
                ax.plot(time, data[::audio.channels], label="Waveform (Left Channel)")
            else:
                ax.plot(time, data, label="Waveform")
        else:
            st.warning(f"Plotting not supported for .{file_extension} format.")
            return

        ax.set_title(title, fontsize=14)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.grid(True, linestyle='--', alpha=0.6)
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error plotting waveform: {e}")

# --- Streamlit App ---
st.set_page_config(page_title="Audio Steganography App", layout="wide")
st.title("🔊 Audio Steganography App with Encryption 🔐")
st.markdown("Hide your secret messages inside WAV or MP3 audio files. This tool visualizes the audio waveforms to show how little the file is altered.")

menu = st.radio("Choose Operation", ["Encode Audio 🔏", "Decode Audio 🔓"], horizontal=True)

# --- ENCODE SECTION ---
if menu == "Encode Audio 🔏":
    st.subheader("Hide a Message in an Audio File")
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_audio = st.file_uploader("Upload a WAV or MP3 file", type=["wav", "mp3"])
        if uploaded_audio:
            st.audio(uploaded_audio, format=f"audio/{uploaded_audio.type.split('/')[1]}")
            plot_waveform(uploaded_audio, "Original Audio Waveform")
            
    with col2:
        secret_text = st.text_area("Enter the secret message", height=150)
        secret_key = st.text_input("Enter a secret key for encryption", type="password")

        if st.button("Hide Message Now 🔏", use_container_width=True):
            if uploaded_audio and secret_text and secret_key:
                with st.spinner("Embedding message... please wait."):
                    try:
                        file_ext = uploaded_audio.name.split('.')[-1].lower()
                        
                        if file_ext == "wav":
                            stego_path = encode_message_in_wav(uploaded_audio, secret_text, secret_key)
                        elif file_ext == "mp3":
                            stego_path = encode_message_in_mp3(uploaded_audio, secret_text, secret_key)
                        else:
                            raise ValueError("Unsupported audio format.")

                        st.success("✅ Message hidden successfully!")
                        st.subheader("Download Your Stego Audio")
                        
                        with open(stego_path, "rb") as f:
                            st.download_button(
                                "⬇️ Download Stego Audio", 
                                f, 
                                file_name="stego_audio." + file_ext,
                                mime=f"audio/{'wav' if file_ext == 'wav' else 'mpeg'}",
                                use_container_width=True
                            )
                        
                        st.audio(stego_path, format=f"audio/{'wav' if file_ext == 'wav' else 'mpeg'}")
                        plot_waveform(stego_path, "Stego (Encoded) Audio Waveform")

                    except Exception as e:
                        st.error(f"❌ Error during encoding: {e}")
            else:
                st.warning("Please provide all inputs: audio file, message, and key.")

# --- DECODE SECTION ---
elif menu == "Decode Audio 🔓":
    st.subheader("Reveal a Message from an Audio File")
    
    col1, col2 = st.columns(2)

    with col1:
        uploaded_audio = st.file_uploader("Upload the stego audio file (WAV or MP3)", type=["wav", "mp3"])
        if uploaded_audio:
            st.audio(uploaded_audio, format=f"audio/{uploaded_audio.type.split('/')[1]}")
            plot_waveform(uploaded_audio, "Uploaded Stego Audio Waveform")
            
    with col2:
        secret_key = st.text_input("Enter the secret key to decode", type="password")
        
        if st.button("Reveal Hidden Message 🔓", use_container_width=True):
            if uploaded_audio and secret_key:
                with st.spinner("Decoding message..."):
                    try:
                        file_ext = uploaded_audio.name.split('.')[-1].lower()
                        
                        if file_ext == "wav":
                            message = decode_message_from_wav(uploaded_audio, secret_key)
                        elif file_ext == "mp3":
                            message = decode_message_from_mp3(uploaded_audio, secret_key)
                        else:
                            raise ValueError("Unsupported audio format.")
                        
                        if message:
                            st.success("📝 Hidden Message Found:")
                            st.code(message, language=None)
                        else:
                            st.warning("No message found, or the key is incorrect.")

                    except Exception as e:
                        st.error(f"❌ Failed to decode: {e}")
            else:
                st.warning("Please upload a file and provide the secret key.")
