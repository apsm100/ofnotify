import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import re
version = "1.3-6"
print("ofnotify v" + version + "\nAmrit Manhas")

"""ofnotify
amrit manhas
Uses Beautifulsoup to scrape 0 post count listings from the 
OF sales forum and notifies the user of new posts via email.
"""
# Email config (set to outlook\hotmail)
# Input your own email and password, this script will send it from yourself.
email = ""
password = ""

#Main 
#Drives the program.
def main():
    soup = getSoup()
    title_list, link_list, index_list = getLists(soup)
    final_title, final_link, new_id_list = compareLists(title_list, link_list, index_list)

    if final_title:
        print('\nNew items found:')
        print(final_link)
        print(final_title)
        sendNotification(final_title, final_link, new_id_list)
    else:
        print('\nNothing to tell you.')
    
    dumpList(new_id_list)

def getSoup():
    try:
        page = requests.get("https://omegaforums.net/forums/private-watch-sales/", timeout=10.0)
    except:
        print("\nOF timed out.")
        exit()
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

def getLists(soup):
    # Find listing titles and links.
    title_list = []
    link_list = []
    links = soup.find_all(href=True)  # Get all href elements.
    for i in links:
        if 'threads/' in i['href']:
            title_list.append(i['href'])
            link_list.append(i.string)

    # post_list finds just the post numbers, below will find the zero post indexes.
    post_list = soup.find_all('dl', class_="major")
    index_list = []  # List of indexes for 0 post items.
    index_count = -1  # Used for items in index_list.
    for i in post_list:
        item = i.find_all('dd')
        for v in item:
            index_count = index_count + 1
            if v.contents == ['0']: # Check contents for 0
                index_list.append(index_count)
    return title_list, link_list, index_list

def compareLists(title_list, link_list, index_list):
    # Check for saved files and load them into old title, old link, and old id variables.
    try:
        with open('id.json') as f:
            old_id_list = json.load(f)
    except:
        old_id_list = []

    #   Create index comparison lists.
    new_title_list = []
    new_link_list = []

    for i in index_list:
        new_title_list.append(title_list[i])
        new_link_list.append(link_list[i])

    # Create new ID list by using new title list urls.
    new_id_list = []
    new_index_list = []
    for i in new_title_list:
        result = re.search('\.(.*?)/', i)
        new_id_list.append(result.group(1))

    # Compare new id list with old id list and append new item indices to new index list.
    for i in new_id_list:
        if i not in old_id_list:
            new_index_list.append(new_id_list.index(i))

    final_title = []
    final_link = []

    # Use the new index list indices to create final title and link lists for notification.
    for i in new_index_list:
        final_title.append(new_title_list[int(i)])
        final_link.append(new_link_list[int(i)])
    return final_title, final_link, new_id_list

def sendNotification(final_title, final_link, new_id_list):
    # the notification is created and sent.
    html_list = []
    difference = len(final_title)
    index_range = range(0, difference)
    versionnum = version

    for i in index_range:
        if i == difference:
            break

        # Variables for email.
        nam = final_link[i]
        url = "https://omegaforums.net/" + final_title[i]

        imageLink, display, em = getImage(url)

        #styling the email
        if i == 0:
            em2 = 0
        else:
            em2 = 1

        if i == difference - 1:
            border = "display:none;"
        else:
            border = ""
        
        html_list_item = """<div style="margin-top:0.5em;margin-bottom:0.5em;"><a href="{url}" style="text-decoration:none;"><img src="{imageLink}" style="{display}object-fit:cover;width:100%;max-height:330px;border-radius:18px;margin-top:0.5em;margin-bottom:1em;"><h3 style="margin-top:{em}em; margin-bottom:{em}em;color:#000000;padding-left:6px;padding-right:6px;">{nam}</h3></a></div><div style="{border}margin-bottom:2em;margin-top:2em;height:1px;width:100%;background-color:gainsboro;"></div>""".format(**locals())
        html_list.append(html_list_item)
        
        body = '\n'.join(html_list)

    if difference > 1:  # Plurality or not.
        period = "s"
    else:
        period = ""

    html = """\
    <html>
        <head></head>
            <body>
                <div style="display: none; max-height: 0px; overflow: hidden;">
                {difference} new post{period}
                </div>
                <div style="display: none; max-height: 0px; overflow: hidden;">
                &nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;
                </div>
                {body}
                <footer style="margin-top:3em;color:gainsboro;text-align:center;font-size:60%;">ofnotify v{versionnum}</footer>
            </body>
    </html>""".format(**locals())
    
    sendEmail(html)

def getImage(url):
    # Scrape first image of the listing.
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # If photo was attached via OF server.
    messageContent = soup.find("div", {"class": "messageContent"})
    image = messageContent.find('img', {"loading": "lazy"})
    
    # If photo was hyperlinked.
    if not image:
        image = messageContent.find('img', {"class": "bbCodeImage LbImage"})

    # If photo cannot be scraped then hide img in html and reorganize to fit.
    if image:
        imageLink = "https://omegaforums.net/" + image['src']
        display = ""
        em = 0
    else:
        imageLink = ""
        display = "display:none;"
        em = 1
    return imageLink, display, em

def sendEmail(html):
    # If email is not configured, output to output.html.
    if email == "" or password == "":
        print("\nEmail not configured.")
        f = open("output.html", "w")
        f.write(html)
        f.close()
        print("Output sent to output.html.")
    else:
        # Send the message via local SMTP server.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Notification"
        msg['From'] = email
        msg['To'] = email

        part1 = MIMEText(html, 'html')

        msg.attach(part1)
        mail = smtplib.SMTP('smtp-mail.outlook.com', 587)

        mail.ehlo()

        mail.starttls()

        mail.login(email, password)
        mail.sendmail(email, email, msg.as_string())
        mail.quit()

        print('\nNotification sent.')

def dumpList(new_id_list):
    # Dump new list created.
    if new_id_list:
        with open('id.json', 'w') as f:
            json.dump(new_id_list, f)

if __name__ == "__main__":
    main()
