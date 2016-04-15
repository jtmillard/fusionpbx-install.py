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

PG_KEY = {"trusty":"https://www.postgresql.org/media/keys/ACCC4CF8.asc"}
PG_REPO = {"trusty":"deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main"}

def ipostgresql():
    INSTALL_ROOT = os.getcwd()
    
    if FPBXParms.PARMS["Distro"][0] == "trusty":
        keyfile = open("/etc/apt/sources.list.d/pgdg.list", 'w')
        keyfile.write(PG_REPO[FPBXParms.PARMS["Distro"][0]])
        keyfile.write("\n")
        keyfile.close()
        ret = subprocess.call("curl %s  | apt-key add -" % (PG_KEY[FPBXParms.PARMS["Distro"][0]]) , stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        FPBXParms.check_ret(ret, "Adding package key for postgresql")
        ret = subprocess.call("apt-get update", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        FPBXParms.check_ret(ret, "Updating repositories after adding in postgresql 9.4")
        
    if os.path.isfile("%s/resources/install.json" % (INSTALL_ROOT)):
        FPBXParms.PARMS = FPBXParms.load_parms(FPBXParms.PARMS)
    else:
        print("Error no install parameters")
        sys.exit(1)
        
    if FPBXParms.PARMS["DatabaseType"][0] == "P":
        print("Installing Postgresql")
        pgidbg = open("pginstall.out", 'w')
        pgierr = open("pginstall.err", 'w')
        ret = subprocess.call("apt-get -y install postgresql-9.4 postgresql-client-9.4 postgresql-client-common postgresql-common ssl-cert", stdout=pgidbg, stderr=pgierr, shell=True)
        FPBXParms.check_ret(ret, "installing postgresql")
        pgidbg.close()
        pgierr.close()
        
    if FPBXParms.PARMS["DatabaseType"][0] == 's':
        ret = subprocess.call("apt-get install sqlite3", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        FPBXParms.check_ret(ret, "Installing sqlite3")
        
    return
