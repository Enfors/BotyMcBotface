#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

# INITIAL SETUP
# =============

# The "irc" import is the irc.py file in this directory, not a
# system level import.
import irc

nickname = "BotyMcBotface"      # The bot's nickname

server = "irc.freenode.net"     # The server to connect to
channel = "#enfors"             # The channel to join

# While we put other variables such as the server to connect to and
# the channel to join in vars directly in this file, doing the same
# with the bot's password would be a bad idea, seeing as how this file
# is publicly available on Github. So, read it from a local file
# instead (which never ends up on Github).

def load_var(var_name):
    var = ""
    
    try:
        with open(var_name, "r") as f:
            var = f.readline().strip()
    except FileNotFoundError:
        print("You need to put your bot's %s in a file called %s "
              "in this directory." % (var_name, var_name))
        raise SystemExit

    return var

nickname = load_var("nickname")
password = load_var("password")

# Create the bot object (which is defined in the file irc.py). If we
# set the debug flag to True, we get more information on what is
# happening with the protocol. It's a useful way to learn how the IRC
# protocol works.
bot = irc.IRCBot(nickname, password, debug = False)

# Connect to the server. This will also log in, and give the server
# our nickname and password.
bot.connect(server, channel)

# Join additional channels:
bot.join_channel("#bots")

# MAIN LOOP
# =========

while True:

    # Get one message from the IRC server. The '5' is a timeout; If
    # nothing happens on the server in 120 seconds, the get_msg()
    # function will return (None, None, None, None) giving us a chance
    # to do stuff here periodically. Otherwise, we'd be stuck waiting
    # for messages forever if there are none. This way, we can do
    # something else every 5 seconds or so if we want.
    sender, msg_type, channel, msg_text = bot.get_msg(5)

    # Now, we (possibly - unless get_msg() timed out) have a sender, a
    # msg_type, a channel and a msg_text. We can check these to decide
    # what we want to do (if anything) with this message.

    # The IRC protocol is weird. The message type "PRIVMSG" can mean
    # two different things, depending on what "channel" is set to.
    #
    #   1. If "channel" is the same as the bot's nickname, then it is
    #      an actual private message.
    # 
    #   2. Otherwise, it's an ordinary message on the channel
    #      specified in "channel".

    # Let's handle actual private messages first:
    if (msg_type == "PRIVMSG" and channel == nickname):
        print("Private message: %s->%s: %s" % (sender, channel, msg_text))

        # Since we're calling privmsg() with the sender as the recipient
        # (the first argument), what we send will also be an actual
        # private message. 
        bot.privmsg(sender, "Hello, I'm a bot skeleton. I can't really "
                    "do anything, I exist merely as an example of how "
                    "to write an IRC bot in Python that others can "
                    "extend if they want. Take a look at my code at "
                    "github.com/enfors/BotyMcBotface if you're "
                    "interested.")

    # Now, let's handle ordinary channel messages:
    if (msg_type == "PRIVMSG" and channel != nickname):
        print("Channel message: %s @ %s: %s" % (sender, channel, msg_text))

    # If we get a message of type JOIN, that means that the 'sender' joined
    # the channel specified in 'channel'.
    if (msg_type == "JOIN" and sender != nickname):
        bot.privmsg(channel, "Hello %s, welcome to %s!" % (sender, channel))

        # If the person who joined is called "enfors", then let's make
        # him or her an operator in this channel. Replace "enfors" with
        # your own IRC name (not the bot's name) if you want. Please note
        # that this will only work if the bot is a channel operator.
        if (sender == "enfors"):
            bot.make_operator(channel, sender)

    # Let's ask people who leave our channel to come back:
    if (msg_type == "PART" and sender != nickname):
        bot.privmsg(sender, "Please come back to %s soon!" % channel)
            
    # That's it!
    #
    # That wasn't very difficult, was it? Feel free to extend this simple
    # skeleton with more functionality. For example, you could make it
    # so that it's owner (you) can send it a private message to add a
    # "friend", and have the bot instantly make all "friends" who join the
    # channel get a greeting or perhaps operator status.
    #
    # Happy hacking!
    #
    # https://github.com/enfors
    
