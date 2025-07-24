import streamlit as st
from PIL import Image
import io

from stegano_utils import encode_message_in_image, decode_message_from_image
from audio_stego_utils import encode_message_in_audio, decode_message_from_audio

st.set_page_config(page_title="Steganography App", layout="centered")
st.title("🕵️ Steganography App (Image + Audio, with Encryption 🔐)")

option = st.sidebar.selectbox("Choose Mode", ["Image Steganography", "Audio Steganography"])

# -------------------- IMAGE --------------------
if option == "Image Steganography":
    st.subheader("🖼️ Image Steganography")

    menu = st.radio("Choose Operation", ["Encode 🔏", "Decode 🔓"])

    if menu == "Encode 🔏":
        uploaded_image = st.file_uploader("Upload an image (PNG/JPG)", type=["png", "jpg", "jpeg"])
        secret_text = st.text_area("Enter the secret message")
        secret_key = st.text_input("Enter a secret key", type="password")

        if uploaded_image and secret_text and secret_key:
            image = Image.open(uploaded_image)
            try:
                stego_image = encode_message_in_image(image, secret_text, secret_key)
                st.success("✅ Message encoded successfully!")
                img_byte_arr = io.BytesIO()
                stego_image.save(img_byte_arr, format='PNG')
                st.download_button("⬇️ Download Stego Image", data=img_byte_arr.getvalue(),
                                   file_name="stego_image.png", mime="image/png")
                st.image(stego_image, caption="Stego Image Preview", use_column_width=True)
            except Exception as e:
                st.error(f"❌ Error: {e}")

    elif menu == "Decode 🔓":
        uploaded_image = st.file_uploader("Upload the stego image", type=["png", "jpg", "jpeg"])
        secret_key = st.text_input("Enter the secret key", type="password")

        if uploaded_image and secret_key:
            image = Image.open(uploaded_image)
            try:
                message = decode_message_from_image(image, secret_key)
                st.success("📝 Hidden Message:")
                st.code(message)
            except Exception as e:
                st.error(f"❌ Error: {e}")

# -------------------- AUDIO --------------------
elif option == "Audio Steganography":
    st.subheader("🔊 Audio Steganography")

    menu = st.radio("Choose Operation", ["Encode Audio 🔏", "Decode Audio 🔓"])

    if menu == "Encode Audio 🔏":
        uploaded_audio = st.file_uploader("Upload a WAV audio file", type=["wav"])
        secret_text = st.text_area("Enter the secret message for audio")
        secret_key = st.text_input("Enter a secret key", type="password")

        if uploaded_audio and secret_text and secret_key:
            try:
                stego_path = encode_message_in_audio(uploaded_audio, secret_text, secret_key)
                with open(stego_path, "rb") as f:
                    st.download_button("⬇️ Download Stego Audio", f, file_name="stego_audio.wav", mime="audio/wav")
                st.audio(stego_path, format='audio/wav')
                st.success("✅ Message hidden successfully in audio!")
            except Exception as e:
                st.error(f"❌ Error: {e}")

    elif menu == "Decode Audio 🔓":
        uploaded_audio = st.file_uploader("Upload stego audio file", type=["wav"])
        secret_key = st.text_input("Enter the secret key", type="password")

        if uploaded_audio and secret_key:
            try:
                message = decode_message_from_audio(uploaded_audio, secret_key)
                st.success("📝 Hidden Message:")
                st.code(message)
            except Exception as e:
                st.error(f"❌ Error: {e}")

