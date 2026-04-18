# Developed by Anthony Castillo
# Last Updated: 04/18/2026
import time
import json
import subprocess
from pathlib import Path
from psutil import cpu_percent
import win32api

class Arbiter():
    def __init__(self) -> None:
        self.__running, self.__afk = False, False
        self.__power_schemes = {}
        self.__curr_scheme = self.get_curr_scheme_id()
        self.__cpu_usage = cpu_percent(percpu=True)
        self.__lastPoll = time.time()
    # end __init__

    def __del__(self) -> None:
        del self.__running, self.__afk, self.__power_schemes, self.__curr_scheme, self.__cpu_usage, self.__lastPoll
    # end __del__

    def start(self) -> None: # Called externally
        self.__running = True
        self.read_settings()
        self.__power_schemes = self.get_schemes()
        self._monitor()
    # end _start

    def get_curr_scheme(self) -> str:
        return subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")
    # end get_curr_scheme

    def get_curr_scheme_id(self) -> str:
        raw_scheme = subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")
        scheme, begin = '', False
        for c in raw_scheme:
            if begin and c != '\n' and c != '\r' and c != ' ':
                scheme += c
            elif not begin and c == ':' :
                begin = True
            elif c == ' ' and len(scheme) > 2:
                scheme += c
                break
        return scheme
    # end _getSchemeID

    def get_schemes(self) -> dict:
        raw_list = subprocess.run("powercfg -l", capture_output=True)
        temp_list, temp_string, power_schemes_list = [], '', {}
        print(f'{time.ctime()} - Reading power schemes...')
        for c in raw_list.stdout.decode('ascii')[74:]:
            if c != '\n' and c != '\r':
                temp_string += c
            else:
                # temp_string += c # Not having this might be causing the scheme to look different than the one output by self.get_curr_scheme()
                temp_list.append(temp_string)
                temp_string = ''
        for i in temp_list:
            if 'High Performance' in i:
                power_schemes_list['High Performance'] = i[19:56]
            elif 'Power saver' in i:
                power_schemes_list['Power saver'] = i[19:56]
            elif 'Balanced' in i:
                power_schemes_list['Balanced'] = i[19:56]
        return power_schemes_list
    # end get_schemes

    def _monitor(self) -> None:
        settings = self.read_settings()
        if self.__curr_scheme != self.__power_schemes[settings['active_scheme']]:
            subprocess.run("powercfg -s "+self.__power_schemes[settings['active_scheme']])
            self.__curr_scheme = self.get_curr_scheme_id()
        print(f'{time.ctime()} - Idle time and CPU usage is now being monitored. The current power scheme is {self.get_curr_scheme()}')
        while self.__running:
            settings = self.read_settings()
            if (time.time()-self.__lastPoll) > settings['pollingSpeed']:
                self.__cpu_usage = cpu_percent(percpu=True)
                self.__lastPoll = time.time()
                if not self.__afk:
                    # for i in range(len(self.__cpu_usage)): # Single CPU usage
                    #     if self.__cpu_usage[i] > int(settings['active_cpu_threshold']):
                    #         self._set_to_high_performance()
                    #         break
                    #     elif i >= len(self.__cpu_usage)-1:
                    #         self._set_to_default()
                    if sum(self.__cpu_usage)/(len(self.__cpu_usage)+1) > int(settings['active_cpu_threshold']): # Average CPU usage
                        self._set_to_high_performance()
                    else:
                        self._set_to_default()
                    
            if self.get_idle_duration() > settings['idle_threshold']:
                if not self.__afk:
                    self._afk()
                    self.__afk = True
            else:
                if self.__afk:
                    self._returned()
                    self.__afk = False
                else:
                    if self.__curr_scheme != self.get_curr_scheme_id():
                        print(f'{time.ctime()} - Current scheme has been changed externally to {self.get_curr_scheme()}')
                        self.__curr_scheme = self.get_curr_scheme_id()
            self._draw_utilization_bar()
            time.sleep(1)
    # end _monitor

    def _draw_utilization_bar(self):
        bar_length = 20
        fraction = round(sum(self.__cpu_usage)/(len(self.__cpu_usage)+1), 1)/100
        arrow = "█" * int(fraction * bar_length)
        padding = "-" * (bar_length - len(arrow))
        print(f"\rCPU Usage: [{arrow}{padding}] {round(sum(self.__cpu_usage)/(len(self.__cpu_usage)+1), 1)}%\r", end="")
    # end _draw_utilization_bar

    def get_idle_duration(self) -> float:
        return (win32api.GetTickCount() - win32api.GetLastInputInfo()) / 1000.0 # Convert to seconds from miliseconds
    # end get_idle_duration

    def _afk(self) -> None:
        settings = self.read_settings()
        if self.get_curr_scheme_id() != self.__power_schemes[settings['idle_scheme']]:
            subprocess.run("powercfg -s "+self.__power_schemes[settings['idle_scheme']]) 
            self.__curr_scheme = self.get_curr_scheme_id() #self.__power_schemes[settings['idle_scheme']]
            print(f'{time.ctime()} - Computer has been idle for {self.get_idle_duration()} seconds and is now is now considered AFK, the Power Scheme has been set to {self.get_curr_scheme()}')
    # end _afk

    def _returned(self) -> None:
        settings = self.read_settings()
        if self.get_curr_scheme_id() != self.__power_schemes[settings['active_scheme']]:
            subprocess.run("powercfg -s "+self.__power_schemes[settings['active_scheme']])
            self.__curr_scheme = self.get_curr_scheme_id() #self.__power_schemes[settings['active_scheme']]
            print(f'{time.ctime()} - Computer is no longer AFK, the Power Scheme has been set to {self.get_curr_scheme()}')
    # end _returned

    def _set_to_power_saver(self) -> None: # Not Used
        if self.get_curr_scheme_id() != self.__power_schemes['Power saver']:
            subprocess.run("powercfg -s "+self.__power_schemes['Power saver'])
            self.__curr_scheme = self.get_curr_scheme_id() #self.__power_schemes['Power saver']
            print(f'{time.ctime()} - Computer is no longer AFK, the Power Scheme has been set to {self.get_curr_scheme()}')
    # end _setToPowerSaver

    def _set_to_default(self) -> None:
        settings = self.read_settings()
        if self.get_curr_scheme_id() != self.__power_schemes[settings['active_scheme']]:
            subprocess.run("powercfg -s "+self.__power_schemes[settings['active_scheme']])
            self.__curr_scheme = self.get_curr_scheme_id() #self.__power_schemes[settings['active_scheme']]
            print(f'{time.ctime()} - CPU utilization % is not over {self.read_settings()['active_cpu_threshold']}, the Power Scheme has been set to {self.get_curr_scheme()}')
    # end _setToBalanced

    def _set_to_high_performance(self) -> None:
        if self.get_curr_scheme_id() != self.__power_schemes['High Performance']:
            subprocess.run("powercfg -s "+self.__power_schemes['High Performance'])
            self.__curr_scheme = self.get_curr_scheme_id() #self.__power_schemes['High Performance']
            print(f'{time.ctime()} - CPU utilization % is over {self.read_settings()['active_cpu_threshold']}, the Power Scheme has been set to {self.get_curr_scheme()}')
    # end _setToHighPerformance

    def read_settings(self) -> dict:
        if Path('settings.json').exists():
            with open('settings.json', 'r') as file:
                settings = json.load(file)
            return settings
        else:
            self.create_settings()
            return self.read_settings()
    # end read_settings

    def create_settings(self) -> None:
        settings = {
            'pollingSpeed': 60,
            'idle_threshold': 180,
            'idle_scheme': 'Power saver',
            'active_scheme': 'Balanced',
            'active_cpu_threshold': 25.0,
        }
        with open('settings.json', 'w') as file:
            json.dump(settings, file, indent=4)        
    # end write_settings
# end Arbiter