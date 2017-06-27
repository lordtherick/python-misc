#!/usr/bin/python

import sys, string, xmlrpclib, re, pprint

debug=1

jiraUsername=''
jiraPassword=''
jiraURL=''

server = xmlrpc.client.ServerProxy(jiraURL)
token = server.confluence2.login(jiraUsername, jiraPassword)

space = 'TT'
pagetree = server.confluence2.getPages(token, space) # Creates a list of dicts
allattachments = []
pp = pprint.PrettyPrinter(indent=1)

for pagedict in pagetree:
	if debug == 1:
		pp.pprint(pagedict)
	pageid = pagedict['id'] # Pulls the ID from the current dict from the pagetree list
	pagetitle = pagedict['title']
	confURL = pagedict['url']

	attachments = server.confluence2.getAttachments(token, pageid) # Creates another list of dicts
	d = {'title': pagetitle, 'attachments': attachments} # Adds attachment list to a temp dict

	if debug == 1:
		pp.pprint(attachments)
	for attachments in d['attachments']:
		outputStr = []
		outputStr.append(confURL.replace(jiraURL+"/display/",""))
		outputStr.append(attachments['title'])
		outputStr.append(attachments['fileSize'])
		outputStr.append(attachments['id'])
		outputStr.append(attachments['pageId'])
		print '|'.join(outputStr)

		#print treePlace+','+attachments['title']+','+attachments['fileSize']+','+attachments['id']+','+attachments['pageId']
		if debug == 1:
			exit('earlyout')

	allattachments.append(d) # Appends each new dict to the allattachments list
# print the page title and all attachments and their file types from the first dict in the allattachments list


#for each in allattachments:
#	print each['title']
#	for attachments in each['attachments']:
#		if (attachments['contentType'] == 'application/x-font-ttf' or attachments['contentType'] == 'application/vnd.oasis.opendocument.formula-template'):
#		print '...'+attachments['title'], attachments['contentType']


exit('Done!')
