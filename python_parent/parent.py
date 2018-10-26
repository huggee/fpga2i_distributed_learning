import thread
import time
import sys
import serial
import serial.tools.list_ports
import pdb
import numpy as np
from lut_parser import float2binary
from time import sleep

if __name__ == '__main__':
    ##### detect arduino #####
    my_serial = []

    for d in serial.tools.list_ports.comports():
        dtype = d.usb_description()
        if dtype and 'Arduino' in dtype:
            my_serial.append(serial.Serial(port=d[0], baudrate=115200))
            print d[0]

    pdb.set_trace()

    w = [[0 for i in range(3)] for j in range(2)]
    w_all = np.array([])
    w = np.array([])
    w2 = np.array([-1.0, -0.75, 1.0])
    while 1:
        if my_serial[0].in_waiting > 0:
            recv_data_upper = my_serial[0].readline()
            recv_data_lower = my_serial[0].readline()
            upper = recv_data_upper.split(',')[:-1]
            lower = recv_data_lower.split(',')[:-1]
            upper_b = [format(int(i), '08b') for i in upper]
            lower_b = [format(int(i), '08b') for i in lower]
            binary = [i+j for (i,j) in zip(upper_b,lower_b)]
            radix = np.array([2**i for i in range(1,-14,-1)])
            sign = [int(i[0]) for i in binary]
            digit = np.array([[float(i) for i in j[1:]] for j in binary])
            for i in range(len(digit)):
                if sign[i] == 0:
                    num = np.dot(digit[i], radix)
                else:
                    num = -1.0 * (np.dot(digit[i]*-1.0+1.0, radix) + 2**(-13))
                w = np.append(w, num)

            w_all = np.append(w_all, w)
            w_all = np.append(w_all, w2)
            w_all = np.reshape(w_all, (-1, w.size))
            new_w = np.sum(w_all, axis=0) / w_all.shape[0]

            send_data = [float2binary(i, [1,2,13]) for i in new_w]
            send_data = [i[4:]+'\n' for i in send_data]
            send_data = [i.encode() for i in send_data]
            
            my_serial[0].write('D')

            pdb.set_trace()

            new_w = (w + w2) / 2

            


            pdb.set_trace()
            recv_data = my_serial[0].read_until(',')
            # recv_data = my_serial[0].read()
            i = 0
            while recv_data != '\n':
                # w[0][i] = recv_data
                print(recv_data)
                # recv_data = my_serial[0].read()
                recv_data = my_serial[0].read_until(',')
                i += 1
            if(i > 0):
                pdb.set_trace()
            

