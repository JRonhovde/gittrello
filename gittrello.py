#!/usr/bin/python
#Version 1.0 - 2015-10-12

import json
import sys
import os
import re
import inspect
import requests
import string
import urllib


branchname = sys.argv[1]
repoURL = sys.argv[2]
userAddLabels = sys.argv[3]
if userAddLabels == '0':
    userAddLabels = ''
userRemoveLabels = sys.argv[4]
if userRemoveLabels == '0':
    userRemoveLabels = ''

issueURL = ''
labelMessage = []
boardName = ''
boardLabels = []
trelloLink = 1

# get home path and parent path
# homepath is the user's home directory
# parentpath is the parent directory of gittrello.py
# homepath is tested before parentpath

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

# data extracted from .gittrello.json
trelloKey = data['trello']['key']
trelloBoards = data['trello']['boards']
trelloToken = data['trello']['token']
gitHubToken = data['github']['token']
gitHubTags = data['github']['tags']
skipTags = data['skiptags']

branchNameList = re.findall(r"[^-]+|-", branchname)[::2]

# Trello shortlinks are 8 characters long
if len(branchNameList[-1]) != 8:
    trelloLink = 0

# don't ask to link if the last part of the branch name is
# on the skiptag list
for skiptag in skipTags:
    if skiptag == branchNameList[-1]:
        tag = branchNameList.pop()
        trelloLink = 0

# match repo owner and repo name
repoObj = re.match(r'(https\:\/\/github\.com\/|git\@github\.com\:)([^\/]*)\/([^.]*)',str(repoURL))
try:
    repoOwner = repoObj.group(2)
    repoName = repoObj.group(3)
    githubBase = "https://api.github.com/repos/"+repoOwner+"/"+repoName
except:
    sys.exit('Could not retrieve repository information, make sure you are in a git repository.')

#{ # User labels(add labels to existing PR 
if len(userRemoveLabels) > 0:
    verifiedRemoved = []
    getPullRequestURL = githubBase+"/pulls?head="+repoOwner+":"+branchname+"&access_token="+gitHubToken
    try:
         prTitle = requests.get(getPullRequestURL).json()[0]['title']
         issueURL = requests.get(getPullRequestURL).json()[0]['_links']['issue']['href']
    except:
        sys.exit('Invalid branch. Check that your branch is spelled correctly. Also check that your branch is associated with a pull request on GitHub')

    userRemoveLabelsList = userRemoveLabels.split(', ')

    for userLabel in userRemoveLabelsList:
        checkLabelURL = githubBase+"/labels/"+urllib.quote(userLabel, safe='')+"?access_token="+gitHubToken
        try:
            # check if the label exists for this repository
            checkLabelResp = requests.get(checkLabelURL).json()['name']
        except:
            print "Unable to find '"+userLabel+"' in '"+repoName+"'"

        try:
            # remove label from pull request (uses Issues API)
            userRemoveLabelsURL = issueURL+"/labels/"+urllib.quote(userLabel, safe='')+"?access_token="+gitHubToken
            try:
                userRemoveLabelsResp = requests.delete(userRemoveLabelsURL).json()
                verifiedRemoved.append(userLabel)

            except:
                print "Unable to remove "+userLabel+" from '"+prTitle+"'"
        except:
             print "Label "+userLabel+" not found"

    if len(verifiedRemoved) > 1:
        labelMessage.append("Labels '"+"', '".join(verifiedRemoved)+"' removed from '"+prTitle+"'")
    else:
        labelMessage.append("'"+', '.join(verifiedRemoved)+"' removed from '"+prTitle+"'")


#}
         
#{ # User labels(add labels to existing PR 
if len(userAddLabels) > 0:

    userAddLabelsList = userAddLabels.split(', ')
    githubBase = "https://api.github.com/repos/"+repoOwner+"/"+repoName

    verifiedLabels = []
    for userLabel in userAddLabelsList:
        checkLabelURL = githubBase+"/labels/"+urllib.quote(userLabel, safe='')+"?access_token="+gitHubToken
        try:
            checkLabelResp = requests.get(checkLabelURL).json()
        except:
            sys.exit("Unable to find label in "+repoName)

        if checkLabelResp['name'] == userLabel:
            verifiedLabels.append(userLabel)

    if len(verifiedLabels) > 0:
        if len(issueURL) == 0:
            getPullRequestURL = githubBase+"/pulls?head="+repoOwner+":"+branchname+"&access_token="+gitHubToken
            try:
                 prTitle = requests.get(getPullRequestURL).json()[0]['title']
                 issueURL = requests.get(getPullRequestURL).json()[0]['_links']['issue']['href']
            except:
                sys.exit('Invalid branch. Check that your branch is spelled correctly. Also check that your branch is associated with a pull request on GitHub')

        userAddLabelsURL = issueURL+"/labels?access_token="+gitHubToken
        try:
            userAddLabelsResp = requests.post(userAddLabelsURL, json.dumps(verifiedLabels)).json()
            labelMessage.append("Labels '"+"', '".join(verifiedLabels)+"' added to '"+prTitle+"'")
        except:
            print ("Unable to add label '"+userLabel+"' to " +prTitle)


#}

# exit with feedback message after adding/removing labels
if len(labelMessage) > 0:
    labelMessage = "\n".join(labelMessage)
    sys.exit(labelMessage)


if trelloLink == 1:
    # trello shortlink should be the last element in the branchNameList
    cardLink = branchNameList.pop()

    try:
        getCardURL = "https://api.trello.com/1/cards/"+cardLink+"?fields=name,url,labels&board=true&board_fields=name&list=true&list_fields=name&key="+trelloKey+"&token="+trelloToken
        getCard = requests.get(getCardURL).json()
    except:
        sys.exit("Unable to get card with shortlink '"+cardLink+"'")

    boardName = getCard['board']['name']
    boardID = getCard['board']['id']
    listName = getCard['list']['name']
    listID = getCard['list']['id']
    cardName = re.sub(r"^\(\d\) ", "", getCard['name']) # remove Trello points from card name
    cardURL = getCard['url']
    cardLabels = getCard['labels']

    try:
        # get label associations from .gitrello.json
        boardLabels = trelloBoards[boardName]['labels']
    except:
        pass
    
    try:
        # this is the list the card should be in
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
        



# join branch name back into a string and
# capitalize the first letter of each word
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
    # insert hyperlink to Trello card using markdown syntax
    prBody = prBody+"\n\n["+cardName+"]("+cardURL+")"


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
    sys.exit("Unable to retrieve pull request url, make sure your branch has been pushed to github")

try:
    prNumber = createPullRequest['number']
except:
    sys.exit('Unable to retrieve pull request number.')

allLabels = []

try:
    # add labels from .gittrello.json
    allLabels += gitHubTags[tag]['labels']
except:
    pass

try:
    # add labels from Trello card that are associated with
    # GitHub labels in .gittrello.json
    allLabels += [boardLabels[label['name']] for label in cardLabels if label['name'] in boardLabels]
except Exception as e:
    print e
    pass


def label_prompt(label):
    labelPrompt = "Would you like to add the '"+label+"' label to your pull request (y/n)? "

    addLabel = raw_input(labelPrompt)
    if addLabel.lower() == "y":
        return label

try:
    # confirm each label
    allLabels = [label_prompt(label) for label in allLabels]
except:
    pass


if len(allLabels) > 0:
    addLabelsURL = "https://api.github.com/repos/"+repoOwner+"/"+repoName+"/issues/"+str(prNumber)+"/labels?access_token="+gitHubToken
    try:
        addLabels = requests.post(addLabelsURL, json.dumps(allLabels))
    except:
        print "There was an error assigning labels to "+prTitle


if trelloLink == 1:
    attachPullRequestURL = "https://api.trello.com/1/cards/"+cardLink+"/attachments?key="+trelloKey+"&token="+trelloToken+"&url="+prURL
    try:
        url = requests.post(attachPullRequestURL).json()['url']
    except:
        sys.exit("Error adding attachemnt to '"+cardName+"'. Please check your '.gittrello.json' file for errors, and report this problem on 'https://github.com/JRonhovde/gittrello'.")

    if len(url) > 0:
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
