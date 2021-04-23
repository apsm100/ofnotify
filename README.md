# ofnotify
ofnotify notifies you of new private sales listing posts from Omega Forums. 

* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [Contents](#content)

## General Info
### The Problem
Omega Forums has a private sales forum which is moderated; sellers can 'bump' their sales listing once per day forever, 
or until their watch sells. As a result, the top-most listing is not always the newest. New sales postings can take a few hours to
be approved by the moderators, hence new listings can sometimes fall near the middle or bottom of the sales list. 

### The Solution
This python script ignores 'bumped' sales listings and only updates the user with the newly approved sales listings. It does not 
matter when the new listings were originally posted for moderation (the dates are ignored).

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
 Project folder:
├── ofnotify.py                # Main script
└── README.md                  # Read Me
