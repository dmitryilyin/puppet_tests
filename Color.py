#!/usr/bin/env pyton
#
# 8 colors mode
# 30 - 37 - Foreground color codes
# 40 - 47 - Background color codes
# 0 - 9 - Special Attributes
#
# 16 colors mode
# color + 60 = 'bright' version
#
# 256 Colors mode (not supported by this module)
# 38;5;ColorNumber - 256 color mode Foreground
# 48;5;ColorNumber - 256 color mode Background
# ColorNumber - 1 - 256 color code


class Color:
    """
    This class is used for coloring terminal output of Python programs
    """
    def __init__(self, fgcode=None, bgcode=None, attrcode=0, enabled=True, brightfg=False, brightbg=False):
        """
        Constructor. Can take color settins when creating class.
        """
        self.start = "\033["
        self.end = "m"
        self.reset = self.start + "0" + self.end

        if enabled:
            self.enabled = True
        else:
            self.enabled = False

        if brightfg:
            self.brightfg = True
        else:
            self.brightfg = False

        if brightbg:
            self.brightbg = True
        else:
            self.brightbg = False

        self.fgoffset = 30
        self.bgoffset = 40
        self.brightoffset = 60

        self.colortable = {
            'black': 0,
            'red': 1,
            'green': 2,
            'yellow': 3,
            'blue': 4,
            'magneta': 5,
            'cyan': 6,
            'white': 7,
            'off': None,
        }

        self.attrtable = {
            'normal': 0,
            'bold': 1,
            'faint': 2,
            'italic':    3,
            'underline': 4,
            'blink': 5,
            'rblink':    6,
            'negative': 7,
            'conceal': 8,
            'crossed':   9,
            'off': 0,
        }

        self.setFG(fgcode)
        self.setBG(bgcode)
        self.setATTR(attrcode)

    def toggleEnabled(self):
        """"
        Toggle enable and disable all colors.
        """
        if self.enabled:
            self.enabled = False
        else:
            self.enabled = True

    def toggleBrightFG(self):
        """
        Toggle enable and disable of bright foreground.
        """
        if self.brightfg:
            self.brightfg = False
        else:
            self.brightfg = True

    def toggleBrightBG(self):
        """
        Toggle enable and disable of bright background.
        """
        if self.brightbg:
            self.brightbg = False
        else:
            self.brightbg = True

    def setFG(self, color):
        """
        Set foreground color or color code.
        """
        if type(color) == int:
            self.fgcode = color
            return True
        if self.colortable.has_key(color):
            self.fgcode = self.colortable[color]
            return True
        self.fgcode = None
        return False

    def setBG(self, color):
        """
        Set background color or color code.
        """
        if type(color) == int:
            self.bgcode = color
            return True
        if self.colortable.has_key(color):
            self.bgcode = self.colortable[color]
            return True
        self.bgcode = None
        return False

    def setATTR(self, color):
        """
        Set additional text attribute code.
        """
        if type(color) == int:
            self.attrcode = color
            return True
        if self.attrtable.has_key(color):
            self.attrcode = self.attrtable[color]
            return True
        self.attrcode = 0
        return False

    def escape(self):
        """
        Print color enabling escape chars.
        """
        vars = []
        attrcode = self.attrcode

        if self.fgcode is not None:
            fgcode = self.fgoffset + self.fgcode
            if self.brightfg:
                fgcode += self.brightoffset
        else:
            fgcode = None

        if self.bgcode is not None:
            bgcode = self.bgoffset + self.bgcode
            if self.brightbg:
                bgcode += self.brightoffset
        else:
            bgcode = None

        vars.append(attrcode)
        if fgcode:
            vars.append(fgcode)
        if bgcode:
            vars.append(bgcode)

        escstr = self.start + ";".join(map(str, vars)) + self.end
        return escstr

    def printChart(self):
        """
        Prints demo color chart tot test terminal support.
        """
        for fg in range(0, 7):
            for bg in range(0, 7):
                for attr in sorted(self.attrtable.values()):
                    democolor = Color(fgcode=fg, bgcode=bg, attrcode=attr, brightfg=False, brightbg=False)
                    print democolor("Hello World!"), repr(democolor)
                    democolor.brightfg = True
                    print democolor("Hello World!"), repr(democolor)
                    democolor.brightbg = True
                    print democolor("Hello World!"), repr(democolor)

    def __str__(self):
        return self.escape()

    def __repr__(self):
        return "Color(fgcode = %d, bgcode = %d, attrcode = %d, enabled = %s, brightfg = %s, brightbg = %s)" % (
            self.fgcode,
            self.bgcode,
            self.attrcode,
            str(self.enabled),
            str(self.brightfg),
            str(self.brightbg),
            )

    def __call__(self, str):
        if self.enabled:
            return self.escape() + str + self.reset
        else:
            return str

if __name__ == '__main__':
    CLR = Color()
    CLR.printChart()
