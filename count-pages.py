#!/usr/bin/python

import sys, string, xmlrpc.client, re, pprint

debug=1

# MAIN START HERE

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

spaces = server.confluence2.getSpaces(token)

print("No. of Spaces = "+str(len(spaces)))

for space in spaces:
	pages = server.confluence2.getPages(token,space['key'])
	print(""+"|".join([space['key'],space['name'],str(len(pages))]))

exit('Done!')
