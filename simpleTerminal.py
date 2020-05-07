
#######################
# simpleTerminal.py
# 7 May 2020 Kevin Matocha - kmatch98
#
# (C) Copyright 2020, Kevin Matocha
#
##############################

# How to use:
# myTerminal=simpleTerminal(rows=17, columns=40) (for a 240x240 display using terminalio.FONT)
# Setup a display using displayio and your hardware display driver.
# Create an instance of simpleTerminal, you must tell it the number of text
# rows and columns.
# Default font used is terminalio.FONT.
# You can get a font's size in pixels using "fontPixelWidth, fontPixelHeight = terminalio.FONT.get_bounding_box()"
#
# An example:
# Add the .displayGroup to a group, and then add your group to the display,
# Here is an example from the python editor (pye_mp.py) that was updated
# to use simpleTerminal to manage the main text and the status line.
#
# self.g=displayio.Group(max_size=2, scale=1) # create a group
# Editor.display.show(self.g) # add the group to the display
# self.g.append(self.mainTerminal.displayGroup) # add the first terminal's displayGroup to my main group
# self.g.append(self.statusTerminal.displayGroup) # add the second terminal's displayGroup to my main group
#
# Original source for pye_mp Micropython-Editor can be found here:
#     https://github.com/robert-hh/Micropython-Editor

# Functions

#######
# Scrolling hints:
#
# When calling for scrolling, it will display faster if you turn
# off the display's auto-refresh. Then you can turn auto_refresh
# back on after you are done scrolling.
#
# for example:
#            Editor.display.auto_refresh=False
#            for i in range(0, scrolling):
#                self.mainTerminal.scrollUp()
#            Editor.display.auto_refresh=True
#

# To Do:
# Maybe the class should take the display as an input
#
# Add highlighted text
# My current thoughts on how to achieve.
# Make three text layers.
# Bottom layer has black background and white letters and displays all the text
# Middle layer has two items in the bitmap, one transparent square and one "highlight" color square.
#   - This has "highlight" entries in the tilegrid only for the highlighted text.
# Top layer has clear background and black text.  It only contains text entries in the tilegrid for highlighted text
#    - (same as the middle layer).


import displayio
import terminalio


class simpleTerminal:
    def __init__(
        self,
        rows,
        columns,
        font=terminalio.FONT,
        bgColor=0x000000,  # black background
        textColor=0xFFFFFF,  # white text
        x=0, # pixel position of the terminal with the parent.
        y=0, # pixel position of the terminal with the parent.
        cursorX=0, # initial row position of the cursor
        cursorY=0, # initial row position of the cursor
        cursorDisplay=True,
        cursorWhileScrolling=False,
    ):
        # Define the instance variables
        self.rows = rows
        self.columns = columns
        self.font = font
        self.bgColor = bgColor
        self.textColor = textColor
        self.xPixels = x  # pixel position within the parent
        self.yPixels = y  # pixel position within the parent
        self.cursorX = cursorX
        self.cursorY = cursorY
        self.cursorDisplay = (
            cursorDisplay
        )  # should the cursor be displayed?  If false, it never is shown
        self.cursorWhileScrolling = (
            cursorWhileScrolling
        )  # if True, keep cursor highlighted while scrolling

        self.cursorStatus = (
            False
        )  # For cursor blinking, this shows when the cursor status is "on"

        self.fontW, self.fontH = self.font.get_bounding_box()

        # Calculate the pixel dimensions for the terminal window
        self.pixelWidth = (
            self.fontW * self.columns
        )  # the pixel width of the terminal window (in units of pixels)
        self.pixelHeight = (
            self.fontH * self.rows
        )  # the pixel height of the terminal window (in units of pixels)

        self.blankGlyph = self.font.get_glyph(
            ord(" ")
        ).tile_index  # this is the font glyph for a blank space
        # do we need to be sure that no one changes the font after creating the instance?

        self.palette = displayio.Palette(2)
        self.palette[0] = bgColor
        self.palette[1] = textColor

        self.tilegrid = displayio.TileGrid(
            bitmap=self.font.bitmap,
            pixel_shader=self.palette,
            x=self.xPixels,
            y=self.yPixels,
            width=self.columns,
            height=self.rows,
            tile_width=self.fontW,
            tile_height=self.fontH,
        )

        # highlight color for the cursor is the swap of the standard colors
        self.bgHighlightColor = self.textColor  # Swap the colors as default
        self.textHighlightColor = self.bgColor  # Swap the colors as default

        self.cursorpalette = displayio.Palette(2)
        self.cursorColorReset()

        self.cursortilegrid = displayio.TileGrid(
            bitmap=self.font.bitmap,
            pixel_shader=self.cursorpalette,
            x=self.xPixels,
            y=self.yPixels,
            width=1,
            height=1,
            tile_width=self.fontW,
            tile_height=self.fontH,
        )

        self.displayGroup = displayio.Group(max_size=2, scale=1, x=0, y=0)
        self.displayGroup.append(self.tilegrid)  ### temporarily commented for debug!!!!!  ****
        if self.cursorDisplay:
            self.cursorOn()  # if the cursor is to be displayed, then add it to the group.

    #    def clamp(self, n, minn, maxn): # if you want to constrain the cursor position
    #        return max(min(maxn, n), minn)

    def setCursor(self, column, row):
        # There are no constraints put on the cursor position.
        # Note: if cursor is off the screen, the function writeChar does not do anything.
        # self.cursorX = self.clamp(column, 0, self.columns - 1)  # if you want to constrain
        # self.cursorY = self.clamp(row, 0, self.rows - 1)# if you want to constrain
        # print( "cursorX: {}, cursorY: {}".format(self.cursorX, self.cursorY) )  # for debug
        self.cursorX = column
        self.cursorY = row

        # this sets the cursor tile grid position to the right location on the display
        self.cursortilegrid.x = self.cursorX * self.fontW
        self.cursortilegrid.y = self.cursorY * self.fontH
        self.writeCursorChar()

    def writeCursorChar(self):
        # This ensures that the cursor shows the same character as the main terminal

        # ensure that the cursor is in the terminal boundaries
        if (0 <= self.cursorX < self.columns) and (0 <= self.cursorY < self.rows):
            self.cursortilegrid[0, 0] = self.tilegrid[self.cursorX, self.cursorY]
            # print("writeCursor!")

    def cursorColorReset(self):
        # sets the color back to the original values, useful when cursorColorChange is used and last color is uncertain
        self.cursorpalette[0] = self.bgHighlightColor
        self.cursorpalette[1] = self.textHighlightColor

    def cursorColorChange(self):  # alternates the color of the cursor
        tempColor = self.cursorpalette[0]
        self.cursorpalette[0] = self.cursorpalette[1]
        self.cursorpalette[1] = tempColor
        self.cursortilegrid.pixel_shader = self.cursorpalette

    def cursorOff(self):  # to turn the cursor off, such as during scrolling
        if self.cursorDisplay and self.cursorStatus:
            #    print("Prepop! {}".format(len(self.displayGroup)))
            self.displayGroup.pop(i=-1)
            #    print("Popped! {}".format(len(self.displayGroup)))
            self.cursorStatus = False

    def cursorOn(self):
        if self.cursorDisplay and self.cursorStatus == False:
            self.displayGroup.append(self.cursortilegrid)
            self.cursorStatus = True
            # writeCursorChar()

    def writeChar(self, char):
        # if the cursor is out of the terminal boundaries, do nothing
        if (0 <= self.cursorX < self.columns) and (0 <= self.cursorY < self.rows):
            thisGlyph = self.font.get_glyph(
                ord(char)
            )  # get the glyph for the character
            # print("{} x: {} y: {} glyph: {}".format(char,self.cursorX, self.cursorY, thisGlyph.tile_index) ) # for debug

            # update the tile at the current cursor position
            if thisGlyph.tile_index != None:  # verify that a glyph was returned
                self.tilegrid[self.cursorX, self.cursorY] = thisGlyph.tile_index
                self.setCursor(self.cursorX + 1, self.cursorY)

    def write(
        self, text
    ):  # based on: circuitpython/shared-module/terminalio/Terminal.c from github
        for char in text:
            if ord(char) < 128:
                if (ord(char) >= 0x20) and (ord(char) <= 0x7E):
                    self.writeChar(char)

                # Some of the VT100 code is missing here from Terminal.c ****
                # Add carriage return \r
                elif char == "\r":
                    self.setCursor(0, self.cursorY)
                # Add newline \n
                elif char == "\n":
                    self.setCursor(self.cursorX, self.cursorY + 1)

                # Add backspace \b
                elif char == "\b":
                    self.setCursor(self.cursorX - 1, self.cursorY)
                    # this should also write a space at the current location
                    self.writeBlank(self.cursorX, self.cursorY)
                    #self.setCursor(self.cursorX - 1, self.cursorY)  #*****

            else:
                self.writeChar(char)

    def writeBlank(self, column, row):
        # This writes a blank space at a given
        self.tilegrid[column, row] = self.blankGlyph
        #self.cursorX=self.cursorX+1  ##****

    def scrollUp(self):
        # move everything down, copying from the bottom up
        if self.cursorWhileScrolling == False:
            self.cursorOff()
        for row in range(self.rows - 1, 0, -1):
            for column in range(0, self.columns):
                self.tilegrid[column, row] = self.tilegrid[column, row - 1]

        # set the first row to blank
        for column in range(0, self.columns):
            self.writeBlank(column, 0)
        self.setCursor(self.cursorX, self.cursorY + 1)
        if self.cursorWhileScrolling == False:
            self.cursorOn()

    def scrollDown(self):
        # move everything down, copying from the bottom up
        if self.cursorWhileScrolling == False:
            self.cursorOff()
        for row in range(0, self.rows - 1):
            for column in range(0, self.columns):
                self.tilegrid[column, row] = self.tilegrid[column, row + 1]

        # set the first row to blank
        for column in range(0, self.columns):
            self.writeBlank(column, self.rows - 1)

        self.setCursor(self.cursorX, self.cursorY - 1)
        if self.cursorWhileScrolling == False:
            self.cursorOn()
        # check scrolling max column to make sure that it scrolls properly even for filled lines to end of the line display

    def clearEOL(self):
        if (self.cursorX < self.columns) and (self.cursorY < self.rows):  # only do something if the cursor position is within the display bounds
            for column in range(self.cursorX, self.columns):
                self.writeBlank(column, self.cursorY)

    def clearAll(self):
        for row in range(0, self.rows):
            for column in range(0, self.columns):
                self.writeBlank(column, row)


