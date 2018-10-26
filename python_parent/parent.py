import thread
import time
import sys
import serial
import serial.tools.list_ports
import pdb
import numpy as np
from lut_parser import float2binary
from time import sleep

class Weights:
    def __init__(self):
        self.recv_u = []
        self.recv_l = []
        self.weight = []
        self.weight_bin_format = []
        self.weight_reduced = []

    def trans_byte_format(self, data):
        int_data = data.split(',')[:-1]
        bin_data = [format(int(i), '08b') for i in int_data]

        return bin_data

    def get_byte_format(self, dev):
        data = dev.readline()
        data = self.trans_byte_format(data)
        return data

    def get_weight_16bit(self, upper, lower):
        weight = [i+j for (i,j) in zip(upper,lower)]

        return weight

    def trans_16bit_to_float(self, data, radix):
        w = np.array([])
        sign = [int(i[0]) for i in data]
        digit = np.array([[float(i) for i in j[1:]] for j in data])
        for i in range(len(digit)):
            if sign[i] == 0:
                num = np.dot(digit[i], radix)
            else:
                num = -1.0 * (np.dot(digit[i]*-1.0+1.0, radix) + 2**(-13))
            w = np.append(w, num)

        return w.tolist()
    
    def get_weight(self):
        return self.weight

    def get_weight_bin_format(self):
        return self.weight_bin_format

    def get_weight_reduced(self):
        return self.weight_reduced

    def append_weight(self, dev, radix):
        u = self.get_byte_format(dev)
        l = self.get_byte_format(dev)
        wb = self.get_weight_16bit(u, l)
        wf = self.trans_16bit_to_float(wb, radix)
        self.weight_bin_format.append(wb)
        self.weight.append(wf)

        print self.weight

        w_all = np.array(self.weight)
        reduce_w = np.sum(w_all, axis=0) / w_all.shape[0]
        self.weight_reduced = reduce_w.tolist()
        return wb, wf
    
def trans_byte_format(data):
    ## ARG
    #### data: str, (ex. "17, 135, 24, \n,")
    ## RETURN
    #### bin_data: str list, (ex. ['00010001', '10000111', '00011000'])
    int_data = data.split(',')[:-1]
    bin_data = [format(int(i), '08b') for i in int_data]

    return bin_data

def get_byte_format(dev):
    ## ARG
    #### dev: serial port object
    ## RETURN
    #### data: str list, (ex. ['00010001', '10000111', '00011000'])
    data = dev.readline()
    data = trans_byte_format(data)
    return data

def get_weight_16bit(upper, lower):
    ## ARG
    #### upper: str list, upper 8 bit of weight in str '10000111'
    #### lower: str list, lower 8 bit of weight in str '11100011'
    ## RETURN
    #### weight: str list, 16 bit weight in str '1000011111100011'
    weight = [i+j for (i,j) in zip(upper,lower)]

    return weight

def trans_16bit_to_float(data, radix):
    ## ARG
    #### data: str list, 16 bit weight in str '1000011111100011'
    #### radix: float ndarray, power of binary format (ex. [2**2, 2**1, 2**0, 2**-1])
    ## RETURN
    #### sign: float list, sign of arg data (= MSB of data)
    #### digit.tolist(): float list, lower 15 bit of data
    #### w.tolist(): float list, weight in float format 
    w = np.array([])
    sign = [int(i[0]) for i in data]
    digit = np.array([[float(i) for i in j[1:]] for j in data])
    for i in range(len(digit)):
        if sign[i] == 0:
            num = np.dot(digit[i], radix)
        else:
            num = -1.0 * (np.dot(digit[i]*-1.0+1.0, radix) + 2**(-13))
        w = np.append(w, num)

    return sign, digit.tolist(), w.tolist()

def get_weight_float_format(dev, radix):
    ## ARG
    #### dev: serial port object
    #### radix: float ndarray, power of binary format (ex. [2**2, 2**1, 2**0, 2**-1])
    ## RETURN
    #### w: float list, weight in float format 
    u = get_byte_format(dev)
    l = get_byte_format(dev)
    w = get_weight_16bit(u, l)
    _, __, w = trans_16bit_to_float(w, radix)
    return w

def reduce_weight(warray):
    w = np.array(warray)
    reduce_w = np.sum(w, axis=0) / w.shape[0]
    return reduce_w.tolist()

def float_to_bin_format(float_list):
    bin_list = [float2binary(i, [1,2,13]) for i in float_list]
    bin_list = [i[4:]+'\n' for i in bin_list]
    bin_list = [i.encode() for i in bin_list]
    return bin_list

if __name__ == '__main__':
    ##### detect arduino #####
    my_serial = []
    radix = np.array([2**i for i in range(1,-14,-1)])

    for d in serial.tools.list_ports.comports():
        dtype = d.usb_description()
        if dtype and 'Arduino' in dtype:
            my_serial.append(serial.Serial(port=d[0], baudrate=9600))
            print d[0]

    for dev in my_serial:
        while dev.in_waiting == 0:
            sys.stdout.write('\r wait %s' % dev.port)
        print('')
        rec = dev.read()
        if rec == 'I':
            print('run %s' % dev.port)
            dev.write('J')
        else:
            print('recieve ERROR')

    print('')

    wh = []
    wo = []
    wo_l = []
    # wh = Weights()
    # wo = Weights()

    for dev in my_serial:
        while dev.in_waiting == 0:
            sys.stdout.write('\r wait %s' % dev.port)
        print('')
        # wh.append_weight(dev, radix)
        # wo.append_weight(dev, radix)
        w = get_weight_float_format(dev, radix)
        wh.append(w)
        # w = get_weight_float_format(dev, radix)
        u = get_byte_format(dev)
        l = get_byte_format(dev)
        w = get_weight_16bit(u, l)
        _, __, w = trans_16bit_to_float(w, radix)
        wo_l.append(l)
        wo.append(w)


    wh_reduced = reduce_weight(wh)
    wo_reduced = reduce_weight(wo)

    wh_bin = float_to_bin_format(wh_reduced)
    wo_bin = float_to_bin_format(wo_reduced)
    
    wh_int_u = [int(i[0:8], 2) for i in wh_bin]
    wh_int_l = [int(i[8:16], 2) for i in wh_bin]
    wo_int_u = [int(i[0:8], 2) for i in wo_bin]
    wo_int_l = [int(i[8:16], 2) for i in wo_bin]

    wh_send_data_u = [chr(i) for i in wh_int_u]
    wh_send_data_l = [chr(i) for i in wh_int_l]
    wo_send_data_u = [chr(i) for i in wo_int_u]
    wo_send_data_l = [chr(i) for i in wo_int_l]

    pdb.set_trace()
    for dev in my_serial:
        for send_data in wh_send_data_u:
            dev.write(send_data)
        dev.write('E')
        for send_data in wh_send_data_l:
            dev.write(send_data)
        dev.write('E')
        for send_data in wo_send_data_u:
            dev.write(send_data)
        dev.write('E')
        for send_data in wo_send_data_l:
            dev.write(send_data)
        dev.write('E')
        
    print("complete")
    print("")
    # pdb.set_trace()


            

