import argparse
import time
import json
import csv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import bs4
from bs4 import BeautifulSoup as bs
from datetime import datetime
import yaml
import re
import numpy as np
import sys

# with open('facebook_credentials.txt') as _file:
#     email = _file.readline().split('"')[1]
#     password = _file.readline().split('"')[1]

#done
def _extract_postDate(item):
    date = None
    postDate = item.find(class_="_5ptz")
    if postDate:
        post_data_utime = postDate["data-utime"]
        date = datetime.utcfromtimestamp(int(post_data_utime)).strftime("%d-%m-%Y")
    return date

#done
def _extract_post_text(item):
    actualPost = item.find(attrs={"data-testid": "post_message"})
    text = ""
    if actualPost:
        paragraphs = actualPost.find_all('p')
        text = ""
        for paragraph in paragraphs:
            all_elems = []
            stack = []
            contents = paragraph.contents
            for content in contents:
                if type(content) == bs4.element.NavigableString:
                    all_elems.append(content.strip())
                elif type(content) == bs4.element.Tag:
                    stack.append(content)
                    while len(stack):
                        st_elem = stack.pop(0)
                        if type(st_elem) == bs4.element.Tag\
                           and len(st_elem.contents):
                            for item in list(map(lambda x : str(x).strip(), content.contents)):
                                if item not in all_elems:
                                    all_elems.append(item) 
                            stack += st_elem.contents

            content_str = "\n".join(list(map(str, all_elems)))
            content_str = re.sub(r"<.*>", "\n", content_str).strip()
            text += content_str.strip() + "\n"
    #print(text)
    while text.find("\n\n") != -1:
        text = text.replace("\n\n", "\n")
    return text

#done
def _extract_link(item):
    postLink = item.find(class_="_6ks")
    link = None
    if postLink:
        if postLink.a:
            link = postLink.a['href']
    return link
    
def _extract_author(item):
    author_tag = item.find('span', class_="fwb fcg")
    author_name = None
    if author_tag:
        author_name = author_tag.a.text
    return author_name

#done
"""
link to a specific long post
"""
def _extract_post_id(item):
    postId = item.find(class_="_5pcq")
    post_id = None
    if postId:
        post_id = f"https://www.facebook.com{postId['href']}"
    return post_id

#done
#_2a2q _65sr
def _extract_image(item):
    postPic = item.find(class_="scaledImageFitWidth img")
    image = None
    if postPic:
        image = postPic['src']
    else:
        postPic = item.find("a", class_="_5dec _xcx")
        if postPic:
            image =  postPic['data-ploi']
    return image

#fixed
"""
including: num_comments, num_shares, num_view(for videos)
"""
def _extract_shares(item):
    postShare = item.find(class_="_4vn1")
    shares = dict()
    if postShare:
        for postShare_child in postShare.children:
            shareNames = postShare_child.string.split()
            name = shareNames[-1].lower()
            num = "".join(shareNames[:-1])

            # fix weird ',' happening in some reaction values
            num = num.replace(',', '.')
            realNum = 0
            if 'K' in num:
                realNum = float(num[:-1]) * 1000
            else:
                realNum = float(num)

            shares[name] = int(realNum)
    return shares

#good
def _extract_comments(item):
    postComments = item.find_all(attrs={"aria-label": "Comment"})
    comments = dict()
    # print(postDict)
    for comment in postComments:
        if comment.find(class_="_6qw4") is None:
            continue

        commenter = comment.find(class_="_6qw4").text #name of person
        comments[commenter] = dict()

        comment_text = comment.find("span", class_="_3l3x")

        if comment_text is not None:
            comments[commenter]["text"] = comment_text.text

        comment_link = comment.find(class_="_ns_")
        if comment_link is not None:
            comments[commenter]["link"] = comment_link.get("href")

        comment_pic = comment.find(class_="_2txe")
        if comment_pic is not None:
            img_child = comment_pic.find(class_="img")
            if img_child:
                comments[commenter]["image"] = img_child.get("src")

        commentList = item.find('ul', {'class': '_7791'})
        if commentList:
            comments = dict()
            comment = commentList.find_all('li') #list of comments (Big)
            if comment:
                for litag in comment:
                    #litag is comment_big
                    aria = litag.find(attrs={"aria-label": "Comment"})
                    if aria:
                        #host
                        commenter = aria.find(class_="_6qw4").text
                        comments[commenter] = dict()
                        comment_text = litag.find("span", class_="_3l3x")
                        if comment_text:
                            comments[commenter]["text"] = comment_text.text
                            # print(str(litag)+"\n")

                        comment_link = litag.find(class_="_ns_")
                        if comment_link is not None:
                            comments[commenter]["link"] = comment_link.get("href")

                        comment_pic = litag.find(class_="_2txe")
                        if comment_pic is not None:
                            img_child = comment_pic.find(class_="img")
                            if img_child:
                                comments[commenter]["image"] = img_child.get("src")

                        repliesList = litag.find(class_="_2h2j")
                        if repliesList:
                            reply = repliesList.find_all('li')
                            if reply:
                                comments[commenter]['reply'] = dict()
                                for litag2 in reply:
                                    aria2 = litag2.find(attrs={"aria-label": "Comment reply"})
                                    if aria2:
                                        replier = aria2.find(class_="_6qw4").text
                                        if replier:
                                            comments[commenter]['reply'][replier] = dict()

                                            reply_text = litag2.find("span", class_="_3l3x")
                                            if reply_text:
                                                comments[commenter]['reply'][replier][
                                                    "reply_text"] = reply_text.text

                                            r_link = litag2.find(class_="_ns_")
                                            if r_link is not None:
                                                comments[commenter]['reply']["link"] = r_link.get("href")

                                            r_pic = litag2.find(class_="_2txe")
                                            if r_pic is not None:
                                                img_child = r_pic.find(class_="img")
                                                if img_child:
                                                    comments[commenter]['reply']["image"] = img_child.get("src")
    return comments


#fixed
def _extract_reaction(item):
    toolBar = item.find(attrs={"role": "toolbar"})

    if not toolBar:  # pretty fun
        return
    reaction = dict()
    for toolBar_child in toolBar.children:
        #str = toolBar_child['data-testid']
        #reaction = str.split("UFI2TopShare/tooltip_")[1]

        #reaction[reaction] = 0

        toolBar_child_childs = toolBar_child.contents
        if len(toolBar_child_childs) > 0:
            toolBar_child_child = toolBar_child_childs[0]
            #ex. 1,2K -> 1200
            react_vals = toolBar_child_child['aria-label'].split() #[13K, Love]
            react_name = react_vals[-1].lower()
            num = "".join(react_vals[:-1])

            # fix weird ',' happening in some reaction values
            num = num.replace(',', '.')
            realNum = 0
            if 'K' in num:
                realNum = float(num[:-1]) * 1000
            else:
                realNum = float(num)

            reaction[react_name] = int(realNum)
    return reaction


def _extract_html(page, bs_data, limit_postDate):

    #Add to check
    #Temp file
    with open('./bs.html',"w", encoding="utf-8") as file:
        file.write(str(bs_data.prettify()))

    name_group = ""
    groupTitle = bs_data.find(class_="_19s-")
    if groupTitle:
        name_group = groupTitle.text.strip().lower()
        name_group = re.sub("\(.*\)|\[.*\]|<.*>", "", name_group)
        name_group = re.sub("\W+", "_", name_group)
        print(f"name_group {name_group}")

    k = bs_data.find_all(class_="_5pcr userContentWrapper")
    postBigDict = list()

    for item in k:
        postDict = dict()
        post_date = _extract_postDate(item)
        if is_valid_postDate(limit_postDate, post_date):
            postDict['Date'] = post_date
            postDict['Author'] = _extract_author(item)
            postDict['Group'] = page
            postDict['Post'] = _extract_post_text(item)
            postDict['Link'] = _extract_link(item)
            postDict['PostId'] = _extract_post_id(item)
            postDict['Image'] = _extract_image(item)
            postDict['Shares'] = _extract_shares(item)
            postDict['Comments'] = _extract_comments(item)
            postDict['Reaction'] = _extract_reaction(item)

        #Add to check
        postBigDict.append(postDict)
        #temporary file
        with open('./postBigDict.json','w', encoding='utf-8') as file:
            file.write(json.dumps(postBigDict, ensure_ascii=False).encode('utf-8').decode())

    return postBigDict, name_group


def _login(browser, email, password):
    browser.get("http://facebook.com")
    browser.maximize_window()
    email_box = browser.find_element_by_name("email") or browser.find_element_by_id("email")
    email_box.send_keys(email)
    pass_box = browser.find_element_by_name("pass") or browser.find_element_by_id("pass")
    pass_box.send_keys(password)
    loginButton = browser.find_element_by_name("login") or browser.find_element_by_id("loginbutton")
    loginButton.click()
    time.sleep(10)

"""
args:
    + lenOfPage is the Number Of Scrolls Needed
    + infinite_scroll gives an assumption lenOfPage 
"""
def _count_needed_scrolls(browser, infinite_scroll, numOfPost):
    if infinite_scroll:
        lenOfPage = browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;"
        )
    else:
        # roughly 8 post per scroll kindaOf, counted by experience
        lenOfPage = int(numOfPost / 8) or 1
    print("Number Of Scrolls Needed " + str(lenOfPage))
    return lenOfPage

def is_valid_postDate_scroll(limit_date, browser):
    # Now that the page is fully scrolled, grab the source code.
    source_data = browser.page_source

    # Throw your source into BeautifulSoup and start parsing!
    bs_data = bs(source_data, 'html.parser')

    last_post = bs_data.find_all(class_="_5pcr userContentWrapper")[-1]
    last_postDate = _extract_postDate(last_post)
    return last_postDate >= limit_date
    
def is_valid_postDate(limit_date, post_date):
    return post_date >= limit_date
    

"""
after scroll, all elements in html will be shown up
"""
def _scroll(browser, infinite_scroll, lenOfPage, limit_postDate):
    lastCount = 0
    match = False

    while not match:
        if infinite_scroll:
            lastCount = lenOfPage
        else:
            lastCount += 1

        # wait for the browser to load, this time can be changed slightly ~3 seconds with no difference, but 5 seems
        # to be stable enough
        time.sleep(5)

        if infinite_scroll:
            # scroll to the end of page and return the lenOfPage that will be changed if there is another page when scroll to the end of page
            lenOfPage = browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return "
                "lenOfPage;")

            #if not is_valid_postDate_scroll(limit_postDate, browser):
            #    break
        else:
            # scroll to the end of page
            browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return "
                "lenOfPage;")

        if lastCount == lenOfPage:
            match = True

def show_up_comments(browser):
    moreComments = browser.find_elements_by_xpath('//a[@class="_4sxc _42ft"]')
    print("Scrolling through to click on more comments")
    while len(moreComments):
        for moreComment in moreComments:
            #ActionChains are a way to automate low level Share such as mouse movements, mouse button actions, key press, and context menu Share. This is useful for doing more complex actions like hover over and drag and drop.
            action = webdriver.common.action_chains.ActionChains(browser)
            try:
                # move to where the comment button is 
                action.move_to_element_with_offset(moreComment, 5, 5)
                action.perform()
                # start action click in the webdriver of selenium
                moreComment.click()
            except Exception as e:
                # do nothing right here
                # pass
                print(e)

        # When click viewMoreComments but still having this button due to too long list of comments
        moreComments = browser.find_elements_by_xpath('//a[@class="_4sxc _42ft"]')

def show_up_SeeMoreCmt(browser):
    seeMoreCmts = browser.find_elements_by_xpath('//a[@class="_5v47 fss"]')
    print("Scrolling through to click on see more")
    # while len(seeMoreCmt):
    for seeMoreCmt in seeMoreCmts:
        action = webdriver.common.action_chains.ActionChains(browser)
        try:
            # move to where the comment button is 
            action.move_to_element_with_offset(seeMoreCmt, 5, 5)
            action.perform()
            # start action click in the webdriver of selenium
            # just on click will show up all the comments hidden
            seeMoreCmt.click()
            # time.sleep(30)
        except Exception as e:
            # do nothing right here
            # pass
            print(e)

def extract(browser, page, numOfPost, limit_postDate, infinite_scroll=False, scrape_comment=False):
    assert limit_postDate, "limit_postDate must be defined"
    
    lenOfPage = _count_needed_scrolls(browser, infinite_scroll, numOfPost)
    _scroll(browser, infinite_scroll, lenOfPage, limit_postDate)

    # click on all the comments to scrape them all!
    # TODO: need to add more support for additional second level comments
    # TODO: ie. comment of a comment

    if scrape_comment:
        show_up_comments(browser)
        show_up_SeeMoreCmt(browser)
        print("finish more comments")

    # Now that the page is fully scrolled, grab the source code.
    source_data = browser.page_source

    # Throw your source into BeautifulSoup and start parsing!
    bs_data = bs(source_data, 'html.parser')

    postBigDict, name_group = _extract_html(page, bs_data, limit_postDate)

    return postBigDict, name_group

def crawl_input_parser():
    parser = argparse.ArgumentParser(description="Facebook Page Scraper")
    required_parser = parser.add_argument_group("required arguments")
    required_parser.add_argument('-page', '-p', help="The Facebook Public Page you want to scrape", required=True)
    required_parser.add_argument('-len', '-l', help="Number of Posts you want to scrape", type=int, required=True)
    required_parser.add_argument('-limit_postDate', '-d', help="The oldest date posts appeared", required=True)
    optional_parser = parser.add_argument_group("optional arguments")
    optional_parser.add_argument('-infinite', '-i',
                                 help="Scroll until the end of the page (1 = infinite) (Default is 0)", type=int,
                                 default=0)
    optional_parser.add_argument('-usage', '-u', help="What to do with the data: "
                                                      "Print on Screen (PS), "
                                                      "Write to Text File (WT) (Default is WT)", default="CSV")

    optional_parser.add_argument('-comments', '-c', help="Scrape ALL Comments of Posts (y/n) (Default is n). When "
                                                         "enabled for pages where there are a lot of comments it can "
                                                         "take a while", default="No")
    args = parser.parse_args()

    f_configs = open('configs.yaml')
    configs = yaml.full_load(f_configs)
    f_configs.close()

    email = configs['credentials']['email']
    password = configs['credentials']['password']
    
    infinite = False
    if args.infinite == 1:
        infinite = True

    scrape_comment = False
    if args.comments == 'y':
        scrape_comment = True

    with open('facebook_credentials.txt') as _file:
        email = _file.readline().split('"')[1]
        password = _file.readline().split('"')[1]

    option = Options()
    option.add_argument("--disable-infobars")
    option.add_argument("start-maximized")
    option.add_argument("--disable-extensions")

    # Pass the argument 1 to allow and 2 to block
    option.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })

    #  should be in the same folder as file
    browser = webdriver.Chrome(executable_path="/home/khacquy/chromedriver_linux64_/chromedriver", options=option)
    _login(browser, email, password) #login or not: comment to not login.
    browser.get(link)

    postBigDict, name_group = extract(browser=browser, page=link, numOfPost=args.len\
                          , infinite_scroll=infinite, scrape_comment=scrape_comment\
                          , limit_postDate=args.limit_postDate)


    #TODO: rewrite parser
    if args.usage == "WT":
        with open(name_group + '.txt', 'w', encoding="utf-8") as file:
            for post in postBigDict:
                file.write(json.dumps(post))  # use json load to recover

    elif args.usage == "CSV":
        with open(name_group + '.csv', 'w', encoding="utf-8") as csvfile:
           writer = csv.writer(csvfile)
           #writer.writerow(['Post', 'Link', 'Image', 'Comments', 'Shares'])
           writer.writerow(['PostId', 'Group', 'Date', 'Author', 'Post', 'Link', 'Image', 'Comments', 'Shares', 'Reaction'])

           for post in postBigDict:
              writer.writerow([post['PostId'], post['Group'], post['Date'], post['Author']\
                              , post['Post'], post['Link'], post['Image']\
                              , post['Comments'], post['Shares'], post['Reaction']])
              #writer.writerow([post['Post'], post['Link'],post['Image'], post['Comments'], post['Shares']])

    else:
        for post in postBigDict:
            print("\n")

    browser.close()
    print("Finished")

def crawl_input_files():
    f_configs = open('configs.yaml')
    configs = yaml.full_load(f_configs)
    f_configs.close()

    email = configs['credentials']['email']
    password = configs['credentials']['password']

    args = configs['args']
    infinite = args['infinite'] or 0
    limit_postDate = args['limit_postDate']
    assert limit_postDate, "limit_postDate is required"
    scrape_comment = args['comments'] or False
    
    option = Options()
    option.add_argument("--disable-infobars")
    option.add_argument("start-maximized")
    option.add_argument("--disable-extensions")

    # Pass the argument 1 to allow and 2 to block
    option.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })

    #  should be in the same folder as file
    browser = webdriver.Chrome(executable_path="/home/khacquy/chromedriver_linux64_/chromedriver", options=option)
    _login(browser, email, password) #login or not: comment to not login.

    id_page = 0
    with open(args["file_links"], 'r') as fLinks:
        for link in fLinks.readlines():
            id_page += 1
            link = link.strip()
            link = link[:-1] if link[-1] == "/" else link
            
            browser.get(link)
            
            postBigDict, name_group = extract(browser=browser, page=link, numOfPost=args['len']\
                                , infinite_scroll=infinite, scrape_comment=scrape_comment\
                                , limit_postDate=limit_postDate)

            #remove noise chars
            fout_name = re.sub("\W+", "_", link.split('/')[-1].lower())
            if not re.search("[^0-9]+", fout_name):
                #have just number
                fout_name += f"_{name_group}"
            fout_name += f"_{id_page}"

            #TODO: rewrite parser
            type_fout = args['usage'] or "CSV"

            if type_fout == "WT":
                with open(fout_name + '.txt', 'w', encoding="utf-8") as text_file:
                    for post in postBigDict:
                        text_file.write(json.dumps(post))  # use json load to recover

            elif type_fout == "CSV":
                with open(fout_name + '.csv', 'w', encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)
                    #writer.writerow(['Post', 'Link', 'Image', 'Comments', 'Shares'])
                    writer.writerow(['PostId', 'Group', 'Date', 'Author','Post', 'Link', 'Image', 'Comments', 'Shares', 'Reaction'])

                    for post in postBigDict:
                        writer.writerow([post['PostId'], post['Group'], post['Date'], post['Author']\
                              , post['Post'], post['Link'], post['Image']\
                              , post['Comments'], post['Shares'], post['Reaction']])
                        #writer.writerow([post['Post'], post['Link'],post['Image'], post['Comments'], post['Shares']])

            else:
                for post in postBigDict:
                    print("\n")

            print(f"Finished {link}")
            
    browser.close()

if __name__ == "__main__":
    # crawl_input_parser()
    crawl_input_files()

