#!/usr/bin/python3

import sys
from protestbot.protestbot import ProtestBot

# Entry point
def run(args=None):
    # First we capture the command line arguments
    if len(sys.argv) < 2:
        print('''
ProtestBot Help

Command syntax: runbot [command] [botname]

The botname is optional. It should be the name of a python module copied from settings.py. Example: mybot.py

List of commands


reply-to-abuser                 Replies to all posts and comments made by 
                                the abuser of power using the 
                                protest_template.txt.

reply-to-abuser-friends         Replies to all comments left by others on 
                                the abuser's posts. Also uses the 
                                protest_template.txt. This command takes 
                                two arguments:
                                1) The title of the post 2) a list of 5 tags.

abused                          Prints out a list of those the abuser 
                                downvoted recently.

memos                           Sends 0.001 transactions to those the abuser 
                                downvoted along with the message in 
                                memo_template.txt

balance                         Prints the current STEEM and SBD balance 
                                for the bot.

replies                         Prints a list of all replies recently made 
                                by the abuser.

replies-to-friends              Prints a list of replies recently made to 
                                the abuser's post by others.

upvote-downvoted                Finds all the authors downvoted by the abuser
                                and gives them an upvote.

''')
    else:

        command = str(sys.argv[1])

        # If no bot name was given use the default settings
        if len(sys.argv) == 2:
            commander("settings", command)
        # Iterate through a list of bot names and execute the same command for each
        else:
            for i in range(2, len(sys.argv)):
                commander(str(sys.argv[i]), command)



def commander(selectedbot, command):
    # import the settings based on which bot we're using
    a = ProtestBot(botname=selectedbot)

    # The various commands
    if command == "reply-to-abuser":
        a.reply_to_abuser_posts()
    elif command == "reply-to-abuser-friends":
        a.reply_to_abuser_posts(friends=True)
    elif command == "post":
        a.post_to_profile()
    elif command == "abused":
        a.find_downvoted_authors()
    elif command == "memos":
        a.send_memos_to_the_downvoted()
    elif command == "balance":
        a.ensure_balance()
    elif command == "replies":
        a.get_all_posts_and_replies()
    elif command == "replies-to-friends":
        a.get_all_posts_and_replies(friends=True)
    elif command == "upvote-downvoted":
        a.find_downvoted_authors()
        a.upvote_the_downvoted()
    else:
        print ("Invalid command.")



if __name__ == "__main__":

    run()


# EOF
