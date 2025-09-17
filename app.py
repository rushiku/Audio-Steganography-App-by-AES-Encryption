import streamlit as st

import numpy as np
import wave
import struct
from Crypto.Cipher import AES
import base64
import os

# ================= Utility Functions =================

def pad_message(message):
    while len(message) % 16 != 0:
        message += " "
    return message

def encrypt_message(key, message):
    key = pad_message(key).encode("utf-8")[:16]
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted = cipher.encrypt(pad_message(message).encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def decrypt_message(key, encrypted_message):
    key = pad_message(key).encode("utf-8")[:16]
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted = cipher.decrypt(base64.b64decode(encrypted_message)).decode("utf-8")
    return decrypted.strip()

def embed_message(audio_path, output_path, message):
    song = wave.open(audio_path, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))

    message = message + int((len(frame_bytes) - (len(message) * 8 * 8)) / 8) *'#'
    bits = list(map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8,'0') for i in message])))

    for i, bit in enumerate(bits):
        frame_bytes[i] = (frame_bytes[i] & 254) | bit
    frame_modified = bytes(frame_bytes)

    with wave.open(output_path, 'wb') as fd:
        fd.setparams(song.getparams())
        fd.writeframes(frame_modified)

    song.close()

def extract_message(audio_path):
    song = wave.open(audio_path, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))
    extracted = [frame_bytes[i] & 1 for i in range(len(frame_bytes))]
    string = "".join(chr(int("".join(map(str, extracted[i:i+8])), 2)) for i in range(0,len(extracted),8))
    decoded = string.split("###")[0]
    song.close()
    return decoded

def plot_waveform(audio_file):
    song = wave.open(audio_file, 'rb')
    signal = song.readframes(-1)
    signal = np.frombuffer(signal, dtype=np.int16)
    plt.figure(figsize=(10, 4))
    plt.plot(signal)
    plt.title("Audio Waveform (WAV only)")
    plt.xlabel("Samples")
    plt.ylabel("Amplitude")
    st.pyplot(plt)
    song.close()

# ================= Streamlit App =================

st.title("🔒 Audio Steganography with AES Encryption")

option = st.sidebar.selectbox("Choose Action", ["Embed Message", "Extract Message"])

if option == "Embed Message":
    audio_file = st.file_uploader("Upload a WAV or MP3 file", type=["wav", "mp3"])
    message = st.text_area("Enter the secret message")
    key = st.text_input("Enter AES Encryption Key (16 chars max)", type="password")

    if audio_file and message and key:
        file_name = audio_file.name
        with open(file_name, "wb") as f:
            f.write(audio_file.getbuffer())

        encrypted_message = encrypt_message(key, message)
        output_file = "embedded_" + file_name

        if file_name.endswith(".wav"):
            embed_message(file_name, output_file, encrypted_message)
            st.success("Message embedded successfully in WAV file!")
            plot_waveform(output_file)  # Show waveform only for WAV
            with open(output_file, "rb") as f:
                st.download_button("Download Stego Audio", f, file_name=output_file)
        else:
            st.warning("MP3 upload detected → Encryption supported, but no graph.")
            st.info("Currently only WAV files can display waveforms.")

elif option == "Extract Message":
    audio_file = st.file_uploader("Upload a WAV file with hidden message", type=["wav"])
    key = st.text_input("Enter AES Decryption Key", type="password")

    if audio_file and key:
        file_name = audio_file.name
        with open(file_name, "wb") as f:
            f.write(audio_file.getbuffer())

        extracted_message = extract_message(file_name)
        decrypted_message = decrypt_message(key, extracted_message)

        st.success("Decrypted Secret Message:")
        st.write(decrypted_message)

