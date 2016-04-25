'''
Created on Jan 21, 2016

@author: jim
'''
import subprocess
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

import os
import re
import sys
import json


#TODO: Restructure PARMS to all be separate vars not in a dictionary
# Also put the save and load routines in this module

PARMS = {
    "BDR":["N", "Flag indicating BDR type of installation should be Yes or No"],
#     "Host1":["NotSet", "The host name of the first server"],
#     "Host2":["", "The host name of the second server"],
    "IP":["", "The IP address of this server"],
#     "IP2":["", "The IP address of the second server"],
#     "Domain":["", "The domain name for this/these server(s)"],
#     "First":["", "Is this the first server of a set"],
    "User":["", "The user name for the FusionPBX Gui"],
    "UserPassword":["", "A temporary GUI user password"],
    "DBUser":["", "The user name for the FusionPBX Database"],
    "DBUserPassword":["", "A temporary Database user password"],
    "DBName":["", "The name of the database for FusionPBX"],
    "DatabaseType":["", "The type of database to be used sqlite or Postgresql (s/P)"],
    "WebServer":["", "The web server to use Apache or Nginx (a/N)"],
    "Distro":["", "The current Linux Distribution Name"],
    "FS_Install_Type":["", "Install Freeswitch from source or packages (s/P)"]
}

BDR_PARMS = ["Host1", "Host2", "IP", "IP2", "Domain", "First"]
# NON_BDR_PARMS = ["Host1", "IP", "Domain"]
NON_BDR_PARMS = []
COMMON_PARMS = ["User", "UserPassword", "DBUser", "DBUserPassword", "DBName", "DatabaseType", "WebServer", "FS_Install_Type"]
INSTALL_ROOT = os.getcwd()
INSTALL_PROGRESS = 0
whitelist = ''

#===============================================================================
# Check the return code from a system call and report errors
#===============================================================================

def check_ret(ret,description):
    if ret > 0:
        print("ERROR: system returned %d for %s" % (ret,description))
        sys.exit(ret)
    else:
        return()

#=============================================================================== 
# find_choice
# checks to see if (x/x) is in the description ( if so there is a choice )
# returns the options if they are found
#=============================================================================== 

def find_choice(var):
    tmp = re.search("\([A-Za-z]/[A-Za-z]\)", var)
    if tmp:
        tmp2 = re.search("[A-Za-z]/[A-Za-z]", tmp.group())
        tmp3 = tmp2.group(0)[:1]
        tmp4 = tmp2.group(0)[2:]
        if tmp3.isupper():
            tmp5 = tmp3
        else:
            tmp5 = tmp4
        return [tmp3, tmp4, tmp5]
    else:
        return None

#===============================================================================
# ask_parm 
# Ask for a parameter, accept Enter key for default if there is one
#=============================================================================== 

def ask_parm(index_m):
    """ Ask for the value of a parameter """
    my_options = find_choice(PARMS[index_m][1])
    if my_options:
        print(PARMS[index_m][1])
        answer = input("Enter a choice from the line above for %s : " % (index_m))
        if answer.upper() == my_options[0].upper():
            PARMS[index_m][0] = my_options[0]
            return
        if answer.upper() == my_options[1].upper():
            PARMS[index_m][0] = my_options[1]
            return
        if answer == "":
            PARMS[index_m][0] = my_options[2]
            return
        print("Error: you did not enter a proper choice")
        sys.exit(1)
    else:
        if PARMS[index_m][0] == "":
            print(PARMS[index_m][1])
            PARMS[index_m][0] = input("Enter a new value for %s : " % (index_m))
        else:
            print("%s Default is %s " % (PARMS[index_m][1], PARMS[index_m][0]))
            ans = input("Enter a new value for %s : " % (index_m))
            if ans != "":
                PARMS[index_m][0] = ans
    return
#===============================================================================
# show_parms 
# Show the parameters in a nice pretty table
#=============================================================================== 

def show_parms():
    """ Show the value of the currently active parameters
        There are two modes:
        BDR = Yes shows all parameters for a Multimaster Replicaton system
        BDR = No Shows only parameters for a single server switch """
    if PARMS["BDR"][0] == "Yes":
        parm_list_m = BDR_PARMS
        print("This server is part of a BDR installation")
    else:
        parm_list_m = NON_BDR_PARMS
        print("This server is a single FusionPBX server")
    
    print("Parameter        Value                Description")
    print("================ ==================== ======================")
    if len(parm_list_m) > 0:
        for val in parm_list_m:
            print("%-16s %-20s %s" % (val, PARMS[val][0], PARMS[val][1]))
    else:
        val = "IP"
        print("%-16s %-20s %s" % (val, PARMS[val][0], PARMS[val][1]))
        
    for val in COMMON_PARMS:
        print("%-16s %-20s %s" % (val, PARMS[val][0], PARMS[val][1]))

#===============================================================================
# save parms 
# Save the parameters in a file on the disk
#=============================================================================== 

def save_parms():
    """ Saves the current parameters in a file """
    parm_file_m = open("%s/resources/install.json" % (INSTALL_ROOT), 'w')
    json.dump(PARMS, parm_file_m)
    parm_file_m.close()

#===============================================================================
# load parms 
# Load the parameters from a file on the disk
#=============================================================================== 

def load_parms(my_parms):
    if os.path.isfile("%s/resources/install.json" % (INSTALL_ROOT)):
        PARM_FILE = open("%s/resources/install.json" % (INSTALL_ROOT), 'r')
        my_parms = json.load(PARM_FILE)
        PARM_FILE.close()
        return(my_parms)
    else:
        return(False)

#===============================================================================
# load show 
# Load and show the parameters
#=============================================================================== 

def load_show():
    load_parms()
    show_parms()
    
#===============================================================================
# Set resource path
#=============================================================================== 

def set_resource(path):
    INSTALL_ROOT = path
    return()

#===============================================================================
# Check for a program or os module installed
#===============================================================================

def is_installed(name):
    installed = subprocess.check_output("dpkg-query -l", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell = True)
    found = False
    for line in installed:
        if name in line:
            found = True
            return(found)
    return(found)
