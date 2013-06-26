#!/usr/bin/env python
import sys
from Color import Color


class Interface:
    def __init__(
            self,
            debuglevel=1,
            debugout="stderr",
            errorout="stderr",
            codepage="UTF-8",
            errorcolor=Color(fgcode='red'),
            debugcolor=Color(fgcode='blue')
    ):
        self.debuglevel = debuglevel
        self.debugout = debugout
        self.errorout = errorout
        self.codepage = codepage
        self.offsetchar = "  "
        self.errorcolor = errorcolor
        self.debugcolor = debugcolor

    def out(self, output, message, color=None):
        """
        Message output
        """
        message = message.encode(self.codepage)
        if color:
            message = color(message)
        if output == "stderr":
            sys.stderr.write(message + "\n")
        elif output == "stdout":
            sys.stdout.write(message + "\n")
        else:
            print "to file: ", output, message

    def fill(self, message, width):
        """
        Fill string into column with width
        """
        if type(message) != unicode:
            message = message.decode('UTF-8')
        message = message.ljust(width)[0:width]
        return message

    def debug(self, message, level=1, offset=0):
        """
        Output debug messages
        """
        color = self.debugcolor
        level = int(level)
        offset = int(offset)

        if not offset:
            offset = level

        if level <= self.debuglevel:
            if type(message) != unicode:
                message = str(message).decode('UTF-8')
            message = offset * self.offsetchar + message
            self.out(self.debugout, message, color)

    def error(self, message, code=0):
        """
        Output error messages
        """
        color = self.errorcolor
        if type(message) != unicode:
            message = str(message).decode('UTF-8')
        self.out(self.errorout, message, color)
        if int(code) > 0:
            sys.exit(code)
