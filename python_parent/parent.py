import thread
import time
import sys
import serial
import serial.tools.list_ports
import pdb
import numpy as np
from lut_parser import float2binary
from time import sleep

n_in = 4
n_h = 30
n_out = 2

reduce_interval = 100
mode = 'M'

def trans_16bit_to_float(data, radix):
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

def reduce_weight(warray):
    w = np.array(warray)
    reduce_w = np.sum(w, axis=0) / w.shape[0]
    return reduce_w.tolist()

def float_to_bin_format(float_list):
    bin_list = [float2binary(i, [1,2,13]) for i in float_list]
    bin_list = [i[4:]+'\n' for i in bin_list]
    bin_list = [i.encode() for i in bin_list]
    return bin_list

def read_buffer(dev, n1, n2):
    data = []
    for i in range(n1 * n2):
        while dev.in_waiting == 0:
            pass
        data.append(dev.read())
    return data


if __name__ == '__main__':
    ##### Ddetect Arduino #####
    my_serial = []
    radix = np.array([2**i for i in range(1,-14,-1)])

    for d in serial.tools.list_ports.comports():
        dtype = d.usb_description()
        if dtype and 'Arduino' in dtype:
            my_serial.append(serial.Serial(port=d[0], baudrate=115200))
            print('DETECT ' + d[0] + ' ' + d[1])
    print ('')

    ###### Initialize Arduino #####
    for dev in my_serial:
        while dev.in_waiting == 0:
            pass
        rec = dev.read()
        if rec == 'I':
            print('INIT %s' % dev.port)
            dev.write(chr(reduce_interval))
        else:
            print('recieve ERROR')    
    print('')

    ####### Run Arduino #####
    for dev in my_serial:
        i = 0
        while dev.in_waiting == 0:
            i += 1
            s = '.' * int(i/50000)
            sys.stdout.write('%s\r' % s)
            sys.stdout.flush()
        print('')
        rec = dev.read()
        if rec == 'R':
            print('RUN %s' % dev.port)
            dev.write(mode)

    print('')

    while mode == 'M':
        recv_w = []
        wh = []
        wo = []
        # wh = Weights()
        # wo = Weights()
        wh_b = []
        wo_b = []
        wo_b_l = []
        for dev in my_serial:
            while dev.in_waiting == 0:
                pass
            if(dev.read() == 'U'): # if recieved message is 'U'pload
                dev.write('S')     # then 'S'tart
                print('START UPLOAD %s' % dev.port)

            # now = time.time()            
            u = read_buffer(dev, n_in, n_h)
            u_int = [int(num.encode('hex'), 16) for num in u]
            u_bin = [format(i, '08b') for i in u_int]
            l = read_buffer(dev, n_in, n_h)
            l_int = [int(num.encode('hex'), 16) for num in l]
            l_bin = [format(i, '08b') for i in l_int]
            w = [i+j for (i,j) in zip(u_bin, l_bin)]
            w = trans_16bit_to_float(w, radix)
            wh.append(w)

            u = read_buffer(dev, n_h, n_out)
            u_int = [int(num.encode('hex'), 16) for num in u]
            u_bin = [format(i, '08b') for i in u_int]
            l = read_buffer(dev, n_h, n_out)
            l_int = [int(num.encode('hex'), 16) for num in l]
            l_bin = [format(i, '08b') for i in l_int]
            w = [i+j for (i,j) in zip(u_bin, l_bin)]
            w = trans_16bit_to_float(w, radix)
            wo.append(w)

            # print(time.time() - now)

            while dev.in_waiting == 0:
                pass
            if(dev.read() == 'E'): # if recieved message is 'E'nd
                print('END UPLOAD %s' % dev.port)
                print('')

        print('')
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


        for dev in my_serial:
            dev.write('D') # send message 'D'ownload
            while dev.in_waiting == 0:
                pass
            if(dev.read() == 'S'): # if recieved message is 'S'tart
                print('START DOWNLOAD %s' % dev.port)
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
            dev.write('C') # send message 'C'omplete
            print("END DOWNLOAD % s" % dev.port)
            print('')
        
        for dev in my_serial:
            dev.write(mode)

        print("complete")
        print("")
        # pdb.set_trace()


            

