import wave
import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TXXX, ID3NoHeaderError
from crypto_utils import encrypt_message, decrypt_message

# --- WAV (LSB method) ---

def _text_to_bits(text):
    return ''.join(format(ord(c), '08b') for c in text)

def _bits_to_text(bits):
    chars = [chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8)]
    return ''.join(chars)

def encode_message_in_wav(wav_file, message, key):
    audio = wave.open(wav_file, mode='rb')
    params = audio.getparams()
    frames = bytearray(list(audio.readframes(audio.getnframes())))
    audio.close()

    encrypted = encrypt_message(message, key) + "####END####"
    bits = _text_to_bits(encrypted)

    if len(bits) > len(frames):
        raise ValueError("Message too long for audio file.")

    for i in range(len(bits)):
        frames[i] = (frames[i] & ~1) | int(bits[i])

    stego_path = "temp_stego.wav"
    stego_audio = wave.open(stego_path, 'wb')
    stego_audio.setparams(params)
    stego_audio.writeframes(frames)
    stego_audio.close()

    return stego_path

def decode_message_from_wav(wav_file, key):
    audio = wave.open(wav_file, mode='rb')
    frames = bytearray(list(audio.readframes(audio.getnframes())))
    audio.close()

    bits = ''.join([str(frame & 1) for frame in frames])
    message = _bits_to_text(bits)

    if "####END####" not in message:
        raise ValueError("No hidden message found.")

    encrypted = message.split("####END####")[0]
    return decrypt_message(encrypted, key)

# --- MP3 (Metadata tag method) ---

def encode_message_in_mp3(mp3_file, message, key):
    encrypted = encrypt_message(message, key)
    temp_path = "temp_stego.mp3"

    with open(temp_path, 'wb') as out_file:
        out_file.write(mp3_file.read())

    try:
        tags = ID3(temp_path)
    except ID3NoHeaderError:
        tags = ID3()

    tags.add(TXXX(encoding=3, desc="secret", text=encrypted))
    tags.save(temp_path)

    return temp_path

def decode_message_from_mp3(mp3_file, key):
    temp_path = "temp_decode.mp3"
    with open(temp_path, 'wb') as out_file:
        out_file.write(mp3_file.read())

    try:
        tags = ID3(temp_path)
        encrypted = tags.getall("TXXX")[0].text[0]
        return decrypt_message(encrypted, key)
    except Exception as e:
        raise ValueError("Failed to decode or no hidden message.") from e
