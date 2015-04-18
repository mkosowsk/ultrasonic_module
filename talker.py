#!/usr/bin/env python
import rospy
import serial
import string

from std_msgs.msg import String
from std_msgs.msg import Float32

ser = serial.Serial(
    # make the port a param
    rospy.get_param('port', '/dev/ttyUSB0'),
    # port='/dev/ttyUSB0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
    #timeout=1
)

windowSize = 5

ser.isOpen()

def talker():
    pub = rospy.Publisher('chatter', Float32, queue_size=10)
    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    
    sensorReadingsList = []

    while not rospy.is_shutdown():
        byteData = ser.read(6)
        byteData += ser.read(ser.inWaiting())
        byteData = byteData.translate(None, 'R')
        strByteData = byteData[0]+byteData[1]+byteData[2]+byteData[3]
        
        if strByteData != '':
            try:
                intByteData = int(strByteData)
                floatByteData = intByteData/1000.0
                
                # use moving average
                sensorReadingsList.append(floatByteData)
                if len(sensorReadingsList) > windowSize:
                    sensorReadingsList.pop(0)
                if len(sensorReadingsList) == windowSize:
                    sensorAverage = sum(sensorReadingsList)/len(sensorReadingsList)
                    pub.publish(sensorAverage)
                rate.sleep()
            except ValueError:
                rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
