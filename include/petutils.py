
############################################################
############################################################
# Returns the serial number of the RPI as a string
#
# from:
#  http://raspberrypi.stackexchange.com/questions/2086/how-do-i-get-the-serial-number
############################################################
############################################################
def getserial():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"

  return cpuserial
