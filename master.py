#!/usr/bin/env python3
#
# This is a simple driver program acting in master mode.
#
#

# Override system installation for development purposes.
import sys
sys.path.insert(0,"/home/pi/rsrpi/umodbus")

from serial import Serial, PARITY_NONE
import serial
import logging
from umodbus import log
from logging import getLogger
import logging
from umodbus.client.serial import rtu
from umodbus.utils import log_to_stream
import re
try:
    import gnureadline as readline
except ImportError:
    import readline

ignore_timeouts = True

########################################################
# Set up logging
########################################################
log = getLogger('uModbus')
log.setLevel(logging.DEBUG)
log_to_stream(stream=sys.stderr, level=logging.DEBUG)
log.debug("Logging is set to debug")

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


readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode emacs')

cmds = [
    ["sendregs", 3, "<register> <data>: Send <data> to <register(s)>"],
    ["readregs", 3, "<register> <len>: Read data from <register>"],
    ["sendreg", 3, "<register> [0x]<2bytesasWord>: Send single byte to <register>"],
    ['bread', 0, "Reads any queued bytes from serial device, timeout 1 sec"],
    ['bcheck', 0, "Displays how many chars are waiting in serial buffer"],
    ["help", 0, ": This help"],
    ["stop", 0, ": Exit Program"],
    ]

serial_port = None

# # port name, slave address (in decimal)
# instrument = minimalmodbus.Instrument('/dev/rs485', 2)
# instrument.serial.baudrate = 115200   # Baud
# instrument.debug = True

# Set global argument list scope for commands
cmdArgs = None

def main():
    global serial_port
    try:
        serial_port = get_serial_port()
    except:
        e = sys.exec_info()[0]
        print("Error opening serial port <{}>".format(repr(e)))
        sys.exit(1)

    # Print out initial commands
    for i in cmds:
        print("{}{} {}".format(
                i[0], " <device>" if i[1] else "", i[2]))

    while True:
        line = input('master: <cmd> <dev> [<opt_data>] ("stop" to quit, ? = help): ')
        if line == 'stop':
            break
        if line == 'help' or line == '?':
            for i in cmds:
                print("{}{} {}".format(
                        i[0], " <device>" if i[1] else "", i[2]))
            continue

        # FIXME: Get a better, more modular parsing routine, but this hack
        # will work for not.
        lineArr = line.split(' ',2)
        import pdb; pdb.set_trace()
        try:
            (cmd, device_s, remainder) = line.split(" ", 2)
        except ValueError:
            import pdb; pdb.set_trace()
            print("Not enough arguments provided")
            continue

        # Get the device number
        try:
            device=int(device_s)
        except:
            print("Device can only be integer: <{}>".format(device_s))
            continue

        foundCommand = False
        # Match which command
        for i in cmds:
            if i[0] == cmd:
                # Get remaining parms, if any
                cmdArgs = remainder.split(" ", i[1]-2)
                print("Found command {} with dev {:d} and parms <{}>".format(
                        i[0], device, repr(cmdArgs)))
                if len(cmdArgs) < (i[1]-1):
                    print("Error, not enough arguments for command, need %d, got %d"%
                           (i[1],len(cmdArgs)+1 ))
                    break
                foundCommand = True
                break
        # Must not have found a match
        if not foundCommand:
            print("Invalid command line: <{}>".format(line))
            continue

        # Dynamically call the processing function for the command
        log.debug("Calling command %s on dev %d with args <%s>"%(cmd, device,
                  repr(cmdArgs)))

        getattr(sys.modules[__name__], "do_%s" % cmd)(device, cmdArgs)

def do_bread(devnum, parmlist):
    """ Reads any outstanding bytes on the serial device (if any).
    Timeout is hardcoded to 1 second, and it'll only read up to 255 bytes.
    :param devnum: Modbus Device number as int.
    :param parmlist: Ignored but must be present because of how we dispatch
    """
    global serial_port
    import hexdump

    if (serial.in_waiting):
        print("bread: have %d bytes in waiting"%serial.in_waiting)
    else:
        return

    oldTimeout = serial_port.timeout()
    serial_port.timeout(1.0)        # Temp timeout

    try:
        buff = serial_port.read(serial.in_waiting)
    except:
        e = sys.exec_info()[0]
        print("bread: Unexpected error getting what's mine: %s"%
                repr(e))
        serial_port.timeout(oldTimeout)
        return

    serial_port.timeout(oldTimeout)
    outstring = hexdump.hexdump(buff, result='return')
    print("{:08x}: {}".format( buffpos, outstring[10:]))

def do_bcheck(devnum, parmlist):
    """ Reports on any outstanding bytes on the serial device.
    Timeout is hardcoded to 1 second.
    :param devnum: Modbus Device number as int.
    :param parmlist: Ignored but must be present because of how we dispatch
    """
    global serial_port

    if (serial_port.in_waiting):
        print("bread: have %d bytes in waiting"%serial.in_waiting)
    return






def do_sendregs(devnum, parmlist):
    # parms = <regnum as int> <stringdata as string>
    try:
        regnum = int(parmlist[0])
    except:
        print("<register> can only be a number");
        return
    dataString = parmlist[1]

    # Send the command
    message = rtu.write_multiple_registers(slave_id=devnum,
                                           starting_address=regnum,
                                           values=string2list(parmlist));

    try:
        response = rtu.send_message(message, serial_port)
    except Timeout:
        print("Timeout error, ignoring", file=sys.stderr)
        if ignore_timeouts:
            return
        sys.exit(1)
    except:
        e = sys.exc_info()[0]
        print("Some other exception: %"%repr(e))
        sys.exit(3)

    # print("Got a response back!");
    # import pdb; pdb.set_trace()

    return

def do_sendreg(devnum, parmlist):
    # parms = <regnum> <single_word> in dec or hex (if "0x" prepended)
    baseConv = 10
    # print("-- do_sendreg: DEV({}), WORD({})".format(devnum, repr(parmlist)))
    try:
        regnum = int(parmlist[0])
    except:
        print("<register> can only be a number");
        return

    singleWord_s = parmlist[1]
    if singleWord_s.startswith("0x"):
        baseConv = 16
        singleWord_s = singleWord_s[2:]
    try:
        singleWord = int(singleWord_s, baseConv)
    except ValueError:
        print("<singleWord> can only be a dec or hex (0x) number")
        return

    # Send the command
    # def write_single_register(slave_id, address, value):

    message = rtu.write_single_register(slave_id=devnum,
                                        address=regnum,
                                        value=singleWord);

    try:
        response = rtu.send_message(message, serial_port)
    except TimeoutError:
        print("Timeout error, ignoring", file=sys.stderr)
        if ignore_timeouts:
            return
        sys.exit(1)
    except:
        e = sys.exc_info()[0]
        print("Some other exception: %"%repr(e))
        sys.exit(3)

    print("Got a response back!");
    import pdb; pdb.set_trace()

def do_readregs(device, parmlist):
    # print("do_readregs: DEV({}), PARMS({})".format(device, repr(parmlist)))
    return

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




if __name__ == '__main__':
    main()
