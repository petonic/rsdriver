#!/usr/bin/env python3
#
# This is a simple driver program acting in master mode.
#
#
#
import minimalmodbus
import re
import sys

try:
    import gnureadline as readline
except ImportError:
    import readline

readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode emacs')

cmds = [
    ["sendregs", 3, "<register> <data>: Send <data> to <register(s)>"],
    ["readregs", 3, "<register> <len>: Read data from <register>"],
    ["sendreg", 3, "<register> [0x]<2bytesasWord>: Send single byte to <register>"],
    ["help", 0, ": This help"],
    ["stop", 0, ": Exit Program"],
    ]



# # port name, slave address (in decimal)
# instrument = minimalmodbus.Instrument('/dev/rs485', 2)
# instrument.serial.baudrate = 115200   # Baud
# instrument.debug = True

# Set global argument list scope for commands
cmdArgs = None

def main():
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

        try:
            (cmd, device_s, remainder) = line.split(" ", 2)
        except ValueError:
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
                foundCommand = True
                break
        # Must not have found a match
        if not foundCommand:
            print("Invalid command line: <{}>".format(line))
            continue

        # Dynamically call the processing function for the command
        getattr(sys.modules[__name__], "do_%s" % cmd)(device, cmdArgs)

def do_sendregs(devnum, parmlist):
    # parms = <regnum> <stringdata>
    print("-- do_sendregs: DEV({}), PARMS({})".format(devnum, repr(parmlist)))
    try:
        regnum = int(parmlist[0])
    except:
        print("<register> can only be a number");
        return
    dataString = parmlist[1]
    # Set up new Instrument
    instrument = minimalmodbus.Instrument('/dev/rs485', devnum)
    instrument.serial.baudrate = 115200   # Baud
    instrument.debug = True
    try:
        instrument.write_string_flex(regnum, dataString)
    except IOError as e:
        print("*** IO Error: ", e)
        import pdb; pdb.set_trace()
    return

def do_sendreg(devnum, parmlist):
    # parms = <regnum> <single_word> in dec or hex (if "0x" prepended)
    baseConv = 10
    print("-- do_sendreg: DEV({}), WORD({})".format(devnum, repr(parmlist)))
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

    # Set up new Instrument
    instrument = minimalmodbus.Instrument('/dev/rs485', devnum)
    instrument.serial.baudrate = 115200   # Baud
    instrument.debug = True
    try:
        instrument.write_bit(regnum, singleWord)
    except IOError as e:
        print("*** IO Error: ", e)
    return


def do_readregs(device, parmlist):
    print("do_readregs: DEV({}), PARMS({})".format(device, repr(parmlist)))
    return





if __name__ == '__main__':
    main()
