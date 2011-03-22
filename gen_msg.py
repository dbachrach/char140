# python gen_msg.py <group secret> <message-file-name>

import sys, os
import codecs
import base64
import re
from datetime import datetime
from Crypto import Random, Cipher
from Crypto.Hash import HMAC, SHA, SHA256


PADDING = '{'
BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

def decrypt_msg(hoot, plain_tag):
    
    # Removes the short tag before the cipher text
    hoot = re.sub(r'^#\S+ ', r'', hoot)
    
    #print hoot
    
    session_integrity_cipher = hoot[0:64]
    integrity = hoot[64:92]
    message_cipher = hoot[92:]
    
    #print session_integrity_cipher, integrity, message_cipher
    
    sha = SHA256.new()
    sha.update(plain_tag)
    bit_long_tag = sha.digest()
    
    aes = Cipher.AES.new(bit_long_tag[16:32])
    session_integrity_payload = DecodeAES(aes, session_integrity_cipher)
    
    session_key = session_integrity_payload[0:16]
    integrity_key = session_integrity_payload[16:36]
     
    
    hmac = HMAC.new(integrity_key, digestmod=SHA)
    hmac.update(message_cipher)
    integrity_computed = base64.b64encode(hmac.digest())
    
    if integrity != integrity_computed:
        print "FAILURE: Integrity not preserved"
        return
    
    aes = Cipher.AES.new(session_key)
    message = DecodeAES(aes, message_cipher)
      
    # print "payload", session_integrity_payload
    # print "message", message
    # print "integrity_computed", integrity_computed


def encrypt_msg(message, plain_tag, short_tag_length=2): 

    session_key = Random.get_random_bytes(16)
    integrity_key = Random.get_random_bytes(20)
    
    sha = SHA256.new()
    sha.update(plain_tag)
    bit_long_tag = sha.digest()

    long_tag = base64.b64encode(bit_long_tag[0:16])
    #long_tag = unicode(bit_long_tag[0:16], "utf_8")
    #long_tag = bit_long_tag[0:16].encode("utf_8")
    short_tag = long_tag[0:short_tag_length]
    
    
    session_integrity_payload = (session_key + integrity_key)
    #print "payload", session_integrity_payload
    
    aes = Cipher.AES.new(bit_long_tag[16:32])
    session_integrity_cipher = EncodeAES(aes, session_integrity_payload)
    
    aes = Cipher.AES.new(session_key)
    message_cipher = EncodeAES(aes, message)
    
    
    hmac = HMAC.new(integrity_key, digestmod=SHA)
    hmac.update(message_cipher)
    integrity = base64.b64encode(hmac.digest())
    
    
    hoot = "#" + short_tag + " " + session_integrity_cipher + integrity + message_cipher
    
    # print "Input (", len(message), "):", message
    # print "Output (", len(hoot), "):", hoot
    # 
    # 
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
    size = 1
    if len(sys.argv) > 3:
        size = int(sys.argv[3])
    
    hoot = "#fE Lw2BuD9HXARCFJy+xjmDbev4S+qknmamtBNagDJDpT6LJP1vsnJBrxPvV1PgygT0USP2pEdQ1n0UrYYFTynoWTaVL3g=Gowxmt+yfH4/PVGCsh/uROLXNoMcI4x0G3AOkPdvS2E="
    for i in xrange(size):
        #hoot = encrypt_msg(message, plain_tag)
        decrypt_msg(hoot, plain_tag)


if __name__ == "__main__":
    main()
    