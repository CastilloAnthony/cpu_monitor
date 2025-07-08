import time
import win32api
# import win32con
# from threading import Thread
import subprocess
# import logging
import json
# import os
from pathlib import Path

class Arbiter():
    def __init__(self) -> None:
        # self.__threads = []
        self.__running = False
        self.__power_schemes = {}
        self.__curr_scheme = self.get_curr_scheme()
        # self.__idle_threshold = 10*1
        self.__afk = False
    # end __init__

    def __del__(self) -> None:
        # while len(self.__threads) > 0:
        #     if self.__threads[-1].is_alive():
        #         self.__threads[-1].join(1)
        #         if self.__threads[-1].is_alive():
        #             self.__threads[-1].terminate()
        #     del self.__threads[-1]
        # del self.__threads
        del self.__running, self.__power_schemes, self.__afk, self.__curr_scheme#, self.__curr_scheme, self.__idle_threshold, self.__threads, self.__main_run, 
    # end __del__

    def start(self) -> None:
        self.__running = True
        self.read_settings()
        self.__power_schemes = self.get_schemes()
        self._monitor()
    # end _start

    def get_curr_scheme(self) -> str:
        return subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")
    # end get_curr_scheme

    def get_schemes(self) -> list:
        raw_list = subprocess.run("powercfg -l", capture_output=True)
        temp_list, temp_string, power_schemes_list = [], '', {}
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
            self.__curr_scheme = self.get_curr_scheme()
        print(f'{time.ctime()} - Idle time is now being monitored. The current power scheme is \n{self.__curr_scheme}')
        while self.__running:
            if self.get_idle_duration() > self.read_settings()['idle_threshold']:
                if not self.__afk:
                    self._afk()
                    self.__afk = True
            else:
                if self.__afk:
                    self._returned()
                    self.__afk = False
                else:
                    if self.__curr_scheme != self.get_curr_scheme():
                        print(f'{time.ctime()} - Current scheme has been changed externally to \n{self.get_curr_scheme()}')
                        self.__curr_scheme = self.get_curr_scheme()
            time.sleep(1)
    # end _monitor

    def get_idle_duration(self) -> float:
        return (win32api.GetTickCount() - win32api.GetLastInputInfo()) / 1000.0 # Convert to seconds from miliseconds
    # end get_idle_duration

    def _afk(self) -> None:
        settings = self.read_settings()
        if self.get_curr_scheme() != self.__power_schemes[settings['idle_scheme']]:
            subprocess.run("powercfg -s "+self.__power_schemes[settings['idle_scheme']]) 
            self.__curr_scheme = self.get_curr_scheme() #self.__power_schemes[settings['idle_scheme']]
            print(f'{time.ctime()} - Computer has been idle for {self.get_idle_duration()} seconds and is now is now considered AFK, the Power Scheme has been set to \n{self.get_curr_scheme()}')
    # end _afk

    def _returned(self) -> None:
        settings = self.read_settings() # Balanced or High Performance
        if self.get_curr_scheme() != self.__power_schemes[settings['active_scheme']]:
            subprocess.run("powercfg -s "+self.__power_schemes[settings['active_scheme']])
            self.__curr_scheme = self.get_curr_scheme() #self.__power_schemes[settings['active_scheme']]
            print(f'{time.ctime()} - Computer is no longer AFK, the Power Scheme has been set to \n{self.get_curr_scheme()}')
    # end _returned

    def read_settings(self) -> json:
        if Path('settings.json').exists():
            with open('settings.json', 'r') as file:
                settings = json.load(file)
            return settings
        else:
            self.write_settings(True)
    # end read_settings

    def write_settings(self, default: bool = False, settings: json =None) -> None:
        if default == True:
            settings = {
                'idle_threshold': 180,
                'idle_scheme': 'Power saver',
                'active_scheme': 'High Performance',
            }
            with open('settings.json', 'w') as file:
                json.dump(settings, file)
        elif settings != None:
            with open('settings.json', 'w') as file:
                json.dump(settings, file)            
    # end write_settings
# end Arbiter