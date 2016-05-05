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


import shutil
import subprocess
import os
import sys
import FPBXParms


def ifail2ban():
    
    ipt_cmds = ["iptables -A INPUT -i lo -j ACCEPT",
                "iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT",
                "iptables -A INPUT -p tcp --dport 22 -j ACCEPT",
                "iptables -A INPUT -p tcp --dport 80 -j ACCEPT",
                "iptables -A INPUT -p tcp --dport 443 -j ACCEPT",
                "iptables -A INPUT -p tcp --dport 5060 -j ACCEPT",
                "iptables -A INPUT -p udp --dport 5060 -j ACCEPT",
                "iptables -A INPUT -p tcp --dport 5080 -j ACCEPT",
                "iptables -A INPUT -p udp --dport 5080 -j ACCEPT",
                "iptables -A INPUT -p udp --dport 16384:32768 -j ACCEPT",
                "iptables -P INPUT DROP",
                "iptables -P FORWARD DROP",
                "iptables -P OUTPUT ACCEPT",
                "iptables -A INPUT -p icmp --icmp-type echo-request -j ACCEPT",
                "iptables -I INPUT -j DROP -p tcp --dport 5060 -m string --string \"friendly-scanner\" --algo bm",
                "iptables -I INPUT -j DROP -p tcp --dport 5080 -m string --string \"friendly-scanner\" --algo bm",
                "iptables -I INPUT -j DROP -p udp --dport 5060 -m string --string \"friendly-scanner\" --algo bm",
                "iptables -I INPUT -j DROP -p udp --dport 5080 -m string --string \"friendly-scanner\" --algo bm"                
                ]
    
    INSTALL_ROOT = os.getcwd()
    if os.path.isfile("%s/resources/install.json" % (INSTALL_ROOT)):
        FPBXParms.PARMS = FPBXParms.load_parms(FPBXParms.PARMS)
    else:
        print("Error no install parameters")  
        sys.exit(1)  
    
    print("Setting up fail2ban to protect your system from several types of attacks")
    if os.path.isfile("%s/resources/fail2ban/jail.local" % (INSTALL_ROOT)):
        if FPBXParms.whitelist != None:
            shutil.copyfile("%s/resources/fail2ban/jail.package" % (INSTALL_ROOT), "/etc/fail2ban/jail.local")
        else:
            shutil.copyfile("%s/resources/fail2ban/jail.source" % (INSTALL_ROOT), "/etc/fail2ban/jail.local")
            shutil.copyfile("%s/resources/fail2ban/freeswitch-dos.conf" % (INSTALL_ROOT), "/etc/fail2ban/filter.d/freeswitch-dos.conf")
            shutil.copyfile("%s/resources/fail2ban/fusionpbx.conf" % (INSTALL_ROOT), "/etc/fail2ban/filter.d/fusionpbx.conf")
            if FPBXParms.whitelist != None:
                ftb = open("/etc/fail2ban/jail.local", 'a')
                ftb.write("[DEFAULT]")
                ftb.write("\n")
                ftb.write("ignoreip = %s" % (FPBXParms.whitelist))
                ftb.write("\n")
                ftb.close()
            ret = subprocess.call("systemctl restart fail2ban", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
            FPBXParms.check_ret(ret, "Restart fail2ban")
    
    print("Setting iptables rules")      
    for cmd in ipt_cmds:
        ret = subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        FPBXParms.check_ret(ret, cmd)
    print("")
    print("NOTE: Please read this before you continue!")
    print("Installing iptables persistence module")
    print("You will see two questions about saving the iptable rules")
    print("Please select yes for both when asked")
    input("press ENTER when you are ready")
    subprocess.call("apt-get -y install iptables-persistent", shell=True)
    return
