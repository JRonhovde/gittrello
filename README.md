# gittrello
Link GitHub pull requests with Trello cards

## Setup    
- Clone this repository:    
`git clone https://github.com/JRonhovde/gittrello.git`    

- Copy `gittrello.example.json` to `.gittrello.json`:    
`cp gittrello.example.json .gittrello.json`    

- Generate a Trello access token. This will allow GitTrello to access and modify your Trello cards. 
Follow this [link](https://trello.com/1/authorize?key=0d8f099586bb1ba35aeb524fd4bd0032&scope=read%2Cwrite&name=GitTrello&expiration=never&response_type=token)
 and insert the token in place of `<personal trello token>` in your .gittrello.json file.    
 
- Generate a GitHub personal access token. Follow [these steps](https://help.github.com/articles/creating-an-access-token-for-command-line-use/)
, making sure the token has 'repo' permissions. Then copy the token and insert it in place of 
`<github access token with 'repo' permissions>`.    

- Go through the rest of the .gittrello.json file and replace what you need for your specific board/list/label set up.

- Source the gittrello.sh script in your .bash_profile(or equivalent). There are several ways to do this but this is the simplest:    
`source ~/gittrello/gittrello.sh`

- Use the `gittrello` command while on a branch you want to link. The branch must follow a specific naming convention
to link with a Trello card. `pull-request-name-<8 character Trello card shortlink>`. Shortlinks for Trello cards can be found
 in the URL when you have a card selected. Take this screenshot for example.    
 
![trello-shortlink](https://cloud.githubusercontent.com/assets/7527424/11251852/c6ecb452-8df8-11e5-98ad-19f47b5829fa.png)

  The shortlink for this card would be '7AxuVasW'. The related git branch would be named 'test-card-7AxuVasW'.
