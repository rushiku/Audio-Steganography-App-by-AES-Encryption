import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

def encrypt_message(message, password):
    key = hashlib.sha256(password.encode()).digest()
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct_bytes = cipher.encrypt(pad(message.encode(), AES.block_size))
    encrypted = base64.b64encode(iv + ct_bytes).decode()
    return encrypted

def decrypt_message(cipher_text, password):
    key = hashlib.sha256(password.encode()).digest()
    raw = base64.b64decode(cipher_text)
    iv = raw[:16]
    ct = raw[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(ct), AES.block_size).decode()
    return decrypted
