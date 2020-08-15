# WifiSignalRos
A Simple ROS Package to publish the Wifi Signal Strength as a Diagnostic Array Message (ROS)

## How to use 
The Package requires certain python dependencies. You can install them with
> chmod +x install.sh
>
> ./install.sh

## Run the node via
> roslaunch WifiSignalRos wifi.launch

## Echo the data via the topic
> rostopic echo /wifi_signal_status
