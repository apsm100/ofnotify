# ofnotify
ofnotify notifies you of new private sales listing posts from Omega Forums. 

* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [Contents](#content)

## General Info
### The Problem
Omega Forums uses a forum moderated private sales system where sellers can 'bump' their sales listing once per day forever.
The top-most listing is not the newest as a result, and because moderation can take hours to days, new listings can sometimes
fall near the bottom of the sales list. 

### The Solution
This python script ignores 'bumped' sales posts and only updates the user with the newly approved sales posts. It does not 
matter when the new listings were created (the dates are ignored).

###### Screenshot of a notification from the Gmail app.
![alt text](https://i.imgur.com/6ZE6z89.jpg)

## Technologies
Technologies used for this project:
* Python
* BeautifulSoup
* JSON

## Setup
Modify the email and password variables to enable notifications by email. If this is left null the output will be sent to output.html.
This script will work the best if run at a 1-10 minute interval.
Windows task scheduler can be used to run a .bat which runs the python script.

## Content
Content of the project folder:

```
 Top level of project folder:
├── ofnotify.py                # Main Python script
├── id.json                    # ID json
└── README.md                  # Read Me
