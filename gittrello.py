#!/usr/bin/python
#Version 1.0 - 2015-10-12

import json
import sys
import os
import re
import inspect
import requests
import string


homePath = os.path.expanduser('~')+'/.gittrello.json'
parentDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentPath = parentDir+'/.gittrello.json'
if os.path.isfile(homePath):
    jsonFile = homePath
elif os.path.isfile(parentPath):
    jsonFile = parentPath
else:
    sys.exit("Could not find '.gittrello.json' file, see '"+parentDir+"/gittrello.example.json' for instructions")

with open(jsonFile) as data_file:
    try:
        data = json.load(data_file)
    except:
        sys.exit(jsonFile+' is not a valid JSON file')

trelloKey = data['trello']['key']
trelloBoards = data['trello']['boards']
trelloToken = data['trello']['token']
gitHubToken = data['github']['token']
gitHubTags = data['github']['tags']
skipTags = data['skiptags']

trelloLink = 1

branchname = sys.argv[1]
branchNameList = re.findall(r"[^-]+|-", branchname)[::2]

if len(branchNameList[-1]) != 8:
    trelloLink = 0

for skiptag in skipTags:
    if skiptag == branchNameList[-1]:
        tag = branchNameList.pop()
        trelloLink = 0

repoURL = sys.argv[2]
repoObj = re.match(r'(https\:\/\/github\.com\/|git\@github\.com\:)([^\/]*)\/([^.]*)',str(repoURL))
try:
    repoOwner = repoObj.group(2)
    repoName = repoObj.group(3)
except:
    sys.exit('Could not retrieve repository information, make sure you are in a git repository.')

if trelloLink == 1:
    cardLink = branchNameList.pop()

    try:
        getCardURL = "https://api.trello.com/1/cards/"+cardLink+"?fields=name,url&board=true&board_fields=name&list=true&list_fields=name&key="+trelloKey+"&token="+trelloToken
        getCard = requests.get(getCardURL).json()
    except:
        sys.exit("Unable to get card with shortlink '"+cardLink+"'")

    boardName = getCard['board']['name']
    boardID = getCard['board']['id']
    listName = getCard['list']['name']
    listID = getCard['list']['id']
    cardName = getCard['name']
    cardURL = getCard['url']


    try:
        fromList = trelloBoards[boardName]['from']
    except:
        sys.exit("The board '"+boardName+"' was not found in .gittrello.json")

    if listName != fromList:
        sys.exit("The card '"+cardName+"' is not in the '"+fromList+"' list");

    try:
        tag = trelloBoards[boardName]['tag'] 
    except:
        tag = raw_input("Enter a tag for this pull request (optional): ")

    response = ''
    while response not in ("Y","n","Q"):
        response = raw_input("Link this PR to '"+cardName+"' on the Trello '"+boardName+"' board? (Y/n/Q): ")


    if response == 'Q':
        sys.exit("Pull request aborted")
    elif response == 'n':
        trelloLink = 0
        continuePR = raw_input("Continue opening pull request? (Y/n): ")
        if continuePR == 'n':
            sys.exit("Pull request aborted")
    elif len(tag) == 0:
        tag = raw_input("Your pull request must have a 3-letter tag if you wish to link it to a Trello card (Q to abort): ")
        if len(tag) != 3 or tag == "Q":
            sys.exit('Pull request aborted')
        



prName = string.capwords(" ".join(branchNameList))
if len(tag) > 0:
    prTitle = "["+tag+"] "+prName
else:
    prTitle = prName

prTitleResponse = ''
while prTitleResponse not in ("Y","n","Q"):
    prTitleResponse = raw_input("Open a pull request with the title '"+prTitle+"' ? (Y/n/Q): ").strip()

if prTitleResponse == 'Q':
    sys.exit("Pull request aborted")
elif prTitleResponse == 'n':
    prTitle = ''
    while len(prTitle.strip()) == 0:
        prTitle = raw_input("Enter pull request title (Q to abort): ").strip()

if(prTitle == "Q"):
    sys.exit("Pull request aborted")

prHead = repoOwner+":"+branchname

prBody = ''
while len(prBody) == 0:
    prBody = raw_input("Enter description for '"+prTitle+"' (Q to abort): ").strip()

if prBody == 'Q':
    sys.exit("Pull request aborted")
elif trelloLink == 1:
    prBody = prBody+"\n\n"+cardURL


createPullRequestURL = "https://api.github.com/repos/"+repoOwner+"/"+repoName+"/pulls?access_token="+gitHubToken
payload = {
    "title": prTitle,
    "head": prHead,
    "body": prBody,
    "base": "master"
}

try:
    createPullRequest = requests.post(createPullRequestURL, json.dumps(payload)).json()
except:
    sys.exit("There was an error creating your pull request in "+repoName)

try:
    prURL = createPullRequest['_links']['html']['href']
except:
    sys.exit("Unabled to retrieve pull request url, make sure your branch has been pushed to github")

try:
    prNumber = createPullRequest['number']
except:
    sys.exit('Unable to retrieve pull request number.')

gitHubLabels = []
for label in gitHubTags[tag]['labels']:
    addLabel = raw_input("Would you like to add the '"+label+"' label to your pull request (y/n)? ")
    if addLabel.lower() == "y":
        gitHubLabels.append(label)

if len(gitHubLabels) > 0:
    addLabelsURL = "https://api.github.com/repos/"+repoOwner+"/"+repoName+"/issues/"+str(prNumber)+"/labels?access_token="+gitHubToken
    try:
        addLabels = requests.post(addLabelsURL, json.dumps(gitHubLabels))
    except:
        print "There was an error assigning labels to "+prTitle


if trelloLink == 1:
    attachPullRequestURL = "https://api.trello.com/1/cards/"+cardLink+"/attachments?key="+trelloKey+"&token="+trelloToken+"&url="+prURL
    try:
        attachPR = requests.post(attachPullRequestURL).json()
    except:
        sys.exit("Error adding attachemnt to '"+cardName+"'. Please check your '.gittrello.json' file for errors, and report this problem on 'https://github.com/JRonhovde/gittrello'.")

    if len(attachPR['url']) > 0:
        print "Pull request '"+prTitle+"' successfully created and linked to Trello card '"+cardName+"'"
    else:
        sys.exit("Unable to attach pull request '"+prTitle+" to Trello card '"+cardName+"'. Please check your '.gittrello.json' file for errors, and report this problem on 'https://github.com/JRonhovde/gittrello'.")

    try:
        getListsURL = "https://api.trello.com/1/boards/"+boardID+"/lists?fields=name&key="+trelloKey+"&token="+trelloToken
        getLists = requests.get(getListsURL).json()
    except:
        sys.exit("'"+cardName+"' not moved from '"+fromBoard+"' to '"+toBoard+"'. Please check your '.gittrello.json' file for errors, and report this problem on 'https://github.com/JRonhovde/gittrello'.")

    toListID = 0
    for thisList in getLists:
        if thisList['name'] == trelloBoards[boardName]['to']:
            toListID = thisList['id']
            break

    if toListID > 0:
        moveCardURL = "https://api.trello.com/1/cards/"+cardLink+"/idList?value="+toListID+"&key="+trelloKey+"&token="+trelloToken
        try:
            moveCard = requests.put(moveCardURL).json()
        except:
            sys.exit("Unable to move card")

    fromList = trelloBoards[boardName]['from']
    toList = trelloBoards[boardName]['to']
    if moveCard['idList'] == toListID:
        print "'"+cardName+"' moved from '"+fromList+"' to '"+toList+"'"
    else:
        print "'"+cardName+"' not moved from '"+fromList+"' to '"+toList+"'. Please check your '.gittrello.json' file for errors, and report this problem on 'https://github.com/JRonhovde/gittrello'."
