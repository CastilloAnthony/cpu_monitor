# cpu_monitor
A simple script written in python for windows computers to monitor the cpu usage of the device and switch the power plan according to the device's (default 3 minute) average utilization percentage. 

### Updated 03/18/24
The script now recognizes if a single core is above 75% then it will switch to high performance. Otherwise it will take the averages of all cores to determine if it needs to be in power saver or balanced mode.
