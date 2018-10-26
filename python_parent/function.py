# -*- coding: utf-8 -*-
import math
import numpy as np
import sys
import random
import time


def bit(a): # Bit Restriction
    #return a # FOR NOW, Use float.
    return bit_compress(a,2,5)

def bit_16(a): # Bit Restriction
    #return a # FOR NOW, Use float.
    return bit_compress(a,2,13)

def bit_compress(a,n,m):
    part = pow(2,m) * np.absolute(a)
    upper = (pow(2,n)-1) * np.ones(a.shape)
    a2 = np.absolute(a).astype(int) - upper
    int_part = np.absolute(a).astype(int) - 0.5 * (np.absolute(a2)+a2)
    fixed =  np.sign(a) * (int_part + part.astype(int) / float(pow(2,m)) - np.absolute(a).astype(int))
    return fixed.astype(np.float32) # bit_compress enable
    # return a # bit_compress unable

def multiply_inf(a,b):
    return bit(np.dot(a,b))

def multiply_lea(a,b):
    return bit_16(np.dot(a,b))

def act_func(x, act): #活性化関数
    if act == 'relu':
        return bit(np.array( 0.5 * (np.absolute(x)+x)))
    elif act == 'sigmoid':
        #return bit(np.array( 0.5 * ( 1 + np.tanh(x)) , dtype=np.float64))
        return bit( 1. / ( 1. + np.exp(-x)))
    elif act == 'no':
        return bit(x)
    elif act == 'tanh':
        return bit(np.tanh(x))
    elif act == 'softmax':
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum()
        # これは誤り

def dif(x, act): #活性化関数の微分
    if act == 'relu':
        return bit_16(np.sign(x))
    elif act == 'sigmoid':
        return bit_16(act_func(x,'sigmoid') * ( 1 - act_func(x,'sigmoid') ))
    elif act == 'no':
        return 1
    elif act == 'tanh':
        return bit( 1.0 / (np.cosh(x)**2))
    elif act == 'softmax':
        return bit_16(act_func(x,'sigmoid') * ( 1 - act_func(x,'sigmoid') ))
        # これは誤り

def step(x):
    #np.sign(x - np.max(x))
    y = np.zeros(len(x))
    y[np.argmax(x)] = 1
    return y
