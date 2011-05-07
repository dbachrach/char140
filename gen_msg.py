# python gen_msg.py <group secret> <message-file-name>

import sys
import base64
import re
from Crypto import Random
from Crypto.Hash import HMAC, SHA, SHA256
from Crypto.Cipher import AES
from tw_uuencode import encode,decode


PADDING = '{'
BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING


def decrypt_msg(hoot, plain_tag, encoding, verbose=False):
    
    if encoding == "base64":
        DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
    else:
        DecodeAES = lambda c, e: c.decrypt(decode(e)).rstrip(PADDING)
    
    # Removes the short tag before the cipher text
    hoot = re.sub(r'^#\S+ ', r'', hoot)
    
    if encoding == "base64":
        session_integrity_cipher = hoot[0:64]
        integrity = hoot[64:92]
        message_cipher = hoot[92:]
    else:
        session_integrity_cipher = hoot[0:35]
        integrity = hoot[35:50]
        message_cipher = hoot[50:]
    
    
    sha = SHA256.new()
    sha.update(plain_tag)
    bit_long_tag = sha.digest()
    
    aes = AES.new(bit_long_tag[16:32])
    session_integrity_payload = DecodeAES(aes, session_integrity_cipher)
    
    session_key = session_integrity_payload[0:16]
    integrity_key = session_integrity_payload[16:36]
     
    
    hmac = HMAC.new(integrity_key, digestmod=SHA)
    if encoding == "base64":
        decoded_message_cipher = message_cipher
    else:
        decoded_message_cipher = decode(message_cipher)
    
    hmac.update(decoded_message_cipher)
    
    if encoding == "base64":
        integrity_computed = base64.b64encode(hmac.digest())
    else:    
        integrity_computed = encode(hmac.digest())
    
    if integrity != integrity_computed:
        print "FAILURE: Integrity not preserved.", integrity, integrity_computed
        return
    
    aes = AES.new(session_key)
    message = DecodeAES(aes, message_cipher)
      
    if verbose:
        print "message:", message
    

def encrypt_msg(message, plain_tag, encoding, short_tag_length=2, verbose=False): 

    if encoding == "base64":
        EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
    else:
        EncodeAES = lambda c, s: encode(c.encrypt(pad(s)))
        
    session_key = Random.get_random_bytes(16)
    integrity_key = Random.get_random_bytes(20)
    
    sha = SHA256.new()
    sha.update(plain_tag)
    bit_long_tag = sha.digest()

    long_tag = base64.b64encode(bit_long_tag[0:16])
    short_tag = long_tag[0:short_tag_length]
    
    session_integrity_payload = (session_key + integrity_key)
    
    aes = AES.new(bit_long_tag[16:32])
    session_integrity_cipher = EncodeAES(aes, session_integrity_payload)
    
    aes = AES.new(session_key)
    message_cipher = EncodeAES(aes, message)
    
    if encoding == "base64":
        decoded_message_cipher = message_cipher
    else:
        decoded_message_cipher = decode(message_cipher)
    
    hmac = HMAC.new(integrity_key, digestmod=SHA)
    hmac.update(decoded_message_cipher)
    
    if encoding == "base64":
        integrity = base64.b64encode(hmac.digest())
    else:
        integrity = encode(hmac.digest())
    
    hoot = "#" + short_tag + " " + session_integrity_cipher + integrity + message_cipher
    
    if verbose:
        print "hoot:", hoot
        # print "Input (", len(message), "):", message
        # print "Output (", len(hoot), "):", hoot
        # print "#shorttag", 1 + len(short_tag)
        # print "space", 1
        # print "Integrity", len(integrity)
        # print "Session Integrity Cipher text", len(session_integrity_cipher)
        # print "Message Cipher text", len(message_cipher)
    
    # TODO: What about date/time?
    return hoot   

def main():
    plain_tag = sys.argv[1]
    message = sys.argv[2]
    size = int(sys.argv[3])
    method = sys.argv[4]
    
    if "-b" in sys.argv:
        encoding = "base64"
    else:
        encoding = "utf8"
        
    
    v = ("-v" in sys.argv)

    
    hoot = "#fE Lw2BuD9HXARCFJy+xjmDbev4S+qknmamtBNagDJDpT6LJP1vsnJBrxPvV1PgygT0USP2pEdQ1n0UrYYFTynoWTaVL3g=Gowxmt+yfH4/PVGCsh/uROLXNoMcI4x0G3AOkPdvS2E="
    if method == "enc":
        for i in xrange(size):
            hoot = encrypt_msg(message, plain_tag, encoding, verbose=v)
    elif method == "dec":
        for i in xrange(size):
            decrypt_msg(hoot, plain_tag, encoding, verbose=v)


if __name__ == "__main__":
    main()
    