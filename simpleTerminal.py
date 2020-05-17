
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
            self.displayGroup.pop(i=-1)
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


class editorTerminal:

# input variables
# pixelsX, pixelsY - display size
# rows,columns (default calculate based on font size)
# font
# bgColor
# textColor
#
#
# cursorDisplay=True # only applies to the mainTerminal
# cursorWhileScrolling=False

#
# class variables
# statusRow # the y-position of the status row
#
# handle special characters
# depending upon cursor location:
#       ->write to either the mainTerminal or the statusTerminal

# if setCursor=statusRow, then do all the editing in the statusTerminal
# otherwise, act on the mainTerminal

# Questions: Do we want to turn cursor on when editing the status row?
# Maybe can just turn on when the cursor is on the statusRow.
    import terminalio, displayio

    def __init__(
        self,
        display,
        displayXPixels, displayYPixels, # display size in pixels
        rows=None,
        columns=None,
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
        self.display=display
        self.font=font
        fontW, fontH = self.font.get_bounding_box()

        from math import floor
        from simpleTerminal import simpleTerminal

        if rows==None:
            self.displayRows=floor(displayYPixels/fontH) # total display rows (main and status)
        if columns==None:
            self.displayColumns=floor(displayXPixels/fontW)
        self.statusRow=self.displayRows-1 # This is the row that houses the highlighted status row
        self.bgColor=bgColor
        self.textColor=textColor
        self.x=x
        self.y=y
        self.cursorX=cursorX
        self.cursorY=cursorY
        self.cursorDisplay=cursorDisplay
        self.cursorWhileScrolling=cursorWhileScrolling



        ########
        # instance the two terminals
        #
        # Instance the main terminal (subtract one row from total for status terminal)
        self.mainTerminal=simpleTerminal(rows=self.displayRows-1,columns=self.displayColumns, # subtract one row for the status row
                                         x=self.x, y=self.y,
                                         textColor=self.textColor, bgColor=self.bgColor,
                                         font=self.font,
                                         cursorDisplay=self.cursorDisplay,
                                         cursorWhileScrolling=cursorWhileScrolling)

        # Instance the status terminal, cursorDisplay is OFF
        yStatusLine=self.mainTerminal.pixelHeight+1 # the status line y-position is just below the upper main terminal
        self.statusTerminal=simpleTerminal(rows=1,columns=self.displayColumns,
                                           x=self.x, y=yStatusLine,
                                           textColor=self.bgColor, bgColor=self.textColor, # swap the color palette versus the main terminal
                                           cursorDisplay=False,
                                           cursorWhileScrolling=False)


        self.displayGroup=displayio.Group(max_size=2, scale=1) # this holds the display terminals for displayio
        self.displayGroup.append(self.mainTerminal.displayGroup)
        self.displayGroup.append(self.statusTerminal.displayGroup)

        self.display.auto_refresh=True  # ensure display auto refreshes
        self.display.show(self.displayGroup) # add group to the display
                                            #  Do we need to clear any other groups from the display?

    def deinit_display(self):
        self.display.show(None)

    def writeToTerminal(self, thisTerminal, text):
        # This writes text to a selected terminal (the mainTerminal or the statusTerminal)
        #
        # First decode and process any special characters (EOL, backspace, newline, etc.)
        #   This handles a set of commands from robert-hh/Micropython-editor
        #
        # commands to consider handling
        # "\b" backspace
        # hilite function (?) - pass
        # mouse functions

        # Handle the following commands (from robert-hh/Micropython-Editor)

##########ifdef VT100
##    if termcap_vt100:
        TERMCAP = (  ## list of terminal control strings
            "\x1b[{row};{col}H",    ## 0: Set cursor
            "\x1b[0K",              ## 1: Clear EOL
            "\x1b[?25h",            ## 2: Cursor ON
            "\x1b[?25l",            ## 3: Cursor OFF
            "\x1b[0m",              ## 4: Hilite 0 - normal text
            "\x1b[1;37;46m",        ## 5: Hilite 1 - Entering the status line
            "\x1b[43m",             ## 6: Hilite 2 - Highlighting Text
            '\x1b[?9h',             ## 7: Mouse reporting on
            '\x1b[?9l',             ## 8: Mouse reporting off
            "\x1bM",                ## 9: Scroll one line up
            "\n",                   ## 10: Scroll one line down
            '\x1b[1;{stop}r',       ## 11: Set lowest line of scrolling range
            '\x1b[r',               ## 12: Scroll the full screen
            '\x1b[999;999H\x1b[6n', ## 13: Report Screen size command
                                    ## 14: Status line format. Elements may be omitted
            "{chd}{file} Row: {row}/{total} Col: {col}  {msg}",
            "\b"                    ## 15: backspace one character, used in line_edit
        )
############

        # This may need to parse the input text in sections, in case multiples are sent ***
        if text[:1]=="\x1b":# escape character
            #print('found escape char')
            if text[-1] == "H": ## 0: Set cursor
                # get row, col  ****
                row,col=text[2:-1].split(';',1) # split into max of two pieces
                self.setCursor( int(col)-1, int(row)-1 ) # col, row
            elif text == TERMCAP[1]: ## 1: Clear EOL
                thisTerminal.clearEOL()
            elif text == TERMCAP[2]: ## Cursor ON
                thisTerminal.cursorOn()
            elif text == TERMCAP[3]: ## Cursor OFF
                thisTerminal.cursorOff()
            elif text == TERMCAP[4]: ## 4: Hilite 0 - normal text
                pass # not available at this time
            elif text == TERMCAP[5]: ## 5: Hilite 1 - Entering the status line
                pass # not available at this time
            elif text == TERMCAP[6]: ## 6: Hilite 2 - Highlighting Text
                pass # not available at this time
            elif text == TERMCAP[7]: ## 7: Mouse reporting on
                pass # not available at this time
            elif text == TERMCAP[8]: ## 8: Mouse reporting on
                pass # not available at this time
            elif text == TERMCAP[9]: ## 9: Scroll one line up
                thisTerminal.scrollUp()
                                    ## 10: newline handled below

            elif text[-1]=="r":  ## 11/12 - Set scrolling options
                pass # not necessary for external display

                                    ## 13: Report Screen size command
                                    ## Use editorTerminal.getScreenSize()

                                    ## 15: backspace one character
                                    ## \b backspace handled by simpleTerminal.write()

        elif text == TERMCAP[10]: ## 10: Scroll one line down
            thisTerminal.scrollDown()
        else:
            thisTerminal.write(text)

    def write(self, text):
        if self.cursorY==self.statusRow: # the text is to be written on the status row
            #print('\nstatusTerminal\n\nwriting: ',text)
            self.writeToTerminal(self.statusTerminal, text)
        else:
            self.writeToTerminal(self.mainTerminal, text)

    def setCursor(self, column, row):
        self.cursorX=column
        self.cursorY=row

        if self.cursorY==self.statusRow: # if the cursor is on the status row, turn on the status cursor
            self.statusTerminal.cursorOn() ##
            self.statusTerminal.setCursor(column,0)
        else: # cursor is in the mainTerminal
            self.statusTerminal.cursorOff() #  turn off the status cursor
            self.mainTerminal.setCursor(column,row) # set the cursor in the mainTerminal

    def cursor(self, onoff):
        if onoff:
            self.cursorOn()
        else:
            self.cursorOff()

    def cursorOff(self): # changes cursor for the mainTerminal only  *** double check
        self.mainTerminal.cursorOff()

    def cursorOn(self): # changes cursor for mainTerminal only *** doublecheck
        self.mainTerminal.cursorOn()

    def scrollUp(self, count=1):
        self.display.auto_refresh=False
        for i in range(count):
            self.mainTerminal.scrollUp()
        self.display.auto_refresh=True

    def scrollDown(self, count=1):
        self.display.auto_refresh=False
        for i in range(count):
            self.mainTerminal.scrollDown()
        self.display.auto_refresh=True

    def clearEOL(self):
        self.display.auto_refresh=False
        if self.cursorY==self.statusRow: # if the cursor is on the status row
            self.statusTerminal.clearEOL()
        else:
            self.mainTerminal.clearEOL()
        self.display.auto_refresh=True

    def clearAll(self):
        if self.cursorY==self.statusRow: # if the cursor is on the status row,
            self.statusTerminal.clearAll()
        else:
            self.mainTerminal.clearAll()

    def getScreenSize(self):
        totalScreenSize=[self.mainTerminal.rows+self.statusTerminal.rows, self.mainTerminal.columns]
        #print( 'rows: {} columns: {}'.format(totalScreenSize[0], totalScreenSize[1]) ) # for debug
        return totalScreenSize # rows, columns




