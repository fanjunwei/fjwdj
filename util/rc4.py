# coding=utf8

class RC4():
    base = [str(x) for x in range(10)] + [chr(x) for x in range(ord('a'), ord('a') + 6)]

    def __init__(self, key):
        # initialize statement vector
        self.s = [i for i in range(0, 256)]
        #print self.s
        #initialize key vector
        lens = len(key)
        self.t = [key[i % lens] for i in range(0, 256)]
        #print self.t
        #use key to change statement vector
        j = 0
        for i in range(0, 256):
            j = (j + ord(self.t[i]) + self.s[i]) % 256
            self.s[i], self.s[j] = self.s[j], self.s[i]
            #to encode the plain text to the RC4 encoded string,also decode

    def dec2hex(self, string_num):
        num = int(string_num)
        mid = []
        while True:
            if num == 0: break
            num, rem = divmod(num, 16)
            mid.append(self.base[rem])

        s = ''.join([str(x) for x in mid[::-1]])
        while len(s) < 2:
            s = '0' + s
        return s

    def array2hex(self, array):
        s = [self.dec2hex(str(i)) for i in array]
        return ''.join(s)

    def hex2dec(self, string_num):
        return int(string_num.lower(), 16)

    def hex2array(self, hex_string):
        str = ''
        flag = 0
        array = []
        for c in hex_string:
            if flag == 0:
                flag = 1
                str = c
            else:
                flag = 0
                str = str + c
                array.append(chr(self.hex2dec(str)))
        return ''.join(array)

    def arrayCrypt(self, encodestring):
        lens = len(encodestring)
        x = y = 0
        self.c = [None] * lens
        for i in range(0, lens):
            x = (x + 1) % 256
            y = (y + self.s[x]) % 256
            self.s[x], self.s[y] = self.s[y], self.s[x]
            t = (self.s[x] + self.s[y]) % 256
            self.c[i] = ord(encodestring[i]) ^ self.s[t]
        return self.c

    def crypt(self, encodestring):
        return self.array2hex(self.arrayCrypt(encodestring))

    def decry(self, hexstring):
        array = self.arrayCrypt(self.hex2array(hexstring))
        s = [chr(i) for i in array]
        return "".join(s)
