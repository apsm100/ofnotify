import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import re
version = "1.3-8"
print("ofnotify v" + version + "\nAmrit Manhas")

# Email configuration (set to Outlook by default).
# Input your own email and password, this script will send it from yourself.
email = ""
password = ""

def main():
    """Main drives the program.
    
    Uses Beautifulsoup to scrape zero post listings from the 
    OF sales forum, extract their IDs, compares the IDs with a stored ID list (last run), 
    notifies the user of new posts via email, and outputs the current ID list to a json. 
    """
    soup = getSoup()
    # link_list - list of listing links.
    # title_list - list of listing titles.
    # index_list - list of indexes where the listing post count is zero.
    link_list, title_list, index_list = getLists(soup)
    #final_link_list - list of listing links after comparison.
    #final_title_list - list of listing titles after comparison.
    #new_id_list - list of listing IDs derived from the final_link_list. 
    final_link_list, final_title_list, new_id_list = compareLists(link_list, title_list, index_list)
    if final_link_list:
        print('\nNew items found:')
        print(final_title_list)
        print(final_link_list)
        sendNotification(final_link_list, final_title_list, new_id_list)
    else:
        print('\nNothing to tell you.')
    dumpList(new_id_list)

def getSoup():
    """Checks if OF is available and returns soup."""
    try:
        page = requests.get("https://omegaforums.net/forums/private-watch-sales/", timeout=10.0)
    except:
        print("\nOF timed out.")
        exit()
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

def getLists(soup):
    """Scrapes the html for links and titles and returns 
    a list of links, a list of titles, and a list of indexes where a listing has zero posts."""
    link_list = []
    title_list = []
    titles = soup.find_all(href=True)  # Get all href elements.
    for i in titles:
        if 'threads/' in i['href']:
            link_list.append(i['href'])
            title_list.append(i.string)
    # post_list finds just listing post counts, index_list will hold the zero post indexes.
    post_list = soup.find_all('dl', class_="major")
    index_list = []  # List of indexes for zero post listings.
    index_count = -1  # Used for items in index_list.
    for i in post_list:
        item = i.find_all('dd')
        for v in item:
            index_count = index_count + 1
            if v.contents == ['0']: # If the listing has zero posts.
                index_list.append(index_count)
    return link_list, title_list, index_list

def compareLists(link_list, title_list, index_list):
    """Creates a new link and titles list of zero post listings 
    using index_list. A new ID list is created and is compared with the old ID list.
    IDs are used here as links and titles can change, but listing IDs will never change.
    Return new items in new lists."""
    # Check for saved id.json and load for comparison. 
    try:
        with open('id.json') as f:
            old_id_list = json.load(f)
    except:
        old_id_list = ["85119"] # This ID is ignored; pinned post ID.
    new_link_list = []
    new_title_list = []
    # Use index_list to create zero-post only lists.
    for i in index_list:
        new_link_list.append(link_list[i])
        new_title_list.append(title_list[i])
    # Create a new_id_list by using new_link_list urls.
    new_id_list = []
    new_index_list = []
    for i in new_link_list:
        result = re.search('\.(.*?)/', i)
        new_id_list.append(result.group(1))
    # Compare new_id_list with old_id_list and append new listing indexes to new_index_list.
    for i in new_id_list:
        if i not in old_id_list:
            new_index_list.append(new_id_list.index(i))
    final_link_list = []
    final_title_list = []
    # Use new_index_list indexes to create final_link_list and final_title_list.
    for i in new_index_list:
        final_link_list.append(new_link_list[int(i)])
        final_title_list.append(new_title_list[int(i)])
    return final_link_list, final_title_list, new_id_list

def sendNotification(final_link_list, final_title_list, new_id_list):
    """Creates and sends the html notification.
    The listing photos are added if possible."""
    html_list = []
    difference = len(final_link_list)
    index_range = range(0, difference)
    ver = version
    for i in index_range:
        if i == difference:
            break
        # Variables for email.
        title = final_title_list[i]
        url = "https://omegaforums.net/" + final_link_list[i]

        image_link = getImage(url)
        # If an image is not available, hide it and adjust the view. 
        if image_link:
            display = ""
            em = 0
        else:
            display = "display:none;"
            em = 1
        # The first item in the list has no margin-top.
        if i == 0:
            em2 = 0
        else:
            em2 = 1
        # Hide the border on the last item.     
        if i == difference - 1:
            border = "display:none;"
        else:
            border = ""
        html_list_item = """<div style="margin-top:0.5em;margin-bottom:0.5em;"><a href="{url}" style="text-decoration:none;">
        <img src="{image_link}" style="{display}object-fit:cover;width:100%;max-height:330px;border-radius:18px;margin-top:0.5em;margin-bottom:1em;">
        <h3 style="margin-top:{em}em; margin-bottom:{em}em;color:#000000;padding-left:6px;padding-right:6px;">{title}</h3></a></div>
        <div style="{border}margin-bottom:2em;margin-top:2em;height:1px;width:100%;background-color:gainsboro;"></div>""".format(**locals())
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
                <footer style="margin-top:3em;color:gainsboro;text-align:center;font-size:60%;">ofnotify v{ver}</footer>
            </body>
    </html>""".format(**locals())
    sendEmail(html)

def getImage(url):
    """Gets and returns the imagetitle at the specified url.
    There are a few methods of uploading a photo to OF, the following three
    cover the methods observed."""
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    # If photo was attached via OF server.
    messageContent = soup.find("div", {"class": "messageContent"})
    image = messageContent.find('img', {"loading": "lazy"})
    # If photo was hypertitleed.
    if not image:
        image = messageContent.find('img', {"class": "bbCodeImage LbImage"})
    # If an image was found create a title.
    if image:
        image_link = "https://omegaforums.net/" + image['src']
    else:
        image_link = ""
    return image_link

def sendEmail(html):
    """Sends a HTML email to the specified username and email
    using the email and password specified."""
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
    """Dumps the new_id_list to a json file
    for the next run. Ignore if new_id_list is null."""
    # Dump new list created.
    if new_id_list:
        with open('id.json', 'w') as f:
            json.dump(new_id_list, f)

if __name__ == "__main__":
    main()
