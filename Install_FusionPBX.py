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
import time
import FPBXParms

#===============================================================================
# Folders that need acl modification
#===============================================================================
paclfolders = ["/etc/freeswitch",
              "/var/www",
              "/run/freeswitch",
              "/usr/local/freeswitch",
              "/usr/include/freeswitch",
              "/usr/lib/debug/usr/lib/freeswitch",
              "/usr/lib/freeswitch",
              "/usr/share/freeswitch",
              "/var/lib/freeswitch",
              "/var/log/freeswitch",
              "/var/www/fusionpbx"
              ]
saclfolders = ["/etc/freeswitch",
               "/run/freeswitch",
               "/usr/local/freeswitch",
               "/usr/src/freeswitch",
               "/usr/src/freeswitch.git",
               "/var/www/fusionpbx"
               ]

#===============================================================================
# Install FusionPBX
#===============================================================================

def ifusionpbx():
    INSTALL_ROOT = os.getcwd()
    if os.path.isfile("%s/resources/install.json" % (INSTALL_ROOT)):
        FPBXParms.PARMS = FPBXParms.load_parms(FPBXParms.PARMS)
    else:
        print("No predefined parameters to install FusionPBX")
        sys.exit(1)
        
    #=======================================================================
    # Determine web server type
    #=======================================================================
    
    if FPBXParms.PARMS["WebServer"][0] == "a":
        ws = "apache2"
    if FPBXParms.PARMS["WebServer"][0] == "N":
        ws = "nginx"
        
    #===============================================================================
    # Set up Postgresql
    #===============================================================================
    
    if FPBXParms.PARMS["DatabaseType"][0] == "P":
        print("Setting up Postgresql to support FusionPBX")
        # temp fix for pg_hba.conf permission problem
        if os.path.isfile("%s/resources/postgresql/pg_hba.conf" % (INSTALL_ROOT)):
            shutil.copyfile("%s/resources/postgresql/pg_hba.conf" % (INSTALL_ROOT), "/etc/postgresql/9.4/main/pg_hba.conf")
            ret = subprocess.call("systemctl restart postgresql", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
            FPBXParms.check_ret(ret, "Restarting postgres for pg_hba.conf changes")
            time.sleep(5) # Give postgresql time to settle
        tmp = open("/var/lib/postgresql/install.sql", 'w')
        tmp.write("CREATE ROLE %s WITH SUPERUSER CREATEROLE CREATEDB LOGIN PASSWORD '%s';\n" % (FPBXParms.PARMS["DBUser"][0], FPBXParms.PARMS["DBUserPassword"][0]))
        tmp.write("ALTER ROLE %s WITH PASSWORD '%s';\n" % (FPBXParms.PARMS["DBUser"][0], FPBXParms.PARMS["DBUserPassword"][0]))
        tmp.write("CREATE DATABASE %s with OWNER = %s;\n" % (FPBXParms.PARMS["DBName"][0], FPBXParms.PARMS["DBUser"][0]))
        tmp.write("CREATE DATABASE freeswitch with OWNER = %s;\n" % (FPBXParms.PARMS["DBUser"][0]))
        tmp.write("GRANT ALL PRIVILEGES ON DATABASE %s to %s;\n" % (FPBXParms.PARMS["DBName"][0], FPBXParms.PARMS["DBUser"][0]))
        tmp.write("GRANT ALL PRIVILEGES ON DATABASE freeswitch to %s;\n" % (FPBXParms.PARMS["DBUser"][0]))
        tmp.close()
        ret = subprocess.call("su -l postgres -c \"psql < /var/lib/postgresql/install.sql\"", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        FPBXParms.check_ret(ret, "Create DB, User, Password")
        os.remove("/var/lib/postgresql/install.sql")
    
    #=============================================================================== 
    # Install FusionPBX
    #=============================================================================== 
    
    os.chdir("/var/www")
    
    #=============================================================================== 
    # Create a git repository and clone from GitHub
    #=============================================================================== 
    
    if os.path.isfile(".git"):
        print("Updating FusionPBX code from GitHub")
        if os.path.isfile("/usr/bin/git"):
            ret = subprocess.call("/usr/bin/git pull", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        else:
            print("git version control is not installed")
            sys.exit(6)

    else:
        print("Cloning the FusionPBX code from GitHub")
        if os.path.isfile("/usr/bin/git"):
            ret = subprocess.call("/usr/bin/git init", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
            ret = subprocess.call("/usr/bin/git clone http://github.com/fusionpbx/fusionpbx", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        else:
            print("git version control is not installed")
            sys.exit(6)
        
    #=============================================================================== 
    # make sure www-data and freeswitch have access to the land
    #=============================================================================== 
    
    if FPBXParms.PARMS["FS_Install_Type"][0] == "P":
        for folder in paclfolders:
            if os.path.isdir(folder):
                ret = subprocess.call("setfacl -R -d -m u:www-data:rwx,g:www-data:rwx %s" % (folder), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
                FPBXParms.check_ret(ret, "Setting user acl for %s" % (folder))
                ret = subprocess.call("setfacl -R -m u:www-data:rwx,g:www-data:rwx %s" % (folder), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
                FPBXParms.check_ret(ret, "Setting user acl for %s" % (folder))
                ret = subprocess.call("setfacl -R -d -m u:www-data:rwx,g:freeswitch:rwx %s" % (folder), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
                FPBXParms.check_ret(ret, "Setting user acl for %s" % (folder))
                ret = subprocess.call("setfacl -R -m u:www-data:rwx,g:freeswitch:rwx %s" % (folder), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
                FPBXParms.check_ret(ret, "Setting user acl for %s" % (folder))
            else:
                print("SetFacl:")
                print("Error: %s is not a directory" % (folder))
    else:
        for folder in saclfolders:
            if os.path.isdir(folder):
                ret = subprocess.call("setfacl -R -d -m u:www-data:rwx,g:www-data:rwx %s" % (folder), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
                FPBXParms.check_ret(ret, "Setting user acl for %s" % (folder))
                ret = subprocess.call("setfacl -R -m u:www-data:rwx,g:www-data:rwx %s" % (folder), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
                FPBXParms.check_ret(ret, "Setting user acl for %s" % (folder))
                ret = subprocess.call("setfacl -R -d -m u:www-data:rwx,g:freeswitch:rwx %s" % (folder), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
                FPBXParms.check_ret(ret, "Setting user acl for %s" % (folder))
                ret = subprocess.call("setfacl -R -m u:www-data:rwx,g:freeswitch:rwx %s" % (folder), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
                FPBXParms.check_ret(ret, "Setting user acl for %s" % (folder))
            else:
                print("SetFacl:")
                print("Error: %s is not a directory" % (folder))
                    
    #===============================================================================
    # Insure FusionPBX config.php is not present
    #===============================================================================
    if os.path.isfile("/var/www/fusionpbx/resources/config.php"):
        os.remove("/var/www/fusionpbx/resources/config.php")
    
    #========================================================================
    # Make sure we are back in the install root directory
    #========================================================================
    os.chdir(INSTALL_ROOT)
       
    #===========================================================================
    # Set up the ssl certificate
    #TODO: Set up our own signed certificate when we can
    #===========================================================================
    
    if not os.path.islink("/etc/ssl/private/%s.key" % (ws)):
        os.symlink("/etc/ssl/private/ssl-cert-snakeoil.key", "/etc/ssl/private/%s.key" % (ws))
    if not os.path.islink("/etc/ssl/certs/%s.crt" % (ws)):
        os.symlink("/etc/ssl/certs/ssl-cert-snakeoil.pem", "/etc/ssl/certs/%s.crt" % (ws))
    
    #===============================================================================
    # Set up Web Server configuration to support FusionPBX
    #===============================================================================
    
    print("Setting Webserver to run FusionPBX")
    ret = subprocess.call("systemctl stop %s" % (ws), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    shutil.copyfile("%s/resources/%s/sites-available/fusionpbx.conf" % (INSTALL_ROOT, ws), "/etc/%s/sites-available/fusionpbx.conf" % (ws))
    if not os.path.islink("/etc/%s/sites-enabled/fusionpbx" % (ws)):
        os.symlink("/etc/%s/sites-available/fusionpbx.conf" % (ws), "/etc/%s/sites-enabled/fusionpbx.conf" % (ws))
    # We need to remove the default so it does not interfere with FusionPBX
    if os.path.islink("/etc/%s/sites-enabled/default.conf" % (ws)):
        os.remove("/etc/%s/sites-enabled/default.conf" % (ws))
    if os.path.islink("/etc/%s/sites-enabled/default" % (ws)):
        os.remove("/etc/%s/sites-enabled/default" % (ws))
    ret = subprocess.call("systemctl start %s" % (ws), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    
    #===============================================================================
    # Request user to run the install procedure in FusionPBX
    #===============================================================================
    
    print("The installation of FusionPBX is almost done.")
    print("Point your browser at http://%s/" % (FPBXParms.PARMS["IP"][0]))
    print("Hint: you may copy and paste the URL from the line above.")
    print("Please fill out the install pages with the information listed here.")
    FPBXParms.show_parms()
    print("I'll wait here while you do that.")
    print("Please wait until the login screen appears")
    input("Press Enter when you are finished. ")
    if os.path.isfile("/var/www/fusionpbx/resources/config.php"):
        print("Thank you")
    else:
        print("The configuration did not get saved, I can not go on.")
        print("WARNING: Fail2ban is not installed. Your system may be subject to attack!")
        sys.exit(6)
    return

#===============================================================================
# Restart freeswitch so FS will see any changes to config we just made.
#===============================================================================
    
    ret = subprocess.call("sytemctl restart freeswitch", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    FPBXParms.check_ret(ret, "Restarting Freeswitch")
    