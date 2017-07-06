# http://jira.readthedocs.io/en/latest/

import os, sys, string, re, pprint, getopt
from jira import JIRA

global debugFlag
debugFlag = False

# issueCYBGSummary
# Turn CustomFields into a dict.

def _issueCYBGInfo (issue):

	# 16400 = Staff Role
	# 13702 = Email Address
	# 13701 = fullName
	# 18001 - T&C statement

	issueSummary = {
		'id': str(issue.id),
		'staffRole': str(issue.fields.customfield_16400),
		'emailAddr': str(issue.fields.customfield_13702),
		'fullName': str(issue.fields.customfield_13701),
		'reporter': str(issue.fields.reporter.name),
		'assignee': str(issue.fields.assignee),
		'status': str(issue.fields.status),
		'summary': str(issue.fields.summary),
		'description': str(issue.fields.description),
		'termsNConfitions': str(issue.fields.customfield_18001)}

	if debugFlag == True:
		for attr in issueSummary: print(attr+"="+issueSummary[attr])

	# Keeping RAW DUMP incase I need it.
	# for field_name in issue.raw['fields']:
	#	print("Field:"+str(field_name)+"Value:"+str(issue.raw['fields'][field_name]))

	return issueSummary

# _getTransitionId(jira,issue,transition)
# Wrapper for find_transitionid_by_name

def _getTransitionId(jira,issue,transition):
	return jira.find_transitionid_by_name(issue,transition),

def _createUser(jira,issue,issueSummary):
	# In here we are going to
	# Detect if the user already exists - close and open a new Ticket
	# Basic checks around the quality of the data - emailAddr, username etc.
	# We dont have to action the item here - just if it is a basic one we can.
	# Audit log is provided through JIRA - must ensure comments are created.

	print('HERE')
	return True

def _dummyFunc(jira,issue,issueSummary):
	# This is used as a dummy function for code to call.
	return True

def processOpenTicket(jira,issue,issueSummary):
	print("Place Holder - Open Ticket "+str(issue)+"="+issueSummary['id'])

	transitionAction = {
		'Full Time Staff': {'transition': 'Setup Access',
							'comment': "Auto Transiton by script\nDetected Full Time Staff Member\nSetting up User",
							'action': _createUser},
		'Contractor / Third Party': {'transition': 'T&Cs Required',
							'comment': "Auto Transiton by script\nDetected Contractor\nAssigning back to report to complete",
							'action': _dummyFunc}
	}

	if debugFlag == True: print("Will attempt to Tranisiton "+str(issue)+" to "+transitionAction[issueSummary['staffRole']]['transition'])

	tranisitonSelected=transitionAction[issueSummary['staffRole']]['transition']
	transitionComment=transitionAction[issueSummary['staffRole']]['comment']
	if 'action' in transitionAction[issueSummary['staffRole']].keys():
		transitionAction[issueSummary['staffRole']]['action'](jira,issue,issueSummary)

	jira.transition_issue(issue,tranisitonSelected,comment=transitionComment)
	jira.assign_issue(issue,issueSummary['reporter'])

	# IF CONTRACTOR - TRANSITION TO T&C.

def processAttachTnC(jira,issueSummary):
	print("Place Holder - Attach TnC")

def processJiraOnboarding(jira,issueSummary):
	print("Place Holder - Jira Onboarding")
	# Load all the information you need from the Ticket
	# Create the user
	# Transition the issue
	# Create notice and assign if cannot progress


## Generic Issue processing
def issueProcessing(jira,issue):
	key=str(issue.key)
	issueSummary = _issueCYBGInfo(issue)

	status=str(issueSummary['status'])

	if not issueSummary['summary'] == 'Test 2':
		return True

	if status == "Open": processOpenTicket(jira,issue,issueSummary)
	elif status == "Attach T&Cs": processAttachTnC(jira,issueSummary)
	elif status == "Jira Onboarding": processJiraOnboarding(jira,issueSummary)
	else:
		print('Bad Status')
#		print("Issue "+"|".join([key,status,assignee]))

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

# Retrieves a list of fields on the instance and creates a custom_field map to use as a reference.
def createJiraNameMap(jira):
	allfields=jira.fields()
	global nameMap
	nameMap = {field['name']:field['id'] for field in allfields}

	if debugFlag == True:
		for attr in nameMap: print(attr+"="+nameMap[attr])

def main():

	jiraUsername=None
	jiraPassword=None
	jiraURL=None

	appName=sys.argv[0]

	global debugFlag
	debugFlag = False

	### Process the arguements - move to library file

	try:
		opts, args = getopt.getopt(sys.argv[1:],"hdU:u:p:",["URL","username=","password="])
		#if opts['-d']: debugFlag = True

		# Turn on debugging first - so we see what is set.
		for opt, arg in opts:
			if opt in ('-d', '--debug'):
				debugFlag = True
				print("Turning Debugging On")

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

	# Custom ID fields




#	jqlStr = "project = \"TA\" AND resolution = Unresolved"
	jqlStr = "project = \"TA\" AND TYPE = \"UA - Jira Add User\" AND resolution = Unresolved"

	try:
		issues = jira.search_issues(jqlStr)
		processIssues(jira,issues)
	except Exception as ex:
		print("Error executing the jqlStr ["+jqlStr+"] - "+ex)



main()
