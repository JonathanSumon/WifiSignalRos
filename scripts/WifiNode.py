#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from diagnostic_msgs.msg import KeyValue
from diagnostic_msgs.msg import DiagnosticStatus
from diagnostic_msgs.msg import DiagnosticArray

import subprocess
import time
from pythonwifi.iwlibs import Wireless
import commands
from ifparser import Ifcfg
import copy

def WifiList():
	ifConfigData = Ifcfg(commands.getoutput('ifconfig -a'))
	wifi=[]
	for interface in ifConfigData.interfaces:
		try:
			wifiInterface = Wireless(interface)
			essid = wifiInterface.getEssid()
			cmd = subprocess.Popen('iwconfig %s' % interface, shell=True, stdout=subprocess.PIPE)
			for line in cmd.stdout:
				if 'Link Quality' in line:
					sigIndex = line.find("Signal level")
					levelStr = line[sigIndex+13:]
					value = 0
					dBm_value = 0
					percent = 0
					if 'dBm' in levelStr:
						value = int(levelStr.split(" ")[0])
						dBm_value = value
						# -35 dBm < signal 100%a
						# -95 dBm > signal 0%
						if dBm_value > -35:
							percent = 100
						elif dBm_value < -95:
							percent = 0
						else:
							percent = (value + 95) * 100 / 60
							pass
					if '/' in levelStr:
						value = int(levelStr.split("/")[0])
						percent = value
						dBm_value = (value * 60 / 100) - 95
					wifiDescriptor = [interface, essid, dBm_value, percent]
					wifi.append(wifiDescriptor)
		except IOError:
			pass
	return wifi

def publisher():
	wifi_publisher = rospy.Publisher("wifi_signal_status", DiagnosticArray, queue_size = 1)
	rospy.init_node("Wifi_Publisher_Node") 
	WifiArray =  DiagnosticArray()
	WifiArray.header.frame_id = "base_link"   #Change Robot Name here
	rospy.loginfo("Wifi Signal Publisher Node has started")
	
	while not rospy.is_shutdown():
		WifiArray.header.stamp = rospy.get_rostime()
		del(WifiArray.status[:])
		for Wifinums in WifiList():
			keyvalue=KeyValue()
			Status = DiagnosticStatus()
			del(Status.values[:])
			keyvalue.key = "Signal Level"
			keyvalue.value = str(Wifinums[2])
			Status.values.append(copy.copy(keyvalue))
			keyvalue.key = "%"
			keyvalue.value = str(Wifinums[3])
			Status.values.append(copy.copy(keyvalue))
			Status.level = DiagnosticStatus.OK
			Status.name = Wifinums[1]
			Status.hardware_id = Wifinums[0]
			Status.message = "Device Ready"
			WifiArray.status.append(copy.copy(Status))
		wifi_publisher.publish(WifiArray)
		#rospy.loginfo(WifiArray)
		rospy.Rate(10).sleep()

if __name__ == '__main__':
    try:
        publisher()
    except rospy.ROSInterruptException:
        pass


