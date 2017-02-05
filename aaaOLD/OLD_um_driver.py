#!/usr/bin/env python3
# scripts/example/simple_rtu_client.py
#
from serial import Serial, PARITY_NONE
import sys
import logging
from umodbus import log
from logging import getLogger
import logging


from umodbus.utils import log_to_stream


log = getLogger('uModbus')
log.setLevel(logging.DEBUG)
log_to_stream(stream=sys.stderr, level=logging.DEBUG)
log.debug("Logging is set to debug")




# Override system installation for development purposes.
sys.path.insert(0,"/home/pi/rsrpi/uModbus")

from umodbus.client.serial import rtu

baud=9600
rsdev="/dev/rs485"


def get_serial_port():
    """ Return serial.Serial instance, ready to use for RS485."""
    port = Serial(port=rsdev, baudrate=baud, parity=PARITY_NONE,
                  stopbits=1, bytesize=8, timeout=1)

    fh = port.fileno()

    # A struct with configuration for serial port.
    # serial_rs485 = struct.pack('hhhhhhhh', 1, 0, 0, 0, 0, 0, 0, 0)
    # fcntl.ioctl(fh, 0x542F, serial_rs485)

    return port

def string2list(string, pad="\x00"):
    """ Packs a Python string into a list of ushorts so that uModbus
    functions can use them.  Since each Modbus register is 2 bytes
    (big-endian) it can hold 2 characters, so if the string is odd number
    in length.  It will be padded by the PAD character.

    :param string: String to be converted to a packed Struct.
    :param pad: Character to padd odd numbered length strings, default = 0x00
    :return: List of UNSIGNED SHORTS.
    """
    # Break the input string into a list of 2 char strings
    charList = [string[i:i + 2] for i in range(0, len(string), 2)]
    if len(string) % 2:
      # if it's an odd numbered length, append the PAD to the last element
      charList[-1] += str(pad)

    retList = []

    for i in charList:
      retList.append((ord(i[0]) << 8) + ord(i[1]))
    # import pdb; pdb.set_trace()
    return retList



def main ():
    # import pdb; pdb.set_trace()
    # import pdb; pdb.set_trace()


    # tempval = string2list("ABCDEFGHIJ");        # Even Number
    tempval = string2list("ABCDEFGHI");        # Odd Number

    serial_port = get_serial_port()

    # Returns a message or Application Data Unit (ADU) specific for doing
    # Modbus RTU.
    # message = rtu.write_multiple_coils(slave_id=1, starting_address=1, values=[1, 0, 1, 1])
    message = rtu.write_multiple_registers(slave_id=1,
                                           starting_address=1,
                                           values=string2list("ABCDEFG"));

    # Response depends on Modbus function code. In this case, it's the number
    # of registers written.

    try:
        response = rtu.send_message(message, serial_port)
    except Timeout:
        print("Timeout error")
        sys.exit(1)
    except:
        e = sys.exc_info()[0]
        print("Some other exception: %"%repr(e))
        sys.exit(3)

    serial_port.close()

if __name__ == '__main__':
    # try:
        main()
    # except:
        pass
        # import pdb;
        # pdb.xpm()
