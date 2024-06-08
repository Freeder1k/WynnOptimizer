from __future__ import annotations

digitsStr = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+-"
digits = [c for c in digitsStr]
digitsMap = {digits[i]: i for i in range(len(digits))}


class Base64:
    @staticmethod
    def fromInt(x, order=-1):
        """
        Convert an integer to a base64 string.
        :param x: The integer to convert.
        :param order: The number of digits the result string should have. -1 for as many as needed.
        """
        result = ''
        i = 0
        while i != order:
            result = digits[x & 0x3f] + result
            x >>= 6
            if order < 0 and x == 0 or x == -1:
                break
            i += 1
        return result

    @staticmethod
    def toInt(s):
        """
        Convert a base64 string to an integer.
        """
        result = 0
        for c in s:
            result = result * 64 + digitsMap[c]
        return result

print(Base64.toInt("2SI"))