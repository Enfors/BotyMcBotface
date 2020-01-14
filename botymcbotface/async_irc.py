#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import asyncio
import re
import select
import socket
import time


class IRCBot:
    """
    A simple IRC bot skeleton.
    """
    def __init__(self, nickname, password, debug_level=0):
        self.nickname = nickname
        self.password = password
        self.debug_level = debug_level

        # done: prob not needed
        # self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # done: async
    async def connect(self, server, channel):
        """
        Connect to the specified IRC server.
        """
        connected = False
        skip_seconds = 10
        self.debug_print("Connecting to: " + server, 1)

        while not connected:
            try:
                # done: open_connection
                # self.socket.connect((server, 6667))
                self.reader, self.writer = await asyncio.open_connection(server,
                                                                         6667)
                connected = True
            except:
                self.debug_print(f"Connection failed. Retrying in "
                                 f"{skip_seconds} seconds.")
                await asyncio.sleep(skip_seconds)
                skip_seconds *= 2
                if skip_seconds > 600:
                    skip_seconds = 600

        # done: remove
        # self.socket.setblocking(0)

        # done: skip sock_file, await send, await get_line
        # We want sock_file for readline().
        # self.sock_file = self.socket.makefile()
        self.debug_print("Connected.", 1)
        await self.send(f"USER {self.nickname} 0 * :Experimental bot.")
        await self.get_line(2)
        await self.send(f"NICK {self.nickname}")
        await self.get_line(2)
        await self.send(f"PRIVMSG NickServ :IDENTIFY {self.nickname} "
                        f"{self.password}")
        await self.get_line(2)
        await self.send(f"JOIN {channel}")
        await self.get_line(2)

    def debug_print(self, text, level):
        """
        Print a debugging message, but only when in debug mode.
        """
        if level < 0:
            level = 0
        elif level > 5:
            level = 5

        if self.debug_level >= level:
            print("IRC[%d] %s%s" % (level, "   " * (level - 1), text))

    # done: async
    async def send(self, msg):
        """
        Low level function which sends a message to the socket.
        """
        msg = msg.rstrip() + "\r\n"
        # done: writer.write
        #self.socket.send(bytearray(msg + "\r\n", "utf-8"))
        self.writer.write(msg.encode())
        self.debug_print("-> " + msg.rstrip(), 1)

    # done: async
    async def privmsg(self, channel, msg):
        """
        Send a PRIVMSG to a channel or user.
        """
        # done: await
        await self.send(f"PRIVMSG {channel}: {msg}")

    async def make_operator(self, channel, user):
        """
        Make user an operator on channel. Only works if the bot is
        already an operator.
        """
        # done: await
        await self.send("MODE %s +o %s" % (channel, user))

    async def join_channel(self, channel):
        """
        Have the bot join a channel.
        """
        # done: await
        await self.send("JOIN " + channel)

    async def get_line(self, timeout=10):
        """
        Low level function which reads one line from the server.
        If the timeout is reached, None is returned instead. get_msg() is a
        higher level function which returns a parsed output.
        """
        # inputs = [self.socket]
        # outputs = []

        # readable, writable, exceptional = select.select(inputs,
        #                                                 outputs,
        #                                                 inputs,
        #                                                 timeout)

        # if self.socket not in readable:
        #     # Our socket never became readable, which means we got
        #     # here because select timed out (see the timeout var).
        #     return None

        # line = self.sock_file.readline().strip()
        line = await self.reader.readline()
        line = line.decode().strip()

        self.debug_print("<- " + line, 1)

        if line.startswith("PING "):
            # The server has sent us a PING to see if we're still
            # alive and connected. We must respond with a PONG, or
            # the server will disconnect us.
            await self.send("PONG " + line.split()[1] + "\r\n")
            return None

        return line

    async def get_msg(self, timeout=10):
        """
        Higher level function than get_line(). get_msg() returns a
        IRCMsg object.

        Returns: IRCMsg object
        """

        line = await self.get_line(timeout)
        
        return self.parse_irc_msg(line)

    def route_msg(self, timeout=10):
        """
        Even higher level function than get_msg(). route_msg() reads a
        message (if one arrives within the timeout, in seconds), and
        routes it to the correct "on_*" function. For example, if the
        message is a private message, it will be sent to the
        "on_private_msg()" function. These functions, the names of
        which start with "on_", can be overridden by an application
        which inherits this class. That application then calls
        route_msg(), and as a result, its own on_* functions will be
        called.

        Returns: IRCMsg object if a message was routed within the
        timeout, otherwise None.
        """

        msg = self.get_msg(timeout)

        if not msg:
            return None

        # sender = msg.sender
        msg_type = msg.msg_type
        channel = msg.channel
        # msg_text = msg.msg_text

        if msg_type == "JOIN":
            self.on_join_msg(msg)

        elif msg_type == "PART":
            self.on_part_msg(msg)

        elif msg_type == "PRIVMSG" and \
                channel.lower() == self.nickname.lower():
            self.on_private_msg(msg)

        elif msg_type == "PRIVMSG":
            self.on_channel_msg(msg)

        else:
            return None

        return msg

    def parse_irc_msg(self, line):

        """
        Low level IRC protocol parsing function.

        Returns: IRCMsg object
        """

        sender = None
        msg_type = None
        channel = None
        msg_text = None

        if not line:
            return None

        match = re.search("^:([^!]*)!"
                          "[^ ]* ([^ ]+) "
                          "([^ ]+) ?"
                          "(:(.*))?$", line)

        if match:
            sender = match.group(1)
            msg_type = match.group(2)
            channel = match.group(3)
            msg_text = match.group(5)

        if sender:
            self.debug_print("SENDER:    '%s'" % sender,   2)

        if msg_type:
            self.debug_print("MSG_TYPE:  '%s'" % msg_type, 2)

        if channel:
            self.debug_print("CHANNEL:   '%s'" % channel,  2)

        if msg_text:
            self.debug_print("MSG_TEXT:  '%s'" % msg_text, 2)

        return IRCMsg(sender, msg_type, channel, msg_text)

    def on_channel_msg(self, msg):
        """
        Called by route_msg() if the message is a channel message.
        This method is meant to be overridden.
        """
        self.debug_print("on_channel_msg(): Unimplemented.", 2)

    def on_private_msg(self, msg):
        """
        Called by route_msg() if the message is a private message.
        This method is meant to be overridden.
        """
        self.debug_print("on_private_msg(): Unimplemented.", 2)

    def on_join_msg(self, msg):
        """
        Called by route_msg() if the message is a join message (that
        is, if someone joins a channel).
        This method is meant to be overridden.
        """
        self.debug_print("on_join_msg(): Unimplemented.", 2)

    def on_part_msg(self, msg):
        """
        Called by route_msg() if the message is a part message (that
        is, if someone leaves a channel).
        This method is meant to be overridden.
        """
        self.debug_print("on_part_msg(): Unimplemented.", 2)


class IRCMsg:

    def __init__(self, sender=None, msg_type=None, channel=None,
                 msg_text=None):

        self.sender = sender
        self.msg_type = msg_type
        self.channel = channel
        self.msg_text = msg_text

    def __repr__(self):
        return "IRC message from %s of type %s on channel %s with " \
            "text '%s'." % (str(self.sender),
                            str(self.msg_type),
                            str(self.channel),
                            str(self.msg_text))
