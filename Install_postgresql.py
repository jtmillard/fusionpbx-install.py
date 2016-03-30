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

def ipostgresql():
    INSTALL_ROOT = os.getcwd()
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
    return
