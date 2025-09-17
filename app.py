import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import io

# Your steganography functions for both WAV and MP3 are needed
from audio_stego_utils import (
    encode_message_in_wav,
    decode_message_from_wav,
    encode_message_in_mp3,
    decode_message_from_mp3
)

# --- Plotting Helper Function (WAV Only) ---
def plot_waveform(audio_file, title="Audio Waveform"):
    """Reads an audio file and plots its waveform ONLY if it's a WAV file."""
    file_extension = ""
    if hasattr(audio_file, 'name'): # Streamlit UploadedFile
        file_extension = audio_file.name.split('.')[-1].lower()
    elif isinstance(audio_file, str): # File path
        file_extension = audio_file.split('.')[-1].lower()

    # Only plot if the file is a WAV
    if file_extension == 'wav':
        try:
            fig, ax = plt.subplots(figsize=(10, 3))
            
            if hasattr(audio_file, 'seek'):
                audio_file.seek(0)

            sample_rate, data = wavfile.read(audio_file)
            
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
    else:
        # Inform the user why no graph is shown for other formats
        st.info("Waveform preview is only available for WAV files.")


# --- Streamlit App ---
st.set_page_config(page_title="Audio Steganography App", layout="wide")
st.title("🔊 Audio Steganography App with Encryption 🔐")
st.markdown("Hide your secret messages inside WAV or MP3 audio files. Waveform previews are shown for WAV files.")

menu = st.radio("Choose Operation", ["Encode Audio 🔏", "Decode Audio 🔓"], horizontal=True)

# --- ENCODE SECTION ---
if menu == "Encode Audio 🔏":
    st.subheader("Hide a Message in an Audio File")
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_audio = st.file_uploader("Upload a WAV or MP3 file", type=["wav", "mp3"])
        if uploaded_audio:
            st.audio(uploaded_audio, format=f"audio/{'wav' if uploaded_audio.name.endswith('wav') else 'mpeg'}")
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
                            raise ValueError("Unsupported format")

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
        uploaded_audio = st.file_uploader("Upload stego audio file (WAV or MP3)", type=["wav", "mp3"])
        if uploaded_audio:
            st.audio(uploaded_audio, format=f"audio/{'wav' if uploaded_audio.name.endswith('wav') else 'mpeg'}")
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
                            raise ValueError("Unsupported format")
                        
                        if message:
                            st.success("📝 Hidden Message Found:")
                            st.code(message, language=None)
                        else:
                            st.warning("No message found, or the key is incorrect.")

                    except Exception as e:
                        st.error(f"❌ Failed to decode: {e}")
            else:
                st.warning("Please upload a file and provide the secret key.")
                st.warning("Please upload a file and provide the secret key.")
