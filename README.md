# afk_monitor
A simple script written in python for windows computers to monitor the cpu usage of the device and switch the power plan according whether or not the device is idle or not. The default time till idle is 3 minute and the default idle scheme is Power saver while the default active scheme is High Performance. These settings can be changed by modifiying the settings.json file. The idle time is in seconds, and the schemes should be either "Power saver", "Balanced", or "High Performance"  

Run the start.py or the start.bat script to start the program.

### Changelog
- 07/08/25: The script has transitioned to monitoring idleness as opposed to utilization.
- 03/18/24: The script now recognizes if a single core is above 75% then it will switch to high performance. Otherwise it will take the averages of all cores to determine if it needs to be in power saver or balanced mode.
