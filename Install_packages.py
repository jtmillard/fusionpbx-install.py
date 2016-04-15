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
import sys
import os
import FPBXParms

ADDON_APPS = {"jessie":"libdb-dev libpq-dev libtool-bin libtiff5-dev",
              "precise":"libtif4.dev",
              "wheezy":"libdb-dev libpq-dev libtiff5-dev",
              "trusty":"libdb-dev libpq-dev libtiff5-dev"
              }
COMMON_APPS = ["autoconf automake bison build-essential bzip2 curl devscripts fail2ban g++ gawk",
               "gettext git git-core ghostscript haveged htop lame libssl-dev libcurl4-openssl-dev libdb-dev libedit-dev",
               "libgdbm-dev libjpeg-dev libldns-dev libmemcached-dev libmyodbc libncurses5-dev libpcre3-dev libperl-dev",
               "libpq-dev libspeex-dev libspeexdsp-dev libsqlite3-dev libssl-dev libtiff5-dev yasm nasm",
               "libtiff-tools libtool make memcached ntp php-db php5 php5-cli php5-fpm php5-pgsql",
               "php5-sqlite php5-odbc php5-curl php5-imap php5-mcrypt pkg-config pkg-config python-dev",
               "python-software-properties screen ssl-cert ssh subversion time unixodbc unixodbc-dev vim"
               ]

#===============================================================================
# Install necessary packages to run freeswitch and FusionPBX
#===============================================================================

def ipackages():
    INSTALL_ROOT = os.getcwd()
    if os.path.isfile("%s/resources/install.json" % (INSTALL_ROOT)):
        FPBXParms.PARMS = FPBXParms.load_parms(FPBXParms.PARMS)
    else:
        print("Error no install parameters")
        sys.exit(1)
        
    print("Updating the OS repository")
    ret = subprocess.call("apt-get update", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    FPBXParms.check_ret(ret, "Updating the OS repository")
    print("Upgrading the OS to the latest packages")
    ret = subprocess.call("apt-get -y upgrade", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    FPBXParms.check_ret(ret,"Upgrading the OS to the latest packages")
    print("Installing additional packages needed for FusionPBX to run under OS %s" % (FPBXParms.PARMS["Distro"][0]))
    for i in range(0,len(COMMON_APPS) + 1):
        print(i, end="", flush=True)
    print("", end="\r", flush=True)
    for addons in COMMON_APPS:
        print("*", end="", flush=True)
        ret = subprocess.call("apt-get -y install %s" % (addons), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        FPBXParms.check_ret(ret,"Installing additional packages")
    addons = ADDON_APPS[FPBXParms.PARMS["Distro"][0]]
    print("*", end="")
    ret = subprocess.call("apt-get -y install %s" % (addons), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    FPBXParms.check_ret(ret,"Installing additional packages")
    print("\n")
    return
