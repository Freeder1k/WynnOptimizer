from __future__ import annotations

digitsStr = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+-"
digits = [c for c in digitsStr]
digitsMap = {digits[i]: i for i in range(len(digits))}


class Base64:
    @classmethod
    def fromInt(cls, x):
        result = ''
        while True:
            result = digits[x & 0x3f] + result
            x >>= 6
            if x == 0 or x == -1:
                break
        return result
