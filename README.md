This python program crawl RSS data from websites (which must have a RSS link.) users select.
Automatically urls are collected from a toppage until a RSS page found.
If a RSS page found for each website,this program get all titles,urls,dates and store them to database so that URLs are not doubled after shaping data.
Database has many tables one of which is for URLs of websites and the others are for data of data(title,url,date) of each website.

How it works.
Users put their site urls.
This program looks for a RSS page.
Firstly,confirm if a url put by a user is a RSS page url(it can not be matched in many situations.) and a urls with /rss is a RSS page url(it is often matched.) 
ex)
Although http://aaa.bbb.ccc can not be a RSS page,http://aaa.bbb.ccc/rss is often a RSS page of many blogs.
Next,this collects all of urls in a toppage(which means a page of a url given by a user first.),and we call collected pages chilspages.
Childpages are done the same as a toppage is done,and we call collected page grandchildPages.
Finally,grandchild pages are checked if they are a RSS page or have a RSS page.

How Database collects data.
If a RSS page found,the program does scraping data(title,link,date) from the RSS page,and shepe the date so that easily it can be used.
If collected data already exists in the database,they are ignored and the others are inserted into the database.

The structure of the database.
It has many tables which are for URLs of websites and for data of each website as mentioned.
In the URLs table,there are only IDs(primary key) and URLs of websites.
Other tables are bound by IDs,and their table name are like table + id(which is the same with id in the URLs table).
