#!/usr/bin/python

import sys, string, xmlrpc.client, re, pprint

debug=1


# MAIN START HERE

pp = pprint.PrettyPrinter(indent=1)
jiraUsername=''
jiraPassword=''
jiraURL=''

server = xmlrpc.client.ServerProxy(jiraURL)
token = server.confluence2.login(jiraUsername, jiraPassword)

username = 0
if len(sys.argv) > 1:
	username = sys.argv[1]
else:
	print("No pageid defined")

userInfo = server.confluence2.getUserInformation(token,username)

pp.pprint(userInfo)

exit('Done!')
