import urllib2,sys,re,time,random,feedparser,database
from HTMLParser import HTMLParser

access = sys.argv[1]
RSS = False
URLList = list()
ErrorList = list()

class ParseHTML(HTMLParser):
    RSS = False
    URLList = list()
    def __init__(self):
        HTMLParser.__init__(self)

    def handle_starttag(self,tagname,attribute):
        # print "handle_starttag: " + tagname
        if tagname == "rss":
            self.RSS = True
        if tagname == "a":
            url = dict(attribute).get('href')
            if url != "":
                self.URLList.append(url)

hasHttp = re.compile(r'^https?')
def has_http(url):
    print "has_http: " + str(url)
    return hasHttp.match(url) # return None or an object.

isHtml = re.compile(r'html/?$')
def is_html(url):
    print "is_html: " + str(url)
    return isHtml.search(url)


# hasForwardSlashes = re.compile(r'^/')
def has_forward_slashes(url):
    print "has_forward_slashes: " + url
    if url[0] == "/":
        return True
    else:
        return False

# hasEndSlahes = re.compile(r'$/')
def has_end_slashes(url):
    if len(url) == 1:
        return False

    print "has_end_slashes: " + str(url)
    if url[-1] == "/":
        return True
    else:
        return False

def has_RSS_link(url):
    print "has_RSS_link: " + str(url + "/rss")
    html = read_HTML(url + "/rss")
    if html:
        parser = ParseHTML()
        parser.feed(html)
        if parser.RSS:
            return True
        return False
    return False

def delete_slashes(url):
    print "deleting slashes"
    if url[0] == "/":
        return url[1:]
    else:
        return url

isRSS = re.compile(r'/rss.*\.xml|/index\.rdf')
def is_RSS_link(url):
    print "is_RSS_link: " + url
    return isRSS.search(url)

def read_HTML(url):
    try:
        f = urllib2.urlopen(url)
        html = f.read().decode('utf-8')
    except Exception as e:
        print "An Error Has Occurred: " + str(e)
        ErrorList.append(["Error","url: " + str(url),e])
        html = False
    return html

def get_page_URL(baseURL,html):
    parser = ParseHTML()
    parser.feed(html)
    pageURL = list()

    print "baseURL: " + baseURL

    for url in parser.URLList:
        try:
            print "url: " + str(url)
        except UnicodeEncodeError:
            continue
        if url == None:
            continue

        """
        elif is_html(url) == None:
            continue
        """

        # if a url has a end slash,it is going to be deleted.
        if has_end_slashes(url):
            url = url[:-1]


        if has_http(url) != None:
            pass
        else:
            print "doesnt have http: " + str(url)
            if has_forward_slashes(url):
                url = access + delete_slashes(url)
            else:
                url = baseURL + "/" + url



        print "getting access to: " + url

        # if url/rss has a content,it must be a RSS page.

        if has_RSS_link(url):
            print "has_RSS_link: " + str(url)
            return [url + '/rss']

        # if a url ends with rss.*\.xml,it must be a RSS page.
        if is_RSS_link(url):
            return [url]

        # if a url already appeared,it is ignored.
        if url in URLList:
            pass
        else:
            URLList.append(url)
            pageURL.append(url)
    return pageURL


#def is_blog_for_livedoorblog(html):

isBlog = re.compile(r'blog')
def is_blog(html):
    print "Checking if this page is a blog."
    if len(isBlog.findall(html)) > 10:
        print "maybe a blog"
        return True
    return False

def send_RSS_data(baseURL,url):
    data = read_RSS(url)
    database.operate_database(baseURL,data)

def shape_updated(updated):
    shapedUpdated = time.strftime('%Y-%m-%d %H:%M:%S',updated)
    #shapedUpdated = "%s-%s-%s %s:%s:%s" % (str(updated{tm_year}),str(updated[tm_mon]),str(updated[tm_mday]),str(updated[tm_hour]),str(updated[tm_min]),str(updated[tm_sec]))
    return shapedUpdated

def read_RSS(url):
    try:
        print 'reading a RSS page: ' + url
        response = feedparser.parse(url)
        RSSData = list()
        for entry in response.entries:
            title = entry.title
            link = entry.link
            updated = entry.updated_parsed
            shapedUpdated = shape_updated(updated)
            RSSData.append([link,title,shapedUpdated])
        return RSSData
    except Exception as e:
        print e
        return False


def get_child_page_URL(topPageURL):
    childPageURL = list()
    for topURL in topPageURL:
        time.sleep(random.randint(5,10))
        html = read_HTML(topURL)
        is_blog(html)
        tempList = get_page_URL(topURL,html) #append urls to tempList likewise topPageURL is done.
        # If the length of tempList is 1,it should be a url of RSS.
        if len(tempList) > 1:
            childPageURL.append(tempList) #append tempList to childPageURL list and continue.
        elif len(tempList) == 0:
            pass
        else:
            print "read_RSS"
            return [tempList[0]]
    return childPageURL

def get_grandchild_page_URL(childPageURL):
    grandChildPageURL = list()
    for childURLList in childPageURL:
        for childURL in childURLList:
            time.sleep(random.randint(5,10))
            html = read_HTML(childURL)
            is_blog(html)
            tempList = get_page_URL(childURL,html) # Append urls to tempList likewise topPageURL is done.
            # If the length of tempList is 1,it should be a url of RSS.
            if len(tempList) > 1:
                grandChildPageURL.append(tempList)
            elif len(tempList) == 0:
                pass
            else:
                return [tempList[0]]
    return grandChildPageURL

def check_grandchild_pages(grandChildPageURL):
    for grandChildURLList in grandChildPageURL:
        for grandChildURL in grandChildURLList:
            time.sleep(random.randint(5,10))
            html = read_HTML(grandChildURL)
            is_blog(html)
            tempList = get_page_URL(grandChildURL,html)
            if len(tempList) >= 1:
                pass
            else:
                return [tempList[0]]


def initial_operation_for_base_URLs(baseURL):
    URLList.append(baseURL)
    # if a baseURL has a end slash,it is going to be deleted.
    if has_end_slashes(baseURL):
        baseURL = baseURL[:-1]
    print "baseURL: " + baseURL
    if has_RSS_link(baseURL):
        url = baseURL + '/rss'
        try:
            send_RSS_data(url,url)
        except Exception as e:
            print "An error has occurred: " + str(e)
            ErrorList.append(["Error","url: " + str(url),e])
            return baseURL
        else:
            return False
    if is_RSS_link(baseURL):
        send_RSS_data(baseURL,baseURL)
    return baseURL

if __name__ == '__main__':
    #url = sys.argv[1]
    baseURL = initial_operation_for_base_URLs(access)
    if baseURL:
        html = read_HTML(baseURL)

        is_blog(html)
        topPageURL = get_page_URL(baseURL,html)
        # if the number of URL in topPageURL is only one, it should be a url of RSS.
        if len(topPageURL) > 1:
            # Do the same action to child pages of a toppage.
            childPageURL = get_child_page_URL(topPageURL)
            if len(childPageURL) > 1:
                grandChildPageURL = get_child_page_URL(childPageURL)
                if len(grandChildPageURL) > 1:
                    check_grandchild_pages(grandChildPageURL)
                elif len(grandChildPageURL) == 1:
                    send_RSS_data(baseURL,grandChildPageURL[0])
                else:
                    print "No URLs."
            elif len(childPageURL) == 1:
                send_RSS_data(baseURL,childPageURL[0])
            else:
                print "No URLs."

        elif len(topPageURL) == 1:
            send_RSS_data(baseURL,topPageURL[0])
        else:
            print "An Error Has Occurred."

    for error in ErrorList:
        print error
