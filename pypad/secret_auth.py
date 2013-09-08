#!/usr/bin/env python

import base64, hashlib, hmac, os, time, struct

def auth_secret(secret, nstr):
    # raise if nstr contains anything but numbers
    try:
        int(nstr)
    except:
        return False

    tm = int(time.time() / 30)
    secret = base64.b32decode(secret)

    #try 30 +/- 
    for ix in [-1, 0, 1]:
        # convert timestamp to raw bytes
        b = struct.pack(">q", tm + ix)
        
        # generate hmac-sha1 from ts based on key
        hm = hmac.HMAC(secret, b, hashlib.sha1).digest()

        #extract 4 bytes from digest based on LSB
        offset = ord(hm[-1]) & 0x0F
        truncatedHash = hm[offset:offset+4]

        #get the code from it
        code = struct.unpack(">L", truncatedHash)[0]
        code &= 0x7FFFFFFF;
        code %= 1000000;
        if ("%06d" % code) == nstr:
            return True
    return False