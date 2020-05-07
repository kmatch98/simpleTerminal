# simpleTerminal

simpleTerminal:  A CircuitPython class for creating a region of text, that keeps track of the cursor location for text entry.  Also includes capability for a highlighted cursor.

How to use:
myTerminal=simpleTerminal(rows=17, columns=40) (for a 240x240 display using terminalio.FONT)
Setup a display using displayio and your hardware display driver.
Create an instance of simpleTerminal, you must tell it the number of text
rows and columns.
Default font used is terminalio.FONT.
You can get a font's size in pixels using "fontPixelWidth, fontPixelHeight = terminalio.FONT.get_bounding_box()"

An example:
Add the .displayGroup to a group, and then add your group to the display,
Here is an example from the python editor (pye_mp.py) that was updated
to use simpleTerminal to manage the main text and the status line.

self.g=displayio.Group(max_size=2, scale=1) # create a group
Editor.display.show(self.g) # add the group to the display
self.g.append(self.mainTerminal.displayGroup) # add the first terminal's displayGroup to my main group
self.g.append(self.statusTerminal.displayGroup) # add the second terminal's displayGroup to my main group

Original source for pye_mp Micropython-Editor can be found here:
     https://github.com/robert-hh/Micropython-Editor


Scrolling hints:
When calling for scrolling, it will display faster if you turn
off the display's auto-refresh. Then you can turn auto_refresh
back on after you are done scrolling.

For example:
            Editor.display.auto_refresh=False
            for i in range(0, scrolling):
                self.mainTerminal.scrollUp()
            Editor.display.auto_refresh=True

simpleTerminal(
        rows,
        columns,
        font=terminalio.FONT,
        bgColor=0x000000,  # black background
        textColor=0xFFFFFF,  # white text foreground
        x=0, # pixel position of the terminal with the parent.
        y=0, # pixel position of the terminal with the parent.
        cursorX=0, # initial row position of the cursor
        cursorY=0, # initial row position of the cursor
        cursorDisplay=True,
        cursorWhileScrolling=False,
    ):


This class creates a terminal of dimensions (columns, rows) with a two color palette using the specified font.  
cursorDisplay=True: the cursor is visible
cursorWhileScrolling=False: the cursor is turned off while scrolling.


Functions:
- setCursor(column, row)
	Set the cursor entry point to the specified location.  It is perfectly ok to set the cursor outside of the display, but nothing will show when text is added at that location.

- writeCursorChar()
	This is an internal function that creates the (1x1) tile grid for the cursor, so that the letter matches whatever is in the main tile grid.

- cursorColorReset()
	Turns the cursor color back to the default values, used for setting back to the original value.

- cursorColorChange()
	Alternates the color of the cursor by swapping the background and foreground color

- cursorOff()
	Stops displaying the cursor

- cursorOn()
	Turns the cursor display to on

- writeChar(char)
	Adds a character to the terminal at the current cursor position, increments the cursor

- write(text)
	Adds a string to the terminal at the current cursor position.  Also handles newline, carriage return and backspace.

- writeBlank(column, row)
	Writes  blank space at the given location.  Note: This does not update the cursor position.

- scrollUp()
	Scrolls up one line, clearing the line that goes off the display

- scrollDown()
	Scrolls down one line, clearing the line that goes off the display

- clearEOL()
	Clears the current line to the right of the current cursor position

- clearAll()
	Writes blanks into the whole terminal
