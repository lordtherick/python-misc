# http://jira.readthedocs.io/en/latest/

import os, sys, string, re, pprint, getopt
from jira import JIRA

debugFlag=False
jiraUsername=None
jiraPassword=None
jiraURL=None

appName=sys.argv[0]

### Process the arguements - move to library file

try:
	opts, args = getopt.getopt(sys.argv[1:],"hU:u:p:",["URL","username=","password="])
	for opt, arg in opts:
		if opt in ('-h',"--help"):
			print(appName+" -U <URL> -u <username> -p <password>")
			sys.exit()
		elif opt in ("-U", "--URL"):
			if debugFlag == True: print("Setting jiraURL")
			jiraURL = arg
		elif opt in ("-u", "--username"):
			if debugFlag == True: print("Setting jiraUsername")
			jiraUsername = arg
		elif opt in ("-p", "--password"):
			if debugFlag == True: print("Setting jiraPassword")
			jiraPassword = arg
except getopt.GetoptError:
	print(appName+" -U <URL> -u <username> -p <password>")
	sys.exit(2)


## Exit if we dont have the details we want.
if jiraURL == None or jiraUsername == None or jiraPassword == None:
	print("Missing credential information")
	print(":".join([jiraURL,jiraUsername,jiraPassword]))
	print(appName+" -U <URL> -u <username> -p <password>")
	sys.exit()

jira = JIRA(jiraURL, basic_auth=(jiraUsername, jiraPassword))

jqlStr = "project = \"TA\" AND resolution = Unresolved"

try:
	issues = jira.search_issues(jqlStr)
except:
	print("Error executing the jqlStr ["+jqlStr+"]")

for issueSummary in issues:
	issue=jira.issue(issueSummary.id)
	print(issue.fields.assignee)
