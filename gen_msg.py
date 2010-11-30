# python gen_msg.py <group secret> <message-file-name>

import sys, os
import hashlib
import subprocess
import base64
import re
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'buzz'))
import buzz


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


def encrypt_msg(message_file_name, group_secret):
    group_hash = base64.b64encode(hashlib.sha256(group_secret).digest())
    
    # TODO: Choose some different number of letters
    
    short_group_hash = group_hash[0:8]
    
    cipher_file = open(message_file_name, 'a')
    cipher_file.write(str(datetime.now()))
    cipher_file.close()
    
    # Encrypt the plain text and save it to msg.encrypt
    subprocess.call(["./aescrypt", "-ep", group_secret, "-o", "msg.encrypt", message_file_name])
        
    cipher_file = open('msg.encrypt', 'r')
    cipher_text = cipher_file.read()
    cipher_file.close()
    
    # Base64 encode cipher text
    cipher_text = base64.b64encode(cipher_text)
        
    output = "#" + short_group_hash + " " + cipher_text
    
    
    cipher_file = open('msg.out', 'w')
    cipher_file.write(output)
    cipher_file.close()
   
    
def main():
    group_secret = sys.argv[1]
    message_file_name = sys.argv[2]
    
    print group_secret, message_file_name
    
    encrypt_msg(message_file_name, group_secret)
    
    decrypt_msg('msg.out', group_secret)


if __name__ == "__main__":
    main()
    