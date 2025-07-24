from PIL import Image
from crypto_utils import encrypt_message, decrypt_message

def _message_to_bits(message):
    return ''.join(format(ord(char), '08b') for char in message)

def _bits_to_message(bits):
    chars = [chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8)]
    return ''.join(chars)

def encode_message_in_image(image, message, key):
    encrypted_message = encrypt_message(message, key)
    encrypted_message += "####END####"
    binary = _message_to_bits(encrypted_message)
    
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    encoded = image.copy()
    width, height = encoded.size
    pixels = encoded.load()
    
    idx = 0
    for y in range(height):
        for x in range(width):
            if idx < len(binary):
                r, g, b = pixels[x, y]
                r = (r & ~1) | int(binary[idx])
                idx += 1
                if idx < len(binary):
                    g = (g & ~1) | int(binary[idx])
                    idx += 1
                if idx < len(binary):
                    b = (b & ~1) | int(binary[idx])
                    idx += 1
                pixels[x, y] = (r, g, b)
            else:
                return encoded
    return encoded

def decode_message_from_image(image, key):
    if image.mode != 'RGB':
        image = image.convert('RGB')

    pixels = image.load()
    binary_data = ""
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            r, g, b = pixels[x, y]
            binary_data += str(r & 1)
            binary_data += str(g & 1)
            binary_data += str(b & 1)

    decoded = _bits_to_message(binary_data)
    if "####END####" not in decoded:
        raise ValueError("No hidden message found.")
    
    encrypted_message = decoded.split("####END####")[0]
    return decrypt_message(encrypted_message, key)
