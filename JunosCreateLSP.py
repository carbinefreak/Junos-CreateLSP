# $language = "python"
# $interface = "1.0"

# This script reads in a CSV file and creates LSP's inside of the designated routers
# The admin groups and the paths need to be defined prior to running this script.
# Created By Joe Keen (cnbm47@motorolasolutions.com)
# v0.2 08/22/16 - Added the ability to set the include/exclude type
# v0.3 09/01/16 - Added Recipricol LSP Creation aka R1-to-R2 and R2-to-R1 with the same admin groups
# v0.4 09/06/16 - Added check for null first cell to skip the line and checked for spaces in the hostname inputs

import csv


def main():

# Constants Modify for Devices and Network
	data = {}
	username = "admin"
	password = "password"
	isHeader = True
	retryTimer = "10"
	optimizeTimer = "120"
	sshRateLimit = "250"
	myShell = '#'

	# This will prompt the user where the LSP CSV file is
	# This is the title that is displayed in the window that opens
	filePathTitle = "Please select a CSV file"

	# Prompt the user with a window to open the file.  This just gets the path to the file.
	filePath = crt.Dialog.FileOpenDialog(filePathTitle)
	if filePath == '':
        #crt.Dialog.MessageBox ("You hit cancel")
		return 0
	else:
            # Open The File and Start Reading out the Rows Skipping the Header
            with open(filePath, 'rb') as f:
                reader = csv.reader(f, delimiter=',', quotechar='"', skipinitialspace=True)
                for row in csv.reader(f):
                    if(isHeader or row[0][0]=='#' or row[0][0]==''):
                        isHeader=False
                        continue
                    else:

                        # Lets Build up the Variables so we can connect to a router and build an LSP
                        router1Name = row[0]
                        router2Name = row[1]
                        router1IP = row[2]
                        router2IP = row[3]
                        primaryPath = row[4]
                        secondaryPath = row[5]
                        primaryType = row[6]
                        secondaryType = row[7]
                        primaryAdminGroups = row[8]
                        secondaryAdminGroups = row[9]
                        
                        # Check if there are spaces in the host names
                        # If there are spaces in the host name, then replace the space with '-'
                        if " " in router1Name:
                            router1Name = router1Name.replace(" ", "-")
                            
                        if " " in router2Name:
                            router2Name = router2Name.replace(" ", "-")

                        # Connect to Router 1
                        cmd = "/SSH2 /AUTH password,keyboard-interactive /L %s /PASSWORD %s %s" % (username, password, router1IP)
                        crt.Session.Connect(cmd)

                        # Enter config mode
                        objTab = crt.GetScriptTab()
                        objTab.Screen.Synchronous = True
                        objTab.Screen.Send("config\n")

                        # Wait for config mode '#", Fail if we don't enter config mode. Is this a juniper router, or are there permission issues
                        if(objTab.Screen.WaitForString(myShell, 30)!=True):
                            crt.Dialog.MessageBox ("Failed to Enter Config Mode, Please check Device.")
                            return

                        # Set the SSH Rate Limit to prevent blocking the script
                        objTab.Screen.Send("set system services ssh rate-limit 250\n")

                        # Wait for Command to complete
                        objTab.Screen.WaitForString(myShell)


                        # Create the Header for all the set commands
                        setLspHeader = "set protocols mpls label-switched-path " + router1Name + "-to-" + router2Name

                        # Create the LSP in the router
                        objTab.Screen.Send(setLspHeader + " to " + router2IP + "\n")

                        # Wait for Command to complete
                        objTab.Screen.WaitForString(myShell)

                        # Set the Retry for the LSP
                        objTab.Screen.Send(setLspHeader + "  retry-timer " + retryTimer + "\n")

                        # Wait for Command to complete
                        objTab.Screen.WaitForString(myShell)

                        # Set the optimize-timer for the LSP
                        objTab.Screen.Send(setLspHeader + "  optimize-timer " + optimizeTimer + "\n")

                        # Wait for Command to complete
                        objTab.Screen.WaitForString(myShell)

                        # Set fast-reroute for the LSP
                        objTab.Screen.Send(setLspHeader + "  fast-reroute" + "\n")

                        # Wait for Command to complete
                        objTab.Screen.WaitForString(myShell)

                        # Set Primary Path for the LSP
                        objTab.Screen.Send(setLspHeader + "  primary " + primaryPath + " admin-group " + primaryType + " " + primaryAdminGroups + "\n")

                        # Wait for Command to complete
                        objTab.Screen.WaitForString(myShell)

                         # Set Secondary Path for the LSP to Standby
                        objTab.Screen.Send(setLspHeader + "  secondary " + secondaryPath + " standby\n")

                        # Wait for Command to complete
                        objTab.Screen.WaitForString(myShell)

                        # Set Secondary Path for the LSP
                        objTab.Screen.Send(setLspHeader + "  secondary " + secondaryPath + " admin-group " + secondaryType + " " + secondaryAdminGroups + "\n")

                        # Wait for Command to complete
                        objTab.Screen.WaitForString(myShell)

                        # Commit the config
                        objTab.Screen.Send("commit and-quit\r\n")

                        # Wait for Command to complete, If we dont end up in usermode error out
                        if(objTab.Screen.WaitForString('>', 30)!=True):
                                crt.Dialog.MessageBox ("Failed to commit new config, please correct the above errors and retry the commit.")
                                return

                        # Go to Next Router
                        objTab.Session.Disconnect()

                        # Connect to Router 2
                        cmd = "/SSH2 /AUTH password,keyboard-interactive /L %s /PASSWORD %s %s" % (username, password, router2IP)
                        crt.Session.Connect(cmd)

                        # Enter config mode
                        objTab = crt.GetScriptTab()
                        objTab.Screen.Synchronous = True
                        objTab.Screen.Send("config\n")

                        # Wait for config mode '#", Fail if we don't enter config mode. Is this a juniper router, or are there permission issues
                        if(objTab.Screen.WaitForString(myShell, 30)!=True):
                            crt.Dialog.MessageBox ("Failed to Enter Config Mode, Please check Device.")
                            return

                        # Set the SSH Rate Limit to prevent blocking the script
                        objTab.Screen.Send("set system services ssh rate-limit 250\n")

                        # Wait for Command to complete
                        objTab.Screen.WaitForString(myShell)


                        # Create the Header for all the set commands
                        setLspHeader = "set protocols mpls label-switched-path " + router2Name + "-to-" + router1Name

                        # Create the LSP in the router
                        objTab.Screen.Send(setLspHeader + " to " + router1IP + "\n")

                        # Wait for Command to complete
                        objTab.Screen.WaitForString(myShell)

                        # Set the Retry for the LSP
                        objTab.Screen.Send(setLspHeader + "  retry-timer " + retryTimer + "\n")

                        # Wait for Command to complete
                        objTab.Screen.WaitForString(myShell)

                        # Set the optimize-timer for the LSP
                        objTab.Screen.Send(setLspHeader + "  optimize-timer " + optimizeTimer + "\n")

                        # Wait for Command to complete
                        objTab.Screen.WaitForString(myShell)

                        # Set fast-reroute for the LSP
                        objTab.Screen.Send(setLspHeader + "  fast-reroute" + "\n")

                        # Wait for Command to complete
                        objTab.Screen.WaitForString(myShell)

                        # Set Primary Path for the LSP
                        objTab.Screen.Send(setLspHeader + "  primary " + primaryPath + " admin-group " + primaryType + " " + primaryAdminGroups + "\n")

                        # Wait for Command to complete
                        objTab.Screen.WaitForString(myShell)

                         # Set Secondary Path for the LSP to Standby
                        objTab.Screen.Send(setLspHeader + "  secondary " + secondaryPath + " standby\n")

                        # Wait for Command to complete
                        objTab.Screen.WaitForString(myShell)

                        # Set Secondary Path for the LSP
                        objTab.Screen.Send(setLspHeader + "  secondary " + secondaryPath + " admin-group " + secondaryType + " " + secondaryAdminGroups + "\n")

                        # Wait for Command to complete
                        objTab.Screen.WaitForString(myShell)

                        # Commit the config
                        objTab.Screen.Send("commit and-quit\r\n")

                        # Wait for Command to complete, If we dont end up in usermode error out
                        if(objTab.Screen.WaitForString('>', 30)!=True):
                                crt.Dialog.MessageBox ("Failed to commit new config, please correct the above errors and retry the commit.")
                                return

                        # Go to Next LSP in the table
                        objTab.Session.Disconnect()

main()








