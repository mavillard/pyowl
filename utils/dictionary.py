# -*- coding: utf-8 -*-


class Dictionary:
    def __init__(self, dct):
        self.dct = dct
    
    def reverse(self):
        d = {}
        for k, v in self.dct.items():
            d[v] = k
        return d
