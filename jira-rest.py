# http://jira.readthedocs.io/en/latest/

import os, sys, string, re, pprint, datetime
from jira import JIRA

jiraUsername=''
jiraPassword=''
jiraURL=''


jira = JIRA(jiraURL, basic_auth=(jiraUsername, jiraPassword))

projects = jira.projects()

for project in projects:
	jqlStr = "project = \""+project.name+"\""
	try:
		issues = jira.search_issues(jqlStr)
	except:
		print("|".join([project.key,project.name,"ISSUE HERE"]))
		continue

	print("|".join([project.key,project.name,str(issues.total)]))
	#print(project.key+"="+project.name+" No.:"+str(issues.total))

#pprint.pprint(projects)

#issue = jira.issue('TT-1')
#print(issue.fields.project.key)
#print(issue.fields.issuetype.name)
#print(issue.fields.reporter.displayName)
