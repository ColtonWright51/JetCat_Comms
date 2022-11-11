import numpy as np
import struct
import pandas as pd
import os
import matplotlib.pyplot as plt
import datetime


def decode_line(byte_array):
    """
    decode_line Decodes a line of bytes with the framing bytes included. Has
    nothing built in for byte stuffing or checksum yet.

    :param byte_array: byte_array is <class 'bytearray'>. Has no framing
    bytes included
    :return: Returns a Series of the processed data in order of JetCat
    documentation
    """

    engine_address = byte_array[0] # Address of engine to be accessed
    message_description = byte_array[1] << 8 | byte_array[2]
    sequence_number = byte_array[3]
    data_byte_count = byte_array[4]

    setpoint_rpm = (byte_array[5] << 8 | byte_array[6])*10
    setpoint_rpm_percent = (byte_array[7] << 8 | byte_array[8])*.01
    actual_rpm = (byte_array[9] << 8 | byte_array[10])*10
    actual_rpm_percent = (byte_array[11] << 8 | byte_array[12])*.01
    exhaust_gas_temp = (byte_array[13] << 8 | byte_array[14])*.1
    setpoint_pump_volts = (byte_array[15] << 8 | byte_array[16])*.01
    actual_pump_volts = (byte_array[17] << 8 | byte_array[18])*.01
    state = (byte_array[19])
    battery_volts = (byte_array[20] << 8 | byte_array[21])*.01
    battery_volts_percent = (byte_array[22])*.5
    battery_current = (byte_array[23] << 8 | byte_array[24])*.01
    airspeed = (byte_array[25] << 8 | byte_array[26])*.1
    pwm_thr = (byte_array[27] << 8 | byte_array[28])*.1
    pwm_aux = (byte_array[29] << 8 | byte_array[30])*.1
    crc16 = (byte_array[31] << 8 | byte_array[32])

    decoded_packet = [engine_address, message_description, sequence_number,
    data_byte_count, setpoint_rpm, setpoint_rpm_percent, actual_rpm,
    actual_rpm_percent, exhaust_gas_temp, setpoint_pump_volts,
    actual_pump_volts, state, battery_volts, battery_volts_percent,
    battery_current, airspeed, pwm_thr, pwm_aux, crc16]
    return decoded_packet


def byte_unstuffing(byte_array):
    """
    byte_unstuffing takes the byte_array and decodes any stuffing that might
    have happened. 
    """
    # TODO: Test this function. If it does not work, engine data will become
    # corrupted.

    for i in range(len(byte_array)-1):

        # "If 0x7D should be transmitted, transmit two bytes: 0x7D and 0x5D"
        # This is from JetCat documentation
        if(byte_array[i]==0x7D and byte_array[i+1]==0x5D):
            # Delete the extra byte
            del byte_array[i+1]
            # Append so that byte_array does not lose length. Code will
            # fail if this is not done.
            byte_array.append(0x00)


        # "If 0x7E should be transmitted, transmit two bytes: 0x7D and 0x5E"
        # This is from JetCat documentation
        if(byte_array[i]==0x7D and byte_array[i+1]==0x5E):
            # Replace two bytes with 0x7E
            byte_array[i] = 0x7E
            del byte_array[i+1]
            byte_array.append(0x00)


    return byte_array

def count_clip_unstuffed():
    """
    """

def check_crcs(decoded_numbers):
    if (decoded_numbers[len(decoded_numbers)-2] == \
        decoded_numbers[len(decoded_numbers)-1]):
        print("CRC's are equal")
    else:
        print("CRC's are NOT equal")


def save_fig(fig_id, folder_descrip , tight_layout=True, fig_extension="png", resolution=600):

    now = datetime.datetime.today()
    now = now.strftime("%Y-%m-%d")
    IMAGES_PATH = os.path.join(".", "images", now, folder_descrip)
    os.makedirs(IMAGES_PATH, exist_ok=True)
    now = datetime.datetime.today()
    now = now.strftime("%Y-%m-%d")
    fig_id = now + " " + fig_id
    path = os.path.join(IMAGES_PATH, fig_id + " " + folder_descrip + "." + fig_extension)
    print("Saving figure", fig_id)
    if tight_layout:
        plt.tight_layout()
    plt.savefig(path, format=fig_extension, dpi=resolution)

# def byte_array_to_string(byte_array):
#     # Convert byte array to a string so it can go into crc16 calculation

# def get_crc16(byte_array):
#     # Cut off the extra zeros in the byte_array, as well as the n-2 bytes sent
#     # The CRC calculation does not use the last two bytes, those contain the 
#     # CRC value!
#     #new_array = byte_array[:31]

#     length = len(byte_array)
#     crc_16_data = 0
#     print("Length of byte_array: ", length)
#     i = 0

#     while(length):

#         data = byte_array[i]
#         print("i: ", i, "data: ", data)
#         crc_16_data = crc16_update(crc_16_data, data)
#         print("crc_16_data: ", crc_16_data)
#         i = i + 1
#         length = length - 1
#     return crc_16_data

# def crc16_update(crc, data):
#     b8_crc = crc & 0xFF

#     data = data ^ (b8_crc & 0xFF)
#     print("data1: ", data)
#     data = data ^ (data << 4)
#     print("data2: ", data)
#     ret_val = ((data<<8) | ((crc&0xFF00)>>8)) ^ (data>>4) ^ (data<<3)
#     print("ret_val: ", ret_val)
#     return ret_val