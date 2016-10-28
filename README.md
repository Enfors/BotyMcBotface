# BotyMcBotface

An example IRC bot skeleton written in Python 3.

## Introduction

BotyMcBotface (because what else can you name a bot, really?) is a
simple IRC bot skeleton inspired by the tutorial at
https://pythonspot.com/en/building-an-irc-bot. This skeleton doesn't
really do anything; it was designed as an example of how to write a
bot that others can build upon.

## Files

There are basically two files - the actual IRC code in the file
**irc.py**, and the main file, **bot.py**. The latter has plenty of
comments, and should probably be the first one you look at. The other
one, **irc.py** should be usable as-is, but it's pretty bare-bones as
of now. However, to make your own bot, changing **bot.py** should be
enough. 

## Setup

To make this work, you first need to register your own version of the
bot's nickname on Freenode:
http://www.wikihow.com/Register-a-Nickname-on-Freenode

Then, you put two files in the same directory as the code, one called
**nickname** which contains the nickname you registered, and one
called **password** which unsurprisingly should contain the password.
Having done that, you should be able to just start **bot.py** to get
it running. Read its code and comments for more in-depth information
of how it works.

-Enfors-

