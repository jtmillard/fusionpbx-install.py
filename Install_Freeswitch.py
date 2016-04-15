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
import shutil
import FPBXParms


FS_KEY = {"jessie":"https://files.freeswitch.org/repo/deb/debian/freeswitch_archive_g0.pub",
          "Precise":"Add key here",
          "wheezy":"Add key here",
          "trusty":"https://files.freeswitch.org/repo/deb/debian/freeswitch_archive_g0.pub"
          } 
FS_REPO = {"jessie":"deb http://files.freeswitch.org/repo/deb/freeswitch-1.6/ jessie main",
           "precise":"add repo here",
           "wheezy":"add repo here",
           "trusty":"deb http://files.freeswitch.org/repo/deb/freeswitch-1.6/ jessie main"
           } 

DEPENDENCIES = "libyuv-dev libvpx2-dev"
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
# Install Freeswitch
#===============================================================================

def ifreeswitch():
    INSTALL_ROOT = os.getcwd()
    if os.path.isfile("%s/resources/install.json" % (INSTALL_ROOT)):
        FPBXParms.PARMS = FPBXParms.load_parms(FPBXParms.PARMS)
    else:
        print("Error no install parameters")
        sys.exit(1)
        
    if FPBXParms.PARMS["FS_Install_Type"][0] == "P":
        
    #===========================================================================
    # Install Freeswitch from packages
    #===========================================================================
   
        if FS_KEY[FPBXParms.PARMS["Distro"][0]] != "add repo here":
            print("Installing Freeswitch from Binary packages")
            # Check to see if the Freeswitch key has been installed
            keys = str(subprocess.check_output("apt-key list", shell = True))
            install_flag = True
            for line in keys:
                if "FreeSWITCH Package Signing Key" in line:
                    install_flag = False
            if install_flag:
                # Install the Freeswitch binary information
                ret = subprocess.call("curl %s  | apt-key add -" % (FS_KEY[FPBXParms.PARMS["Distro"][0]]) , stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
                FPBXParms.check_ret(ret, "Adding package key")
                ret = subprocess.call("echo %s  > /etc/apt/sources.list.d/freeswitch.list" % (FS_REPO[FPBXParms.PARMS["Distro"][0]]), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
                FPBXParms.check_ret(ret, "Setting distro in package list")
                
            # Now we actually install Freeswitch from binary packages
            ret = subprocess.call("apt-get update && apt-get install -y freeswitch-all freeswitch-all-dbg gdb", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
            FPBXParms.check_ret(ret, "Installing Freeswitch")
        else:
            print("I can not install from binary packages for the %s distro" % (FPBXParms.PARMS["Distro"][0]))
            sys.exit(4)
    else:
        
    #=============================================================================== 
    # Install Freeswitch from source
    #===============================================================================
    #===============================================================================
    # Set up necessary files
    #===============================================================================
        if not os.path.isdir("/usr/src/freeswitch/libs/spandsp/m4"):
            os.makedirs("/usr/src/freeswitch/libs/spandsp/m4")
        if os.path.isfile("%s/resources/freeswitch/libs/spandsp/m4/memmove.m4" % (INSTALL_ROOT)):
            shutil.copyfile("%s/resources/freeswitch/libs/spandsp/m4/memmove.m4" % (INSTALL_ROOT), "/usr/src/freeswitch/libs/spandsp/m4/memmove.m4")
        else:
            print("Missing needed file %s/resources/freeswitch/libs/spandsp/m4/memmove.m4" % (INSTALL_ROOT))
            sys.exit(12)
        if os.path.isfile("%s/resources/default/freeswitch" % (INSTALL_ROOT)):
            if not os.path.isdir("/etc/default"):
                os.makedirs("/etc/default")
            shutil.copyfile("%s/resources/default/freeswitch" % (INSTALL_ROOT), "/etc/default/freeswitch")

        if FS_KEY[FPBXParms.PARMS["Distro"][0]] != "add repo here":
            print("Installing Freeswitch from Source")
            # Check to see if the Freeswitch key has been installed
            keys = str(subprocess.check_output("apt-key list", shell=True))
            install_flag = True
            for line in keys:
                if "FreeSWITCH Package Signing Key" in line:
                    install_flag = False
            if install_flag:
                print("Installing source definitions")
                ret = subprocess.call("curl %s  | apt-key add -" % (FS_KEY[FPBXParms.PARMS["Distro"][0]]), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell = True)
                FPBXParms.check_ret(ret, "Setting source definitions")
                ret = subprocess.call("echo %s  > /etc/apt/sources.list.d/freeswitch.list" % (FS_REPO[FPBXParms.PARMS["Distro"][0]]), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell = True)
                FPBXParms.check_ret(ret, "Setting source list")
                print("Installing freeswitch video dependencies")
                ret = subprocess.call("apt-get update && apt-get install -y --force-yes freeswitch-video-deps-most", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell = True)
                print("Installing freeswitch libraries")
                ret = subprocess.call("apt-get update && apt-get install -y %s" % (DEPENDENCIES), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell = True)
                FPBXParms.check_ret(ret, "Installing video dependencies")
                print("Setting up git to pull rebase (Prevents conflicts)")
                ret = subprocess.call("git config --global pull.rebase true", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell = True)
                FPBXParms.check_ret(ret, "Configuring Git")
                os.chdir("/usr/src")
                if not os.path.exists("/usr/src/freeswitch.git"):
                    print("Retrieving the source from Freeswitch")
                    ret = subprocess.call("git clone https://freeswitch.org/stash/scm/fs/freeswitch.git -bv1.6 freeswitch.git", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell = True)
                    FPBXParms.check_ret(ret, "Retrieving the source using Git")
                os.chdir("freeswitch.git")
                print("Configuring the source install. (log in freeswitch_configure.log)")
                fslog = open("%s/freeswitch_configure.log" % (INSTALL_ROOT), 'w')
                ret = subprocess.call("./bootstrap.sh -j", stdout=fslog, stderr=fslog, shell = True)
                FPBXParms.check_ret(ret, "Setting bootstrap")
                fslog.close()
                ret = subprocess.call("./configure  --enable-core-pgsql-support", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell = True)
                FPBXParms.check_ret(ret, "Configuring source for your machine")
                print("Compiling Freeswitch (This may take a long time, log in freeswitch_compile.log)")
                fslog = open("%s/freeswitch_compile.log" % (INSTALL_ROOT), 'w')
                ret = subprocess.call("make", stdout=fslog, stderr=fslog, shell = True)
                FPBXParms.check_ret(ret, "Compiling Freeswitch")
                fslog.close()
                print("Installing Freeswitch. (log in freeswitch_install.log)")
                fslog = open("%s/freeswitch_install.log" % (INSTALL_ROOT), 'w')
                ret = subprocess.call("make install", stdout=fslog, stderr=fslog, shell = True)
                FPBXParms.check_ret(ret, "Installing Freeswitch")
                fslog.close()
                fslog = open("freeswitch_sounds_install.log", 'w')
                fslog.close()
                print("Installing sounds, log in freeswitch_sounds_install.log")
                fslog = open("freeswitch_sounds_install.log", 'a')
                print("64 Bit Sounds")
                ret = subprocess.call("make cd-sounds-install", stdout=fslog, stderr=fslog, shell=True)
                print("64 Bit Music on hold")
                ret = subprocess.call("make cd-moh-install", stdout=fslog, stderr=fslog, shell=True)
                print("32 Bit Sounds")
                ret = subprocess.call("make uhd-sounds-install", stdout=fslog, stderr=fslog, shell=True)
                print("32 Bit Music on hold")
                ret = subprocess.call("make uhd-moh-install", stdout=fslog, stderr=fslog, shell=True)
                print("16 Bit Sounds")
                ret = subprocess.call("make hd-sounds-install", stdout=fslog, stderr=fslog, shell=True)
                print("16 Bit Music on hold")
                ret = subprocess.call("make hd-moh-install", stdout=fslog, stderr=fslog, shell=True)
                print("8 Bit Sounds")
                ret = subprocess.call("make sounds-install", stdout=fslog, stderr=fslog, shell=True)
                print("8 Bit Music on hold")
                ret = subprocess.call("make moh-install", stdout=fslog, stderr=fslog, shell=True)
                print("Samples")
                ret = subprocess.call("make samples", stdout=fslog, stderr=fslog, shell=True)
                fslog.close()
                ret = subprocess.call("/usr/sbin/adduser --disabled-login --no-create-home --shell /bin/false --gecos FreeSWITCH freeswitch", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell = True)
                FPBXParms.check_ret(ret, "Adding freeswitch user")
                ret= subprocess.call("/usr/sbin/usermod -a -G audio freeswitch", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell = True)
                FPBXParms.check_ret(ret, "Adding freeswitch to audio group")
                print("Setting freeswitch to run automatically")
                ret = subprocess.call("chown -R www-data:www-data /usr/local/freeswitch", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell = True)
                FPBXParms.check_ret(ret, "Changing ownership of freeswitch")
                if os.path.isfile("/usr/local/freeswitch/bin/freeswitch"):
                    os.symlink("/usr/local/freeswitch/bin/freeswitch", "/usr/bin/freeswitch")
                    os.symlink("/usr/local/freeswitch/bin/fs_cli", "/usr/bin/fs_cli")
                else:
                    print("Abort freeswitch is not in the usual location")
                    sys.exit(15)
                shutil.copyfile("%s/resources/freeswitch/freeswitch.service" % (INSTALL_ROOT), "/lib/systemd/system/freeswitch.service")
                shutil.copyfile("%s/resources/etc/default/freeswitch" % (INSTALL_ROOT), "/etc/default/freeswitch")
                if not os.path.exists("/etc/freeswitch"):
                    os.makedirs("/etc/freeswitch")
                ret = subprocess.call("cp -a /usr/local/freeswitch/conf/* /etc/freeswitch/", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell = True)
                ret = subprocess.call("systemctl enable freeswitch", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell = True)
                ret = subprocess.call("systemctl unmask freeswitch.service", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell = True)
                ret = subprocess.call("systemctl daemon-reload ", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell = True)
                ret = subprocess.call("systemctl start freeswitch", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell = True)
                FPBXParms.check_ret(ret, "freeswitch start failed")
    os.chdir("%s" % INSTALL_ROOT)
    return
