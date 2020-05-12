

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
    import simpleTerminal
    
    def __init__(
        self,
        display,
        displayXpixels, displayYpixels, # display size in pixels
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
        self.fontW, self.fontH = self.font.get_bounding_box()

        from math import floor
        
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

    def deinit_display(self):
        self.display.show(None)

    def write(self, text):
        if self.cursorY==self.statusRow: # the text is to be written on the status row
            writeToTerminal(self.statusTerminal, text) 
        else:
            writeToTerminal(self.mainTerminal, text) 

    def setCursor(self, column, row):
        self.cursorX=column
        self.cursorY=row

        if self.cursorY==self.statusRow: # if the cursor is on the status row, turn on the status cursor
            self.statusTerminal.cursorOn() ##
            self.statusTerminal.setCursor(column,row)
        else: # cursor is in the mainTerminal
            self.statusTerminal.cursorOff() #  turn off the status cursor
            self.mainTerminal.setCursor(column,row) # set the cursor in the mainTerminal
 
    def writeToTerminal(self, terminal, text):
        # This writes text to a selected terminal (the mainTerminal or the statusTerminal)
        #
        # First decode and process any special characters (EOL, backspace, newline, etc.)
        #   This handles a set of commands from robert-hh/Micropython-editor
        #
        # commands to consider handling
        # "\b" backspace
        # hilite function (?) - pass
        # mouse functions
        terminal.write(text)

    def cursorOff(self): # changes cursor for the mainTerminal only
        self.mainTerminal.cursorOff()

    def cursorOn(self): # changes cursor for mainTerminal only
        self.mainTerminal.cursorOn()

    def scrollUp(self, count):
        self.display.auto_refresh=False
        for i in range(count):
            self.mainTerminal.scrollUp()
        self.display.auto_refresh=True

    def scrollDown(self, count):
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
        return totalScreenSize
        

                

