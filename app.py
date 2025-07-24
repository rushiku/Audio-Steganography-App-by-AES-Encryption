import streamlit as st
from stegano_utils import encode_message_in_image, decode_message_from_image
from PIL import Image
import io

st.set_page_config(page_title="Image Steganography", layout="centered")
st.title("🕵️‍♂️ Image Steganography App (with Secret Key 🔐)")

menu = st.sidebar.radio("Choose Operation", ["Encode 🔏", "Decode 🔓"])

if menu == "Encode 🔏":
    st.header("🔐 Hide Secret Message")
    uploaded_image = st.file_uploader("Upload an image (PNG recommended)", type=["png", "jpg", "jpeg"])
    secret_text = st.text_area("Enter the secret message")
    secret_key = st.text_input("Enter a secret key for encryption", type="password")
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
            st.error(f"❌ Error encoding message: {e}")

elif menu == "Decode 🔓":
    st.header("🔍 Reveal Hidden Message")
    uploaded_image = st.file_uploader("Upload the stego image", type=["png", "jpg", "jpeg"])
    secret_key = st.text_input("Enter the secret key used by the sender", type="password")
    if uploaded_image and secret_key:
        image = Image.open(uploaded_image)
        try:
            hidden_message = decode_message_from_image(image, secret_key)
            st.success("📝 Secret Message Found:")
            st.code(hidden_message)
        except Exception as e:
            st.error(f"❌ Failed to decode or wrong key: {e}")

