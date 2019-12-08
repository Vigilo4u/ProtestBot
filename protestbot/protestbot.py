from simplesteem.simplesteem import SimpleSteem
import sqlite3
from sqlite3 import Error
import sys
import re
import importlib
import os


class ProtestBot:


    def __init__(self, botname="settings"):
        bot = importlib.import_module("."+botname, "protestbot")
        self.cfg = bot.Config()
        self.steem = SimpleSteem(mainaccount=self.cfg.protester_account,
                                keys=self.cfg.keys, 
                                screenmode="verbose",
                                logpath="/home/dragon/")
        self.abuser_of_power = self.cfg.abuser_of_power
        self.protester_account = self.cfg.protester_account
        self.replies = []
        self.the_abused = []
        self.db = BotDB()
        self.db.initialize_database()
        self.db.initialize_abused_database()

                
    def get_all_posts_and_replies(self, friends=False):
        print("     __ Retrieving abuser's history __\n\n")
        h = self.steem.get_my_history(account=self.abuser_of_power, limit=1000)
        if h is False or h is None:
            return None
        for a in h:
            if a[1]['op'][0] == "comment":
                ident = None
                if friends:
                    if (a[1]['op'][1]['author'] != self.abuser_of_power):
                        permlink = a[1]['op'][1]['permlink']
                        author = a[1]['op'][1]['author']
                        ident = self.steem.util.identifier(author, permlink)
                else:
                    if (a[1]['op'][1]['author'] == self.abuser_of_power):
                        permlink = a[1]['op'][1]['permlink']
                        ident = self.steem.util.identifier(self.abuser_of_power, permlink)
                if ident is not None:
                    duplicate_found = False
                    for r in self.replies:
                        if r == ident:
                            duplicate_found = True
                    if not duplicate_found:
                        if not self.db.already_posted(ident):
                            self.replies.append(ident)
                            print("\n__ *new post* __")
                            print(ident)


    def find_downvoted_authors(self):
        print("     __ Retrieving list of the abused __\n\n")
        h = self.steem.get_my_history(account=self.abuser_of_power, limit=1000)
        if h is False or h is None:
            return None
        for a in h:
            if a[1]['op'][0] == "vote":
                if (a[1]['op'][1]['voter'] == self.abuser_of_power):
                    if (a[1]['op'][1]['weight'] < 0):
                        author = a[1]['op'][1]['author']
                        permlink = a[1]['op'][1]['permlink']
                        ident = self.steem.util.identifier(author, permlink)
                        duplicate_found = False
                        for b in self.the_abused:
                            if b == author:
                                duplicate_found = True
                        if not duplicate_found:
                            self.the_abused.append(ident)
                            print("\n__ *newly abused* __")
                            print(ident)


    def upvote_the_downvoted(self):
        for a in self.the_abused:
            if self.cfg.weight < 0:
                w = self.cfg.weight * -1
            else:
                w = self.cfg.weight
            self.steem.vote(a, weight=w)
            print ("Upvoted {} by {}%".format(a, w))


    def send_memos_to_the_downvoted(self):
        if self.ensure_balance():
            self.find_downvoted_authors()
            if self.the_abused is not None and len(self.the_abused) > 0:
                pmsg = self.memo_temp()
                for a in self.the_abused:
                    self.steem.transfer_funds(a, 0.001, "STEEM", pmsg)
                    print("Sent memo to " + a)
            else:
                print("No one has been downvoted!")
                

    def ensure_balance(self):
        bal = self.steem.check_balances(self.protester_account)
        print ("Current STEEM balance: " + str(bal[1]))
        if float(bal[1]) > 0.0001:
            return True
        else:
            return False


    def reply_to_abuser_posts(self, friends=False):
        self.get_all_posts_and_replies(friends)
        pmsg = self.protest_temp()
        for r in self.replies:
            if self.steem.reply(r, pmsg):
                if not friends and self.cfg.downvote:
                    self.steem.vote(r, weight=self.cfg.weight)
            self.db.add_reply(r)
            

    def post_to_profile(self):
        pmsg = self.protest_temp()
        permlink = re.sub(r' ', '-', self.cfg.title)
        permlink = re.sub(r'[^A-Za-z0-9\-]', '', permlink)
        permlink = permlink.lower()
        self.steem.post(title, pmsg, permlink, self.cfg.tags)


    def template(self, filename):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        if os.path.exists(dir_path + "/" + filename):
            with open(dir_path + "/" + filename,'r') as f:
                try:
                    msg = f.read()
                except:
                    f.close()
                    print("\nCould not open post_template.txt!\n")
                    return None
                else:
                    f.close()
                    return msg
        return None


    def protest_temp(self):
        msg = self.template("protest_template.txt")
        pmsg = msg.format(self.abuser_of_power, 
                        self.abuser_of_power,
                        self.protester_account,
                        self.protester_account,
                        self.protester_account,
                        self.protester_account,
                        self.protester_account,
                        self.protester_account,
                        self.protester_account,
                        self.abuser_of_power)
        return pmsg


    def memo_temp(self):
        msg = self.template("memo_template.txt")
        return msg.format(self.abuser_of_power, 
                        self.abuser_of_power)



class BotDB():


    def __init__(self):
        print("Connecting to database")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        try:
            self.conn = sqlite3.connect(dir_path + "/protest_log.db")
        except Error as e:
            print(e)
        self.c = self.conn.cursor()


    def __del__(self):
        print("Disconnecting from database")
        self.conn.close()


    def initialize_database(self):
        self.c.execute("CREATE TABLE IF NOT EXISTS "
                        + "abusers_replies"
                        + " (ID INT "
                        + "PRIMARY KEY, Identifier varchar(250) UNIQUE, "
                        + "Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
        self.conn.commit()


    def initialize_abused_database(self):
        self.c.execute("CREATE TABLE IF NOT EXISTS "
                        + "the_abused"
                        + " (ID INT "
                        + "PRIMARY KEY, Username varchar(250) UNIQUE, "
                        + "Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
        self.conn.commit()


    def already_sent_memo(self, user):
        self.c.execute("SELECT * FROM "
                        + "the_abused"                     
                        + " WHERE Username = '%s';" % user)
        rows = self.c.fetchall()
        if len(rows) > 0:
            return True
        else:
            return False


    def already_posted(self, identifier):
        self.c.execute("SELECT * FROM "
                        + "abusers_replies"                     
                        + " WHERE Identifier = '%s';" % identifier)
        rows = self.c.fetchall()
        if len(rows) > 0:
            return True
        else:
            return False


    def add_reply(self, identifier):
        print("Adding {}".format(identifier))
        self.c.execute("INSERT INTO "
                        + "abusers_replies"
                        + " (Identifier) VALUES ('%s');" % identifier)
        self.conn.commit()


    def add_victim(self, username):
        print("Adding {}".format(username))
        self.c.execute("INSERT INTO "
                        + "the_abused"
                        + " (Username) VALUES ('%s');" % username)
        self.conn.commit()

