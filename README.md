# CPU & Idleness Monitor
A simple script written in python for windows 11 (and 10) computers to monitor the cpu usage of the device and switch the power plan according to whether or not the device is idle or not. The default time till idle is 3 minute and the default idle scheme is Power saver while the default active scheme is Balanced and the high CPU utilization scheme is High Performance. The plling speed, idle time delay, idle scheme, active shceme, and utilization threshold can all be changed in the settings.json file. The polling speed and idle time are in seconds, the threshold is as a percentage, and the schemes should be either "Power saver", "Balanced", or "High Performance".

First run pip -r requirements.txt to install the required packages.
Then run the start.py file or the start.bat script to start the program.

### Changelog
- 04/18/26: Script now utilizes average CPU usage and idle time to determine which schemes to use. Displays the most recent CPU usage in the terminal.
- 07/08/25: The script has transitioned to monitoring idleness as opposed to utilization.
- 03/18/24: The script now recognizes if a single core is above 75% then it will switch to high performance. Otherwise it will take the averages of all cores to determine if it needs to be in power saver or balanced mode.
