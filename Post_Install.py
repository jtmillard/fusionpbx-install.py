'''
Created on May 3, 2016

@author: jim
'''

#------------------------------------------------------------------------------ 
# Post Intsalation informatioin
#------------------------------------------------------------------------------ 

def ipostinstall():
    msg = ["FusionPBX Post Installation Instructions",
           "FusionPBX is now installed there are a few steps to take.",
           "1. Open FusionPBX in a browser.",
           "2. Advanced -> Upgrade",
           "3. Click on App Defaults.",
           "4. Click on Execute Button.",
           "5. Status -> SIP Status",
           "6. Click start button for:",
           "   Soifia Status Profile External",
           "   Soifia status profile internal",
           " Also start the ipv6 options if you use ipv6",
           " ",
           "To enable HTTP provisioning:",
           "Advanced -> Default Settings",
           "Enter Provision in the search box",
           "Enter the http_auth_password and http_auth_username",
           "Enable both of these and the enabled entry",
           "You can do this by clicking on the False status for each",
           "Now you can set up your extensions and devices."
           ]
    
    for line in msg:
        print("%s" % (line))
        
    return
