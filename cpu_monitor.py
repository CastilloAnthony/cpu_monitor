import psutil
from threading import Thread
import time
import subprocess
import logging
import numpy as np
import win32api
import win32con

class Arbiter():
    def __init__(self):
        self.__threads = []
        self.__main_run = False
        self.__running = False
        self.__polling_speed = 60.0*3 # three minute default
        self.__cpu_usage = 0.0
        self.__cpu_usage_list = []
        self.__power_schemes = {}
        self.__curr_scheme = ''
        self._start()

    def __del__(self):
        del self.__main_run, self.__running, self.__polling_speed, self.__cpu_usage, self.__cpu_usage_list, self.__power_schemes, self.__curr_scheme
        while len(self.__threads) > 0:
            if self.__threads[-1].is_alive():
                self.__threads[-1].join(1)
                if self.__threads[-1].is_alive():
                    self.__threads[-1].terminate()
            del self.__threads[-1]
        del self.__threads

    def _start(self):
        self.__main_run = True
        self.__running = True
        # self._monitorUsage()
        self.__threads.append(Thread(target=self._monitorUsage, name='_monitorUsage'))
        self.__threads[len(self.__threads)-1].start()
        # self.__threads.append(Thread(target=self._getUsage, name='_getUsage'))
        # self.__threads[len(self.__threads)-1].start()
        # self.__threads.append(Thread(target=self._switchSetting, name='_switchSetting'))
        # self.__threads[len(self.__threads)-1].start()
        # while self.__running:
        #     time.sleep(0.1)
        exit_list = ['quit', 'exit', 'q']
        commands = ['help', 'exit', 'threads', 'status', 'schemes', 'restart', 'polling']
        affirmative = ['y', 'yes']
        while self.__main_run:
            user_input = input('Command: ')
            if user_input.lower() == 'help':
                print('Currently supported commands are:')
                for i in commands:
                     print(i)
                print('')
            elif user_input.lower() in exit_list:
                print(time.ctime()+' - Exiting, this may take up to '+str(self.__polling_speed)+'s.')
                self.__running = False
                self.__main_run = False
            elif user_input.lower() == 'threads':
                for i in self.__threads:
                    print(time.ctime()+' - Thread Name: '+str(i.name)+' Alive Status: '+str(i.is_alive()))
            elif user_input.lower() == 'status':
                print(time.ctime()+' - Average CPU Usage over the last '+str(self.__polling_speed)+'s: '+str(round(self.__cpu_usage, 1))+' '+str(round(self.__cpu_usage/len(self.__cpu_usage_list), 1))+'% '+str(self.__cpu_usage_list)) # +str(self.__cpu_usage))
                print(time.ctime()+' - Current '+self.__curr_scheme)#str(subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")))
            elif user_input.lower() == 'schemes':
                print(time.ctime()+' - The current schemes are:')
                for i in self.__power_schemes:
                    if i == 'Balanced':
                        print('\tName: '+str(i)+'\t\t\tGUID: '+str(self.__power_schemes[i]))
                    else:
                        print('\tName: '+str(i)+'\t\tGUID: '+str(self.__power_schemes[i]))
            elif user_input.lower() == 'restart':
                print(time.ctime()+' - Restarting threads...')
                while len(self.__threads) > 0:
                    print(time.ctime()+' - Killing thread '+str(self.__threads[0].name)+' this may take up to '+str(self.__polling_speed)+'s.')
                    self.__running = False
                    self.__threads[0].join(self.__polling_speed)
                    if self.__threads[0].is_alive():
                        self.__threads[0].terminate()
                    del self.__threads[0]
                self.__running = True
                self.__threads.append(Thread(target=self._monitorUsage, name='_monitorUsage'))
                self.__threads[len(self.__threads)-1].start()
                print(time.ctime()+' - Successfully restarted.')
            elif user_input.lower() == 'polling':
                print(time.ctime()+' - Current Polling Speed is '+str(self.__polling_speed)+'s')
                user_input2 = input('Do you want to change that? ')
                if user_input2.lower() in affirmative:
                    user_input3 = input('Enter an integer of seconds that you would like to set the polling speed to: ')
                    temp = ''
                    one = False
                    for c in user_input3:
                        if c != '.':
                            temp += c
                        elif one:
                            temp = 'Negative'
                            break
                        else:
                            one = True
                    if temp.isdecimal():
                        self.__polling_speed = float(user_input3)
                        print(time.ctime()+' - Current Polling Speed is '+str(self.__polling_speed)+'s')
                    else:
                        print(time.ctime()+' - Only numbers are acceptable.')
            time.sleep(0.1)

    def _monitorUsage(self):
        # print(str(time.ctime())+' - '+str(psutil.getself.__cpu_usageavg()))
        # print(str(time.ctime())+' - '+str(psutil.cpu_percent()))
        psutil.cpu_percent()
        time.sleep(5)
        raw_list = subprocess.run("powercfg -l", capture_output=True)
        self.__curr_scheme = subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")#[19:56]
        # print(str(time.ctime())+' - Current scheme is '+subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")) 
        # 36 characters long uuid
        # print(self.__curr_scheme[19:56])
        # print(list)
        # print(list.stdout.decode('ascii')[0:63])
        # print(list.stdout.decode('ascii')[0:74])
        # print(raw_list.stdout.decode('ascii')[74:])
        list = []
        string = ''
        for c in raw_list.stdout.decode('ascii')[74:]:
            if c != '\n' and c != '\r':
                string += c
            else:
                list.append(string)
                string = ''
        # for i in list:
        #     print(i)
        self.__power_schemes = {}
        for i in list:
            if 'High Performance' in i:
                self.__power_schemes['High Performance'] = i[19:56]
            elif 'Power saver' in i:
                self.__power_schemes['Power saver'] = i[19:56]
            elif 'Balanced' in i:
                self.__power_schemes['Balanced'] = i[19:56]

        while self.__running:            
            # self.__cpu_usage = psutil.getself.__cpu_usageavg() #[x / psutil.cpu_count() * 100 for x in psutil.getself.__cpu_usageavg()] # self.__cpu_usage[0] = 1min, self.__cpu_usage[1] = 5mins, self.__cpu_usage[2] = 15mins
            # self.__cpu_usage = float(psutil.cpu_percent())
            
            # # print(str(time.ctime())+' - Current self.__cpu_usage: '+str(self.__cpu_usage))
            # # if self.__cpu_usage[0] <= 20.0 and self.__cpu_usage[1] <= 20.0 and self.__cpu_usage[2] <= 20.0:
            # if self.__cpu_usage < 20.0:
            #     if subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")[19:56] != self.__power_schemes['Power saver']:#self.__curr_scheme:
            #         subprocess.run("powercfg -s "+self.__power_schemes['Power saver']) 
            #         self.__curr_scheme = subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")#[19:56]
            #         print(str(time.ctime())+' - Current scheme updated to '+str(subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")))
            # # elif self.__cpu_usage[0] >= 75.0 and self.__cpu_usage[1] >= 75.0:# and self.__cpu_usage[2] >= 50.0:
            # elif self.__cpu_usage >= 75.0:
            #     if subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")[19:56] != self.__power_schemes['High Performance']:#self.__curr_scheme:
            #         subprocess.run("powercfg -s "+self.__power_schemes['High Performance'], capture_output=True)
            #         self.__curr_scheme = subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")#[19:56]
            #         print(str(time.ctime())+' - Current scheme updated to '+str(subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")))
            # # elif self.__cpu_usage[0] >= 20.0 and self.__cpu_usage[1] >= 20.0 and self.__cpu_usage[2] >= 20.0:
            # elif self.__cpu_usage >= 20.0:
            #     if subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")[19:56] != self.__power_schemes['Balanced']: #self.__curr_scheme:
            #         subprocess.run("powercfg -s "+self.__power_schemes['Balanced'])
            #         self.__curr_scheme = subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")#[19:56]
            #         print(str(time.ctime())+' - Current scheme updated to '+str(subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")))
            self.__cpu_usage_list = np.asarray(psutil.cpu_percent(percpu=True))
            self.__cpu_usage = np.mean(self.__cpu_usage_list) # self.__cpu_usage_list.avg
            if self.__cpu_usage < 20.0:
                if subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")[19:56] != self.__power_schemes['Power saver']:#self.__curr_scheme:
                    subprocess.run("powercfg -s "+self.__power_schemes['Power saver']) 
                    self.__curr_scheme = subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")#[19:56]
                    print(str(time.ctime())+' - Current scheme updated to '+str(subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")))
            elif self.__cpu_usage >= 20.0:
                hp_switch = False
                for i in self.__cpu_usage_list:
                    if i >= 50.0:
                        if subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")[19:56] != self.__power_schemes['High Performance']:#self.__curr_scheme:
                            subprocess.run("powercfg -s "+self.__power_schemes['High Performance'], capture_output=True)
                            self.__curr_scheme = subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")#[19:56]
                            print(str(time.ctime())+' - Current scheme updated to '+str(subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")))
                            hp_switch = True
                if not hp_switch:
                    if subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")[19:56] != self.__power_schemes['Balanced']: #self.__curr_scheme:
                        subprocess.run("powercfg -s "+self.__power_schemes['Balanced'])
                        self.__curr_scheme = subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")#[19:56]
                        print(str(time.ctime())+' - Current scheme updated to '+str(subprocess.run("powercfg -getactivescheme", capture_output=True).stdout.decode("ascii")))
            time.sleep(self.__polling_speed)
# end Arbiter
        
if __name__ == '__main__':
    newArbiter = Arbiter()