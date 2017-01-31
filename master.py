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


# port name, slave address (in decimal)
instrument = minimalmodbus.Instrument('/dev/rs485', 2)
instrument.serial.baudrate = 115200   # Baud
instrument.debug = True
#
while True:
    line = input('master: <dev> <string to send> ("stop" to quit): ')
    if line == 'stop':
        break
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
