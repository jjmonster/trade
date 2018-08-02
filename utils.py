#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

def gaps(n1, n2):
    return digits(abs(n1-n2)*100/((n1+n2)/2), 6)

def isclose(n1, n2):
    if gaps(n1, n2) < 0.1:
        return True
    return False

def digits(num, digit):
    site = pow(10, digit)
    return math.floor(num*site)/site

def s2f(data):
    t = type(data)
    if t == None or t == int:
        return data
    elif t == float:
        return digits(data, 6)
    elif t == str:
        try:
            data = digits(float(data),6)
        except:
            return data
    elif len(data) == 0:
        return data
    elif t == list:
        for i in range(len(data)):
            data[i] = s2f(data[i])
    elif t == dict:
        for k,v in data.items():
            data[k] = s2f(v)
    else:
        print("unknown data type!", type(data), data)

    return data


