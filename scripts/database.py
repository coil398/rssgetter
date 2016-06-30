import sqlite3,os,shutil

DB_NAME = "data.db"
URL_TABLE = "urlTable"

class SQLite3Connector:
    def __init__(self,url):
        self.con = sqlite3.connect("../data.db")
        self.cur = self.con.cursor()
        # Check whether A table for URLs exist.
        if self.URLs_table_exists() == None:
            self.create_URLs_table()

        if self.blog_URL_in_table(url) == None:
            self.insert_blog_data(url)

    def URLs_table_exists(self):
        self.cur.execute("""SELECT * FROM sqlite_master WHERE type='table' and name='URLs'""")
        return self.cur.fetchone()

    def create_URLs_table(self):
        self.cur.execute("""CREATE TABLE URLs(id INTEGER PRIMARY KEY AUTOINCREMENT,url TEXT)""")
        self.con.commit()

    def blog_URL_in_table(self,url):
        self.cur.execute("""SELECT * FROM URLs WHERE url='%s'""" % url)
        return self.cur.fetchone()

    def insert_blog_data(self,url):
        self.cur.execute("""INSERT INTO URLs values(null,'%s')""" % url)

    def backup_database(self):
        print "backup database"
        i = 1
        while True:
            if os.path.exists('./bk/data' + str(i) + '.bk'):
                i += 1
            else:
                shutil.copy('./data.db','./bk/data' + str(i) + '.bk')
                return

    def get_blog_ID(self,url):
        self.cur.execute("""SELECT id FROM URLs WHERE url='%s'""" % url)
        return self.cur.fetchone()[0]

    def blog_updated(self,blogURL,data):
        self.blogID = self.get_blog_ID(blogURL)
        self.tableName = 'blogTable' + str(self.blogID)
        if self.blog_table_exists() == None:
            self.create_blog_table()
        else:
            print "Exists"
        # What th is index of new data.
        num = self.check_which_data_exists(data)
        newData = data[:num]
        self.insert_blog_page_data(newData)

    def blog_table_exists(self):
        self.cur.execute("""SELECT * FROM sqlite_master WHERE type='table' and name='%s'""" % self.tableName)
        return self.cur.fetchone()

    def create_blog_table(self):
        self.cur.execute("""CREATE TABLE %s(id INTEGER PRIMARY KEY AUTOINCREMENT,pageURL TEXT,pageTitle TEXT,updatedTime TEXT)""" % self.tableName)

        self.con.commit()

    def check_which_data_exists(self,data):
        sql = """SELECT * FROM %s WHERE pageURL='%s'"""
        for i in range(len(data)):
            self.cur.execute(sql % (self.tableName,data[i][0]))
            if self.cur.fetchone() != None:
                return i
        return len(data)

    def insert_blog_page_data(self,data):
        sql = """INSERT INTO %s values(null,?,?,?)""" % self.tableName
        with open('./log/' + self.tableName + '.log','a+') as f:
            for datum in data:
                print "Inserting data: " + str(datum)
                print 'outputting insert log'
                f.write(str(datum) + '\n')

                self.cur.execute(sql , (datum[0],datum[1],datum[2]))
                self.con.commit()
            f.write('\n-------------\n')

    def close_database(self):
        print "closing database."
        self.con.close()

    def show_all_data(self):
        sql = """SELECT * FROM %s""" % self.tableName
        self.cur.execute(sql)
        print self.cur.fetchall()

def operate_database(url,data):
    print 'URL: ' + url
    database = SQLite3Connector(url)
    database.blog_updated(url,data)
    #database.show_all_data()
    database.backup_database()
    database.close_database()
