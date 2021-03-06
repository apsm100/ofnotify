import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import re
import argparse
import datetime
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

# MongoDB connection; redacted for gitHub.
# Use version 1.0 for local use. 
client = pymongo.MongoClient("mongodb+srv://hidden")
db = client.ofnotify
mycol = db["data"]
mongo_id = "listings"

version = "1.1b"
print("ofnotify v" + version + " - amrit manhas @apsm100")

# Email configuration (set to Outlook by default; ex. "hello@outlook.com").
# Input your own email and password, this script will send it from yourself.
email = ""
password = ""


class Post:
    """
    Post object that has a title and link; the post id is extracted from the url.
    """
    def __init__(self, title, link):
        """
        Initializes title and link
        """
        self.title = title
        self.link = link


"""Command Line Arguments"""
parser = argparse.ArgumentParser()
parser.add_argument("--noimage", help="no images in notification",
                    action="store_true")
parser.add_argument("--noemail", help="no email will be sent",
                    action="store_true")
parser.add_argument("--noradius", help="no image border radius",
                    action="store_true")
parser.add_argument("--sendall", help="send all zero-post listings",
                    action="store_true")
args = parser.parse_args()
arguments = ""
if args.noimage:
    arguments = arguments + "--noimage "
if args.noemail:
    arguments = arguments + "--noemail "
if args.noradius:
    arguments = arguments + "--noradius "
if args.sendall:
    arguments = arguments + "--sendall "
if arguments:
    print("arguments: " + arguments)


def main():
    """Main drives the program."""
    url = "https://omegaforums.net/forums/private-watch-sales/"
    soup = get_soup(url)
    notify(soup)


def get_db_list():
    """Gets the old id list from the DB"""
    col = mycol.find_one({'_id': mongo_id})
    old_id_list = col['idList']
    if args.sendall:
        old_id_list = [85119]
    return old_id_list


def write_db_list(id_list):
    """Writes the old id list to the DB"""
    new_values = {"$set": {"idList": id_list}}
    mycol.update_one({'_id': mongo_id}, new_values)


def notify(soup):
    """Uses Beautifulsoup to scrape zero post listings from the 
    OF sales forum, extract their IDs, compares the IDs with a stored ID list (last run), 
    notifies the user of new posts via email, and outputs the current ID list to a json."""
    # post_list = list of all zero post objects
    post_list = get_lists(soup)
    # final_post_list = final list of post objects after comparison with id list
    # new_id_list = new id list to be dumped
    final_post_list, new_id_list = compare_lists(post_list)
    if final_post_list:
        if args.sendall:
            print('\nall zero-post listings [' + str(len(final_post_list)) + '].')
        else:
            print('\nnew listings found [' + str(len(final_post_list)) + '].')
        send_notification(final_post_list, new_id_list)
        # log(new_id_list, True)
    else:
        print('\nnothing to tell you.')
        # log(new_id_list, False)
    dump_list(new_id_list)


def get_soup(url):
    """Checks if OF or network is available and returns soup."""
    try:
        page = requests.get(url, timeout=10.0)
    except Exception as inst:
        print("\nof timed out, scrape incomplete.")
        print(inst)
        exit()
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup


def get_lists(soup):
    """Scrapes the HTML for links and titles and returns 
    a list of links, a list of titles, and a list of indexes where a listing has zero posts."""
    post_list = []
    raw_posts = soup.find_all(href=True)  # Get all href elements.
    for i in raw_posts:
        if 'threads/' in i['href']:
            post = Post(i.string, i['href'])
            post_list.append(post)

    # index_list will hold the zero post indexes.
    raw_posts = soup.find_all('dl', class_="major")
    index_list = []  # List of indexes for zero post listings.
    index_count = -1  # Used for items in index_list.
    for i in raw_posts:
        item = i.find_all('dd')
        for v in item:
            index_count = index_count + 1
            if v.contents == ['0']:  # If the listing has zero posts.
                index_list.append(index_count)

    # Remove anything but 0 posts
    final_post_list = []
    for i in index_list:
        final_post_list.append(post_list[i])
    return final_post_list


def compare_lists(post_list):
    """Creates a new link and titles list of zero post listings 
    using index_list. A new ID list is created and is compared with the old ID list.
    IDs are used here as links and titles can change, but listing IDs will never change.
    Return new items in new lists."""
    old_id_list = get_db_list()
    # Create a new_id_list by using new_link_list urls.
    new_id_list = []
    final_post_list = []
    for i in post_list:
        result = re.search('\.(.*?)/', i.link)
        new_id_list.append(int(result.group(1)))
    # Compare new_id_list with old_id_list and append new listings to final_post_list.
    for i in new_id_list:
        if i not in old_id_list:
            index_val = int(new_id_list.index(i))
            final_post_list.append(post_list[index_val])
    return final_post_list, new_id_list


def send_notification(final_post_list, new_id_list):
    """Creates and sends the html notification.
    The listing photos are added if possible."""
    html_list = []
    difference = len(final_post_list)
    index_range = range(0, difference)
    ver = version
    for i in index_range:
        if i == difference:
            break
        # Variables for email.
        title = final_post_list[i].title
        link = "https://omegaforums.net/" + final_post_list[i].link
        image_link = ""
        if not args.noimage:
            image_link = get_image(link)
        # If an image is not available, or disabled, hide it and adjust the view. 
        if image_link:
            image_display = ""
            em = 0
        else:
            image_display = "display:none;"
            em = 1
        # Hide the border on the last item.     
        if i == difference - 1:
            border_display = "display:none;"
        else:
            border_display = ""
        html_list_item = create_html_list_item(link, image_link, image_display, em, title, border_display)
        html_list.append(html_list_item)
        body = '\n'.join(html_list)
    if difference > 1:  # Plurality or not.
        period = "s"
    else:
        period = ""
    html = create_html(difference, period, body, ver)
    send_email(html)


def create_html_list_item(link, image_link, image_display, em, title, border_display):
    """Creates a list item in HTML"""
    image_radius = 18
    if args.noradius:
        image_radius = 0
    html_list_item = """<div style="margin-top:0.5em;margin-bottom:0.5em;"><a href="{link}" style="text-decoration:none;">
    <img src="{image_link}" style="{image_display}object-fit:cover;width:100%;max-height:330px;border-radius:{image_radius}px;margin-top:0.5em;margin-bottom:1em;">
    <h3 style="margin-top:{em}em; margin-bottom:{em}em;color:#000000;padding-left:6px;padding-right:6px;">{title}</h3></a></div>
    <div style="{border_display}margin-bottom:2em;margin-top:2em;height:1px;width:100%;background-color:gainsboro;"></div>""".format(
        **locals())
    return html_list_item


def create_html(difference, period, body, ver):
    """Creates a final compile of all list items in HTML.
    Utilizes nbsp zwnj trick to create a hidden subtitle."""
    html = """\
    <html>
        <head></head>
            <body>
                <div style="display: none; max-height: 0px; overflow: hidden;">
                {difference} new post{period}
                </div>
                <div style="display: none; max-height: 0px; overflow: hidden;">
                &nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;
                &zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;
                &zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;
                &zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;
                &nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;
                &nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;
                &nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;
                &zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;
                &zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;
                &zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;
                &zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;
                &nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;
                &nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;
                &nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;
                &zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;
                &zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;
                &zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;
                &nbsp;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;
                &nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;
                </div>
                {body}
                <footer style="margin-top:3em;color:gainsboro;text-align:center;font-size:60%;">ofnotify v{ver}</footer>
            </body>
    </html>""".format(**locals())
    return html


def get_image(url):
    """Gets and returns the image_link at the specified url.
    There are a few methods of uploading a photo to OF, the following two
    cover the methods observed."""
    soup = get_soup(url)
    # If photo was attached via OF server.
    message_content = soup.find("div", {"class": "messageContent"})
    image = message_content.find('img', {"loading": "lazy"})
    # If photo was hyperlinked.
    if not image:
        image = message_content.find('img', {"class": "bbCodeImage LbImage"})
    # If an image was found create a title.
    if image:
        image_link = "https://omegaforums.net/" + image['src']
    else:
        image_link = ""
    return image_link


def send_email(html):
    """Sends a HTML email to the specified username and email
    using the email and password specified."""
    # If email is disabled.
    if args.noemail:
        output_html(html)
        return
    # If email is not configured, output to output.html.
    if email == "" or password == "":
        print("\nemail not configured.")
        output_html(html)
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
        print('\nnotification sent.')


def output_html(html):
    """Outputs HTML to output.html"""
    f = open("output.html", "w")
    f.write(html)
    f.close()
    print("\noutput sent to output.html.")


def dump_list(new_id_list):
    """Dumps the new_id_list to the DB.
    for the next run. Ignore if new_id_list is null."""
    # Dump new list created.
    # if new_id_list is not None and new_id_list != [85119]:
    if new_id_list:
        write_db_list(new_id_list)


def log(id_list, is_new):
    """Logs the id list"""
    x = datetime.datetime.now()
    f = open("log.txt", "a")
    date_time = x.strftime("%m/%d/%Y, %H:%M:%S")
    f.write(date_time + " - " + str(id_list) + " new_items = " + str(is_new) + "\n")


if __name__ == "__main__":
    main()
