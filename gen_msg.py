# python gen_msg.py <group secret> <message-file-name>

import sys, os
import hashlib
import subprocess
import base64
import re
from datetime import datetime
import Crypto


def decrypt_msg(message_file_name, group_secret):
    
    cipher_file = open(message_file_name, 'r')
    msg = cipher_file.read()
    cipher_file.close()
    
    # Removes the hash tag before the cipher text
    msg = re.sub(r'^#\S+ ', r'', msg)
    
    # Base64 Decode the cipher text
    msg = base64.b64decode(msg)
    
    
    cipher_file = open(message_file_name, 'w')
    cipher_file.write(msg)
    cipher_file.close()
    
    # Decrypt the cipher text and save it to msg.decrypt file
    subprocess.call(["./aescrypt", "-dp", group_secret, "-o", "msg.decrypt", message_file_name])


def encrypt_msg(message, plain_tag, short_tag_length=3): 

    rander = Crypto.Random.new()

	session_key = rander.get_random_bytes(16)
	integrity_key = rander.get_random_bytes(20)
	
	sha = Crypto.Hash.SHA256.new()
	bit_long_tag = sha.update(plain_tag).digest()
	
    long_tag = base64.b64encode(bit_long_tag[0:16])

    short_tag = long_tag[0:short_tag_length]
	
	
	session_integrity_payload = (session_key + integrity_key)
	
	aes = Crypto.Cipher.AES.new(long_tag[16:32])
	
	session_integrity_cipher = base64.b64encode(aes.encrypt(session_integrity_payload))
	
	aes = Crypto.Cipher.AES.new(session_key)
	message_cipher = base64.b64encode(aes.encrypt(message))
	
	hmac = Crypto.Hash.HMAC.new(integrity_key, digestmod=SHA)
	integrity = base64.b64encode(hmac.update(message_cpiher).digest())
	
	
	output = "#" + short_tag + " " + session_integrity_cipher + " "	+ message_cipher + " " + integrity
	
	print "Output", output
	
    # TODO: Choose some different number of letters
    
    # short_group_hash = group_hash[0:8]
    # 
    # cipher_file = open(message_file_name, 'a')
    # cipher_file.write(str(datetime.now()))
    # cipher_file.close()
    # 
    # # Encrypt the plain text and save it to msg.encrypt
    # subprocess.call(["./aescrypt", "-ep", group_secret, "-o", "msg.encrypt", message_file_name])
    #     
    # cipher_file = open('msg.encrypt', 'r')
    # cipher_text = cipher_file.read()
    # cipher_file.close()
    # 
    # # Base64 encode cipher text
    # cipher_text = base64.b64encode(cipher_text)
    #     
    # output = "#" + short_group_hash + " " + cipher_text
    # 
    # print output
    # 
    # cipher_file = open('msg.out', 'w')
    # cipher_file.write(output)
    # cipher_file.close()
   
    
def main():
    group_secret = sys.argv[1]
    message = sys.argv[2]
    
    print group_secret, message
    
    encrypt_msg(message, group_secret)
    
    #decrypt_msg('msg.out', group_secret)


if __name__ == "__main__":
    main()
    