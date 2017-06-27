#!/usr/bin/python
# Updated for python 3.6+


import os, sys, string, xmlrpc.client, re, pprint, datetime

debug=1

def attachmentsSize(server,token,pageid,depth):
	asize = 0
	depth += 1

	try:
		attachments = server.confluence2.getAttachments(token, pageid) # Creates another list of dicts
	except xmlrpc.client.Fault as err:
		print("A fault occurred")
		print("Fault code: %d" % err.faultCode)
		print("Fault string: %s" % err.faultString)
		sleep(2)
		return 0

	lastUpdate = xmlrpc.client.DateTime(1)
	print("LAST UPDATE "+str(lastUpdate))

	for attachment in attachments:
		asize += int(attachment['fileSize'])

		if lastUpdate < attachment['created']: lastUpdate = attachment['created']

		spaceItem = {
			'type': 'attachment',
			'id': attachment['id'],
			'parent': pageid,
                        'size': int(attachment['fileSize']),
                        'depth': depth,
			'created': attachment['created'],
			'creator': attachment['creator'],
                        'title': attachment['fileName']}
		spaceList.append(spaceItem)

	return {'size': asize , 'lastUpdate': lastUpdate}

def treeSize(server,token,pageItem,parentPath,depth,doChildPages):
	depth += 1

	pageid = pageItem['id']
	aInfo = attachmentsSize(server,token,pageid,depth)

	directorySize = aInfo['size']
	lastUpdate = aInfo['lastUpdate']

	childPages = server.confluence2.getChildren(token,pageid) # get child pages
	if doChildPages == 1:
		for pagedict in childPages:
			parentPath.append(pageItem['title'])

			childInfo = treeSize(server,token,pagedict,parentPath,depth,doChildPages)
			directorySize += childInfo['size']
			if lastUpdate < childInfo['lastUpdate']: lastUpdate = childInfo['lastUpdate']

			parentPath.pop()

	created = xmlrpc.client.DateTime(0)
	creator = "not defined"
	modified = lastUpdate
	modifier = ""
	if modified > xmlrpc.client.DateTime(0): modifier = "update from child"

	# trying this - might be too memory intensive.
	if directorySize > 0:
		pageInfo = server.confluence2.getPage(token,pageid) # get page Details
		if pageInfo:
			if 'creator' in pageInfo: creator = pageInfo['creator']
			if 'created' in pageInfo: created = pageInfo['created']
			if 'modified' in pageInfo:
				if modified < pageInfo['modified']:
					modified = pageInfo['modified']
					if 'modifier' in pageInfo: modifier = pageInfo['modifier']
			if 'content' in pageInfo: directorySize += len(pageInfo['content'])

		del pageInfo

	childPath = list(parentPath)

	spaceItem = {
		'type': 'page',
		'id': pageid,
		'path': childPath,
		'title': pageItem['title'],
		'created': created,
		'creator': creator,
		'modified': modified,
		'modifier': modifier,
		'depth': depth,
		'size': directorySize}

	if debug == 1:
		print("ADDING PAGE "+pageItem['title']+" TO THE ARRAY")
		pp.pprint(spaceItem['path'])

	spaceList.append(spaceItem)

	depth -= 1
	return {'size': directorySize, 'lastUpdate': modified}

def GetHumanReadable(size,precision=2):
	suffixes=['B','KB','MB','GB','TB']
	suffixIndex = 0
	while size > 1024 and suffixIndex < 4:
		suffixIndex += 1 #increment the index of the suffix
		size = size/1024.0 #apply the division
	return "%.*f%s"%(precision,size,suffixes[suffixIndex])

# Clean up the data coming from Confluence

def ValConvert(val):
	val = val.replace('|','-')
	if type(val).__name__ == 'unicode':
		return val.encode('utf8')
	elif type(val).__name__ == 'str':
		return val
	else:
		return str(val)

def printDirectoryTree(outputFiles,directoryList,server,token):

	DT = open(outputFiles['directoryTree'], 'w')
	AC = open(outputFiles['attachmentCSV'], 'w')
	PC = open(outputFiles['pageCSV'], 'w')

	# Add Header line to CSV
	PC.write("|".join(["id" , "title" , "depth" , "size", "created" , "creator" , "modified" , "modifier"])+"\n")
	AC.write("|".join(["id" , "title" , "parent" , "size" , "created", "creator"])+"\n")
	DT.write("|".join(["position" , "title" , "id" , "depth" , "hr-size" , "created" , "creator" , "modified" , "modifier"])+"\n")

	itemNo = 0

	if debug == 1:
		print("DIRECTORY LIST PRE_PRINT")
		pprint.pprint(directoryList, depth=4)

	for directory in directoryList:
		indentDot = ""
		itemNo += 1;

		for x in range(directory['depth']):
			indentDot += "  ."

		if directory['size'] > 0 :
			title = ValConvert(directory['title'])

			id = directory['id']
			size = str(directory['size'])
			depth = str(directory['depth'])
			created = str(directory['created'])
			creator = str(directory['creator'])

			if directory['type'] == 'page':
				created = str(directory['created'])
				creator = str(directory['creator'])

				modified = str(directory['modified'])
				modifier = str(directory['modifier'])

				if debug == 1:
					print("DIR "+" >> ".join(directory['path']))
					print("PRINTING PAGE "+title+" FROM THE ARRAY")
					pp.pprint(directory)

				path = directory['path']
				path.append(title)

				pathStr = ValConvert(" > ".join(path))

				if debug == 1:
					print(pathStr)

				PC.write("|".join([id , pathStr , depth , size, created , creator , modified , modifier])+"\n")
				title = "\\"+pathStr
				DT.write("|".join([str(itemNo), indentDot+title , id , depth , GetHumanReadable(directory['size'],2), created , creator , modified , modifier])+"\n")
			elif directory['type'] == 'attachment':
				AC.write("|".join([id , title , directory['parent'] , size , created , creator])+"\n")
				title = "-"+title
				DT.write("|".join([str(itemNo), indentDot+title , id , depth , GetHumanReadable(directory['size'],2), created , creator ])+"\n")



# MAIN START HERE

pp = pprint.PrettyPrinter(indent=1)
jiraUsername=''
jiraPassword=''
jiraURL=''

server = xmlrpc.client.ServerProxy(jiraURL)
token = server.confluence2.login(jiraUsername, jiraPassword)
space = 'TT'

### CLEAN UP ARGUEMENT HANDLING
if len(sys.argv) > 1:
	space = sys.argv[1]

pageid = 0
if len(sys.argv) > 2:
	pageid = sys.argv[2]
else:
	spaceObj = server.confluence2.getSpace(token, space) # Get Space information
	pageid = spaceObj['homePage']

#### END CLEANUP

spaceList = []
pid = os.getpid()
outputDirectory="./"+str(space)+"-"+str(pid)
outputFilename=outputDirectory+"/"+"op-"+str(space)+"-"+str(pid)

print ("Making directory ["+outputDirectory+"]")
os.makedirs(outputDirectory[:outputFilename.rindex(os.path.sep)], exist_ok=True)

print ("Output filename prefix "+outputFilename+" created")

outputFiles = {'directoryTree': outputFilename+"-dt.csv",
		'attachmentCSV': outputFilename+"-ac.csv",
		'pageCSV': outputFilename+"-pc.csv"}

pageItem = server.confluence2.getPage(token, pageid)
parentPath = []

spaceSize = treeSize(server,token,pageItem,parentPath,0,1)
print ("total space size="+GetHumanReadable(spaceSize['size'],4))

printDirectoryTree(outputFiles,spaceList[::-1],server,token)

exit('Done!')
