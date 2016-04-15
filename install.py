#!/usr/bin/python3
'''
Created on Jan 21, 2016
@author: Jim Millard

Install Freeswitch prior to installing Fusionpbx
'''
"""
        FusionPBX
        Version: MPL 1.1

        The contents of this file are subject to the Mozilla Public License Version
        1.1 (the "License"); you may not use this file except in compliance with
        the License. You may obtain a copy of the License at
        http://www.mozilla.org/MPL/

        Software distributed under the License is distributed on an "AS IS" basis,
        WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
        for the specific language governing rights and limitations under the
        License.

        The Initial Developer of the Original Code is
        Jim Millard <jmillard459@gmail.com>
        Portions created by the Initial Developer are Copyright (C) 2008-2016
        the Initial Developer. All Rights Reserved.

        Contributor(s):
        Mark J. Crane <markjcrane@fusionpbx.com>
"""

import subprocess
import os
import sys
import socket
import json
import argparse
import FPBXParms
import ask_questions
import Install_packages
import Install_postgresql
import Install_Freeswitch
import Install_FusionPBX
import Install_fail2ban
import Install_webserver

KNOWN_DISTROS = ["lucid",
                 "squeeze",
                 "wheezy",
                 "precise",
                 "jessie",
                 "wily",
                 "trusty"
                 ]
#===============================================================================
# TimeZone data
#===============================================================================

zones = {'':[]}
geoloc = {}
loc = []
maxlen = 0
INSTALL_ROOT = os.getcwd()
INSTALL_PROGRESS = 0

#===============================================================================
# Ask a yes or no question
#===============================================================================

def ask_yn(question):
    """ Ask a Yes or No question """
    ans = input("%s? (y/n) " % (question))
    if 'y' in ans or 'Y' in ans:
        return "Yes"
    if 'n' in ans or 'N' in ans:
        return "No"
    print("Sorry you must answer y or n to this question.")
    print("I don't know how to continue!")
    sys.exit(1)

#===============================================================================
# save parms 
# Save the parameters in a file on the disk
#=============================================================================== 

def save_parms():
    """ Saves the current parameters in a file """
    parm_file_m = open("%s/resources/progress.json" % (INSTALL_ROOT), 'w')
    json.dump(INSTALL_PROGRESS, parm_file_m)
    parm_file_m.close()

#===============================================================================
# load parms 
# Load the parameters from a file on the disk
#=============================================================================== 

def load_parms(my_parms):
    if os.path.isfile("%s/resources/progress.json" % (INSTALL_ROOT)):
        PARM_FILE = open("%s/resources/progress.json" % (INSTALL_ROOT), 'r')
        my_parms = json.load(PARM_FILE)
        PARM_FILE.close()
        return(my_parms)
    else:
        return(0)


#===============================================================================
# Install starts here
#===============================================================================

parser = argparse.ArgumentParser(description = "Install FusionPBX", epilog="The default is to install all")
install_group = parser.add_mutually_exclusive_group(required = False)
restart_group = parser.add_argument_group(title = "Restart")
oneonly_group = parser.add_argument_group(title = "One module only")
install_group.add_argument("-a", "--all", action = "store_const", const = 0, dest = "in_start", help = "Install all modules")
install_group.add_argument("-p", "--Packages", action = "store_const", const = 10, dest = "in_start", help = "Start install with required packages")
install_group.add_argument("-d", "--Database", action = "store_const", const = 20, dest = "in_start", help = "Start install with Database program")
install_group.add_argument("-s", "--FreeSwitch", action = "store_const", const = 30, dest = "in_start", help = "Start install with Freeswitch")
install_group.add_argument("-w", "--WebServer", action = "store_const", const = 40, dest = "in_start", help = "Start install with Web server")
install_group.add_argument("-f", "--FusionPBX", action = "store_const", const = 50, dest = "in_start", help = "Start install with FusionPBX")
install_group.add_argument("-b", "--fail2ban", action = "store_const", const = 60, dest = "in_start", help = "Set up fail2ban")
oneonly_group.add_argument("-o", "--One", action = "store_true", help = "Run One module only")
restart_group.add_argument("-r", "--restart", action = "store_true", help = "Restart a failed install")

#===============================================================================
# Default is to install all from the start
#===============================================================================

if len(sys.argv) == 1:
    args = parser.parse_args(["-a"])
else:
    args = parser.parse_args()
if not args.restart:   
    INSTALL_PROGRESS = args.in_start
    save_parms()
    
#===============================================================================
# Check for running as root
#===============================================================================

user = os.getuid()
if not user == 0:
    print("This install script must be run as root")
    sys.exit(1)
    
#===============================================================================
# Install dbus up front
# NOTE: It is possible to install with out dbus
#       dbus is needed to set the timezone and for other operations
#===============================================================================

print("Welcome to FusionPBX installation.")
print ("Installing dbus as it is required")
ret = subprocess.call("apt-get install dbus", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
FPBXParms.check_ret(ret, "Updating the OS repository")
    
#===============================================================================
# Make sure we have current parameters to continue
#===============================================================================

if args.restart and os.path.isfile("%s/resources/install.json" % (INSTALL_ROOT)):
    FPBXParms.PARMS = FPBXParms.load_parms(FPBXParms.PARMS)
else:
    ask_questions.iask_questions()
    if os.path.isfile("%s/resources/install.json" % (INSTALL_ROOT)):
        FPBXParms.PARMS = FPBXParms.load_parms(FPBXParms.PARMS)
    else:
        print("ERROR: no saved parameters to load")
        sys.exit(3)
        
#===============================================================================
# Set TimeZone before we do anything
#===============================================================================

if not args.restart:
    print()
    print("FusionPBX recommends setting the server time zone to GMT")
    ans = ask_yn("Do you want to set the time zone on this system")
    if ans == "Yes":
        settime = ask_yn("Do you want to set the time zone to GMT")
        if settime == "No":
            if user == "root":
                ret = subprocess.check_output("stty size", shell=True)
                ret = ret.decode("utf-8")
                parts = ret.split(" ")
                crows = int(parts[0])
                ccols = int(parts[1])
        
                zoneret = subprocess.check_output("timedatectl list-timezones", shell=True)
                zoneret = zoneret.decode("utf-8")
        
                for zone in zoneret.split('\n'):
                    parts = zone.split('/')
                    if len(parts) > 2:
                        location = "%s/%s" % (parts[1], parts[2])
                    else:
                        if parts[0] == '':
                            continue
                        location = parts[1]
                    if len(location) > maxlen:
                        maxlen = len(location)
                    if parts[0] in geoloc:
                        geoloc[parts[0]].append(location)
                    else:
                        geoloc[parts[0]] = [location]
        
                print("The geographical areas are:")
                i = 1
                for key in sorted(geoloc):
                    print("%2d : %-s" % (i, key))
                    i += 1
                    loc.append(key)
                geolocnum = input("Enter the number for you geographical location: ")
                geolocnum = int(geolocnum) - 1
                inc = int(len(geoloc[loc[geolocnum]]) / 3)
                remainder = int(len(geoloc[loc[geolocnum]]) % 3)
        
                print("These are the known locations for %s, please chose the closest to your location." % (loc[geolocnum]))
        
                j = 0
                last = False
                rowlimit = 2
                while j < len(geoloc[loc[geolocnum]]):
                    if (len(geoloc[loc[geolocnum]]) - j) < crows-1:
                        i = crows - (len(geoloc[loc[geolocnum]]) - j + 1)
                        last = True
                    else:
                        i = 0
                    while i < (crows - rowlimit):
                        print("%3d %-30s" % (j, geoloc[loc[geolocnum]][j]))
                        i += 1
                        j += 1
        
                    rowlimit = 1
                    subloc = input("Enter the number for your location (or press Enter for the next set of locations): ")
                    if last and len(subloc) == 0:
                        print("Sorry you must select one of these locations")
                        sys.exit(1)
                    else:
                        if len(subloc) == 0:
                            i = 0
                            continue
                        else:
                            subloc = int(subloc)
                            break
        
                print("I am setting the timezone to %s/%s" % (loc[geolocnum], geoloc[loc[geolocnum]][subloc]))
                ret = subprocess.check_output("timedatectl set-timezone %s/%s" % (loc[geolocnum], geoloc[loc[geolocnum]][subloc]), shell=True)
            else:
                print("TimeZone not set as we are testing")
        else:
            ret = subprocess.check_output("timedatectl set-timezone Europe/London", shell=True)
            print("Time zone set to GMT")
    else:
        print("The time zone is not changed on this system")    
    print("I will now check several necessary requirements")

#===============================================================================
# Check to see if we are in via ssh, if so, offer to white list the user's address 
#===============================================================================

ip = os.getenv("SSH_CONNECTION","127.0.0.1").split(" ")[0]
if len(ip) > 0:
    print()
    print("During initial installation it is easy to get locked out of your server. ")
    print("It appears you are connected from %s" % (ip))
    ans = ask_yn("Would you like to white list this address")
    if ans == 'Yes':
        FPBXParms.whitelist = ip
else:
    FPBXParms.whitelist = None
#------------------------------------------------------------------------------ 

#===============================================================================
# OK we have the parameters now let's see what release we are working under
#===============================================================================
# First check to see if we know how to install in this environment
#===============================================================================

ret = subprocess.check_output("uname -v", shell=True)
if "Debian" in str(ret) or "Ubuntu" in str(ret):
    pass
else:
    print("This install procedure only runs under a Debian or Ubuntu version of Linux")
    sys.exit(1)

lsb_line = subprocess.check_output('lsb_release -c', shell=True)
parts = lsb_line.split()
dist_code_name = parts[1]

if not dist_code_name.decode(encoding='UTF-8') in KNOWN_DISTROS:
    print("I do not know how to install on this distro named %s" % (dist_code_name))
    sys.exit(1)
FPBXParms.PARMS["Distro"][0] = dist_code_name.decode(encoding='UTF-8')

#===============================================================================
# Check the machine architecture
#===============================================================================

arch = subprocess.check_output("uname -m", shell = True)
if "64" in arch.decode(encoding='UTF-8'):
    pass
else:
    print("This machine appears to not be 64 bit")
    print("This can create problems in modern software")
    ans = ask_yn("Do you wish to continue")
    if ans == "No":
        sys.exit(0)
        
#===============================================================================
# Check connection to the Internet
#===============================================================================

REMOTE_SERVER = "www.google.com"
try:
    # see if we can resolve the host name -- tells us if there is
    # a DNS listening
    host = socket.gethostbyname(REMOTE_SERVER)
    # connect to the host -- tells us if the host is actually
    # reachable
    s = socket.create_connection((host, 80), 2)
except:
    print("I don't seem to be connected to the Internet")
    print("This script requires Internet connection")
    print("Please insure Internet availability and run this script again")
    sys.exit(2)

#===============================================================================
# Check for package install of freeswitch and distro trusty
#===============================================================================

if FPBXParms.PARMS["Distro"][0] == "trusty" and FPBXParms.PARMS["FS_Install_Type"][0] == 'P':
    print("There are no packages for Ubuntu trusty, I will install from source")
    FPBXParms.PARMS["FS_Install_Type"][0] = 's'

FPBXParms.save_parms()

#===============================================================================
# One last time let the user verify we are ready to begin
#===============================================================================

FPBXParms.show_parms()
print("The Linux distribution appears to be code named %s" % (FPBXParms.PARMS["Distro"][0]))
print()
INSTALL_PROGRESS = load_parms(INSTALL_PROGRESS)



#===============================================================================
# Ask the burning question
#===============================================================================

if not args.restart:
    answer = ask_yn("Do you want to start the install")
else:
    answer = ask_yn("Do you want to re-start the install")
if answer == "Yes":
    # print("Progress %d" % (INSTALL_PROGRESS))


    if args.restart:
        # We are restarting a failed install
        if INSTALL_PROGRESS < 10:
            print("This is a new install, you should not request a restart")
            print("Install Progress is %d" % INSTALL_PROGRESS)
            sys.exit(0)
        
#===============================================================================
# Install necessary packages
#===============================================================================

    if INSTALL_PROGRESS < 11:
        Install_packages.ipackages()
        INSTALL_PROGRESS = 12
        save_parms()
        if args.One:
            sys.exit(0)
        
#===========================================================================
# Install Postgresql 
#===========================================================================

    if INSTALL_PROGRESS < 21:
        Install_postgresql.ipostgresql()
        INSTALL_PROGRESS = 22
        save_parms()
        if args.One:
            sys.exit(0)

#===============================================================================
# Install Freeswitch
#===============================================================================
    
    if INSTALL_PROGRESS < 31:
        Install_Freeswitch.ifreeswitch()
        INSTALL_PROGRESS = 32
        save_parms()
        if args.One:
            sys.exit(0)

#===============================================================================
# Install the web server
#===============================================================================
    
    if INSTALL_PROGRESS < 41:
        Install_webserver.iwebserver()
        INSTALL_PROGRESS = 42
        save_parms()
        if args.One:
            sys.exit(0)

#===============================================================================
# Install FusionPBX
#===============================================================================

    if INSTALL_PROGRESS < 51:
        Install_FusionPBX.ifusionpbx()
        INSTALL_PROGRESS = 52
        save_parms()
        if args.One:
            sys.exit(0)

#===============================================================================
# Set up fail2ban
#===============================================================================

    if INSTALL_PROGRESS < 61:
        Install_fail2ban.ifail2ban()
        INSTALL_PROGRESS = 62
        save_parms()
        if args.One:
            sys.exit(0)

#===============================================================================
# Install Completed
#===============================================================================

else:
    print("Thank you for visiting")
    sys.exit(0)
    
print("\n\n")
print("===========================================")
print("Your installation of FusionPBX is completed")
print("You may log in and set up your system")
print("===========================================")
print("Thank you for choosing FusionPBX")
print("===========================================")
