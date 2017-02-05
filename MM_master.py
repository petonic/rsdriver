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

def do_readregs(device, parmlist):
    print("do_readregs: DEV({}), PARMS({})".format(device, repr(parmlist)))
    return




"""
    print('ENTERED: {!r}'.format(line))
    # Format is 1 number address, space, string to send
    mo=re.match(r'^([0-9]+)\s+(.*)$', line)
    if not mo:
        print("Error in input, format = 'devnum string to send'",
              file=sys.stderr);
        continue

    try:
        devnum = int(mo.group(1))
    except:
        print("Invalid device address: {}, can only use int".
            format(mo.group(1)))
        continue
    print("Device address is ", devnum)
    sendString = mo.group(2)
    if not(len(sendString)):
        print("String len must be more than 0", file=sys.stderr);
        continue
    try:
        instrument.write_string_flex(devnum, sendString)
    except IOError as e:
        print("IO Error: ", e, file=sys.stderr)
"""


if __name__ == '__main__':
    main()
