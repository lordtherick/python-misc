# http://jira.readthedocs.io/en/latest/

import os, sys, string, re, pprint, getopt
from jira import JIRA

def processOpenTicket(jira,issue):
	print("Place Holder - Open Ticket")

def processAttachTnC(jira,issue):
	print("Place Holder - Attach TnC")

def processProjectApproval(jira,issue):
	print("Place Holder - Project Approval")

def processInProgress(jira,issue):
	print("Place Holder - In Progress")

def processProxyRequired(jira,issue):
	print("Place Holder - Proxy Required")


## Generic Issue processing
def issueProcessing(jira,issue):
	key=str(issue.key)
	status=str(issue.fields.status)

    if status == "Open": processOpenTicket(jira,issue)
	elif status == "Attach T&Cs": processAttachTnC(jira,issue)
	elif status == "Project Approval": processAttachTnC(jira,issue)
	elif status == "In Progress": processAttachTnC(jira,issue)
	elif status == "Proxy Required": processAttachTnC(jira,issue)
	else :
		print("Issue "+"|".join([key,status,assignee]))

#	assignee=str(issue.fields.assignee)





# Wrapper for issue Processing - move to a Type based model.
def processIssues(jira,issues):
	for issueSummary in issues:
		issue=jira.issue(issueSummary.id)

# Work on this at a later date - will be more dynamic
#		status=str(issue.fields.status)
#		status=status.replace(" ","_")
#		status=status.replace("&","and")
#		status=status.lower()
#		print("STATUS"+status)

		issueProcessing(jira,issue)

	return True


def main():

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

#	jqlStr = "project = \"TA\" AND resolution = Unresolved"
	jqlStr = "project = \"TA\" AND TYPE = \"PA - Jira Add/Edit Project User\" AND resolution = Unresolved"

	try:
		issues = jira.search_issues(jqlStr)
		processIssues(jira,issues)
	except Exception as ex:
		print("Error executing the jqlStr ["+jqlStr+"] - "+ex)



main()
