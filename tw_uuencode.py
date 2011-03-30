"""
Copyright (c) 2009 Timothy J Fontaine <tjfontaine@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

tw_uuencode for Web2.0 (Where the U's are Unicode and not Unix)

Microblogging limits you based on characters. Twitter's limit for instance is 140.
For most Latin1 based languages that means you can only transfer 140 bytes. But,
most sites also accept unicode characters, and their storage space varies from 1
byte, to 4.

So taking a cue from the olden days of NNTP, I present a new uuencode. Instead of
taking 3 bytes and pulling out 4 sets of 6 bits and translating into an 8bit clean
representation, this uuencode (by default) takes 11 bytes and transforms them into
8 unicode characters. You can also override the default storage and alphabet to
improve space efficiency.

Example:

from tw_uuencode import encode,decode
import zlib

msg = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate'

compressed = zlib.compress(msg, 9)
encoded = encode(compressed)
decoded = decode(encoded)
decompressed = zlib.decompress(decoded)

print 'Original message: (%d) %s' % (len(msg), msg)
print 'Zlib Compressed : (%d)' % (len(compressed))
print 'Encoded message : (%d) %s' % (len(encoded), ''.join(encoded))
print 'Did round trip  : %s' % (str(decompressed == msg))

Results:

Original message: (284) Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate
Zlib Compressed : (184)
Did round trip  : True

The default alphabet is made of the following sections of unicode characters
  'basic_latin' : range(0x20, 0x7E),
  'latin1'      : range(0xA1, 0xFF),
  'latin_ea'    : range(0x100, 0x17F),
  'latin_eb'    : range(0x180, 0x24F),
  'ipa'         : range(0x250, 0x2AE),
  'spacing'     : range(0x2B0, 0x2FE),
  'greek'       : range(0x390, 0x3CE) + range(0x3D0, 0x3FF),
  'cyrillic'    : range(0x400, 0x4FF),
  'canadian'    : range(0x1401, 0x1676),
  'blocks'      : range(0x2580, 0x259F),
  'geometry'    : range(0x25A0, 0x25FF),
  'dingbats'    : range(0x2701, 0x27BE),
  'matha'       : range(0x27C0, 0x27EB),
  'arrowsa'     : range(0x27F0, 0x27FF),
  ## the following are not included because of the skipped ranges
  # required too much effort on my part
  #'cyrillic1'   : range(0x500, 0x513), # not currently included
  #'armenian'    : range(0x531, 0x589), # not currently included
  #'hebrew'      : range(0x5BE, 0x5F4), # not currently included
"""

from bitstring import BitString

ALPHABET = range(0x20, 0x7E) + range(0xA1, 0xFF) + range(0x100, 0x17F) + range(0x180, 0x24F) + range(0x250, 0x2AE) + range(0x2B0, 0x2FE) + range(0x390, 0x3CE) + range(0x3D0, 0x3FF) + range(0x400, 0x4FF) + range(0x1401, 0x1676) + range(0x2580, 0x259F) + range(0x25A0, 0x25FF) + range(0x2701, 0x27BE) + range(0x27C0, 0x27EB) + range(0x27F0, 0x27FF)

BIT_STORAGE = 11

TWUUENC_START = unichr(0x2639)
TWUUENC_START_ZLIB = unichr(0x263A)

def encode(s, storage=BIT_STORAGE, alpha=ALPHABET, char_func=unichr):
  """
    Accepts any string/bytes. You can override the storage and alpha
    keywords to change to another language set and storage mechanism

    Returns a list of encoded bits.
  """
  n = s
  buf = ''
  while len(n) > 0:
    b = n[:storage]
    n = n[storage:]

    d = 11 - len(b)
    for i in range(d):
      b += '\0'

    bs = BitString(data=b)

    for i in range(8):
      v = bs.readbits(storage).uint
      buf += char_func(alpha[v])

  return buf.rstrip(char_func(alpha[0]))

def decode(s, storage=BIT_STORAGE, alpha=ALPHABET):
  """
    Accepts any iterable object, you can override storage and alpha
    keywords to change to another language set and storage mechanism

    Returns a string/bytes
  """
  n = [ord(a) for a in s if a != TWUUENC_START and a != TWUUENC_START_ZLIB]
  bs = BitString()
  for a in n:
    for pos,l in enumerate(alpha):
      if a == l:
        bs.append(BitString(uint=pos, length=storage))
  bs.seekbyte(0)
  return bs.readbytes(len(bs)/8).data.rstrip('\0')
