#!/usr/bin/python3
""" Ask questions module for Fusionpbx install script
    Has no arguments.
    Output is a single file, "install.json"
    containing all of the parameters needed for the install script
"""
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

import sys
import os
import random
import FPBXParms
import socket


INSTALL_ROOT = os.getcwd()
LOOPNUMBER = 0

#===============================================================================
# Make up a temporary password
#===============================================================================

def mkpass():
    """ Make a simi-secure temporary password
    """
    words = []
    symbols = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "+", "="]
    numsymbols = len(symbols) - 1

    listofwords = open("%s/resources/words" % (INSTALL_ROOT), 'r')

    for word in listofwords.readlines():
        word = word.strip()
        words.append(word)
    numwords = len(words) - 1
    listofwords.close()

    word1 = words[random.randint(0, numwords)]
    word1 = word1.capitalize()
    word2 = words[random.randint(0, numwords)]
    word2 = word2.capitalize()
    number = str(random.randint(0, 9))
    symbol = symbols[random.randint(0, numsymbols)]
    password = word1 + number + word2 + symbol
    return password

#===============================================================================
# Ask a yes or no question
#===============================================================================

def ask_yn(question):
    """ Ask a Yes or No question """
    ans = input("%s? (y/n) " % (question)).lower()
    if 'y' in ans:
        return "Yes"
    if 'n' in ans:
        return "No"
    print("Sorry you must answer y or n to this question.")
    print("I don't know how to continue!")
    sys.exit(1)


#===============================================================================
# Main code starts here
#===============================================================================

def iask_questions():    
    
    print("I am checking to see if there are parameters already defined")
    
    #===============================================================================
    # Load the previously saved parameters
    #===============================================================================
    
    if os.path.isfile("%s/resources/install.json" % (INSTALL_ROOT)):
    
        FPBXParms.PARMS = FPBXParms.load_parms(FPBXParms.PARMS)
    
        print("I found the following parameters")
        FPBXParms.show_parms()
    
        USEPARMS = ask_yn("Do you want to use them")
        if USEPARMS == "Yes":
            pass
#             print("In loop %d" % (LOOPNUMBER))
#             LOOPNUMBER += 1
        else:
    #===============================================================================
    # Start asking the hard questions
    #===============================================================================
            print("Very well I will ask you several questions.")
            print("Note: if a question has '(a/B)' in it, 'B' is the default")
            print("If a question has a value listed that is the default")
            print("All default values can be selected by just pressing Enter")
            print("If a parameter does not have a default, a value must be entered")
            
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('google.com', 0))
            FPBXParms.PARMS["IP"][0] = (s.getsockname()[0])
        
            BDR_ANS = "No"
#             BDR_ANS = ask_yn(FPBXParms.PARMS["BDR"][1])
            FPBXParms.PARMS["BDR"][0] = BDR_ANS
            if BDR_ANS == "Yes":
                PARM_LIST = FPBXParms.BDR_PARMS
            else:
                PARM_LIST = FPBXParms.NON_BDR_PARMS
    
            if len(PARM_LIST) > 0:
                for index in PARM_LIST:
                    FPBXParms.ask_parm(index)
    
            for index in FPBXParms.COMMON_PARMS:
                FPBXParms.ask_parm(index)
    
    #======================================================================
    # Make up some passwords that are secure and easy to remember
    #======================================================================
    
    #         FPBXParms.PARMS["FPBXuserPassword"][0] = mkpass()
    #         FPBXParms.PARMS["FPBXDBUserPassword"][0] = mkpass()
    
            FPBXParms.save_parms()
    else:
        print("There is no predefined parameter file.")
        print("Please answer the following questions.")
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('google.com', 0))
        FPBXParms.PARMS["IP"][0] = (s.getsockname()[0])
#        For now we are only installing a single switch, No BDR
        BDR_ANS = "No"
#         BDR_ANS = ask_yn(FPBXParms.PARMS["BDR"][1])
        FPBXParms.PARMS["BDR"][0] = BDR_ANS
        if BDR_ANS == "Yes":
            PARM_LIST = FPBXParms.BDR_PARMS
        else:
            PARM_LIST = FPBXParms.NON_BDR_PARMS
        if len(PARM_LIST) > 0:
            for index in PARM_LIST:
                FPBXParms.ask_parm(index)
    
        for index in FPBXParms.COMMON_PARMS:
            FPBXParms.ask_parm(index)
    
    #======================================================================
    # Make up some passwords that are secure and easy to remember
    #======================================================================
    
    #     FPBXParms.PARMS["FPBXuserPassword"][0] = mkpass()
    #     FPBXParms.PARMS["FPBXDBUserPassword"][0] = mkpass()
    
    #===========================================================================
    # We need to check for Ubuntu and insure it is a source install
    #===========================================================================
        
        if FPBXParms.PARMS["Distro"][0] == "trusty":
            FPBXParms.PARMS["FS_Install_Type"][0] = "s"
            print("This install is on Ubuntu and only source is currently configured")
            print("I have set your Freeswitch install type to source")
        
        FPBXParms.save_parms()
            
    return