#!/usr/bin/python3
"""
SimpleMenu.py
Provides an easy-to-use interface for creating menus with the Curses library.
"""

import curses
import os

class Menu(object):
    """Main object to represent the menu screen. `show` method shows the menu
    and returns the user's choice."""
    def __init__(self, *names, title=None, subtitle=None):
        self.title = title
        self.subtitle = subtitle
        # Setup a window object etc., misc Curses stuff.
        self.stdscr = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        curses.cbreak()  # No need for [Return]
        curses.noecho()  # Stop keys being printed
        curses.curs_set(0)  # Invisible cursor
        self.stdscr.keypad(True)
        self.stdscr.clear()
        self.stdscr.border(0)
        width = os.get_terminal_size().columns
        width -= 2  # Compensate for border

        # Setup color pairs
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)

        # Setup background
        self.stdscr.bkgd(' ', curses.color_pair(1))

        # Y position makes the menu centered vertically
        global y_pos
        y_pos = (self.stdscr.getmaxyx()[0] - len(names)) // 2

        # Get y position for title
        if self.title is not None:
            # 3 lines above menu items
            if len(self.title) > width:
                self.title = self.title[:width - 3] + "..."
            pad = 3 if self.subtitle else 2
            self.y_pos_title = y_pos - pad
            screen_width = self.stdscr.getmaxyx()[1]
            self.x_pos_title = (screen_width - len(self.title)) // 2

        if self.subtitle is not None:
            if len(self.subtitle) > width:
                self.subtitle = self.subtitle[:width - 3] + "..."
            # 1 line below self.title
            self.y_pos_subtitle = self.y_pos_title + 1
            self.x_pos_subtitle = (self.stdscr.getmaxyx()[1]
                                   - len(self.subtitle)) // 2

        # Create list of menu items
        self.menu_items = []
        for name in names:
            self.menu_items.append(MenuItem(name, self.stdscr))


    def clear_display(self):
        """Clear the screen and restore terminal state to normal."""
        curses.nocbreak()
        curses.echo()
        curses.curs_set(1)
        self.stdscr.keypad(False)
        self.stdscr.clear()
        curses.endwin()


    def draw(self):
        """Draw out each item on menu, with highlighting."""
        if self.title:
            self.stdscr.addstr(self.y_pos_title,
                               self.x_pos_title,
                               self.title,
                               curses.A_BOLD)
        if self.subtitle:
            self.stdscr.addstr(self.y_pos_subtitle,
                               self.x_pos_subtitle,
                               self.subtitle)
        for item in self.menu_items:
            self.stdscr.addstr(item.y_pos,
                               item.x_pos,
                               item.name,
                               item.attr)
        self.stdscr.refresh()


    def show(self):
        """Display the menu, and return the user's choice (or None)."""
        try:
            # Initially select first item on the menu.
            selected_item = 0
            self.menu_items[selected_item]._select()
            # Draw out the menu.
            self.draw()
            while True:
                # Get the user's input.
                user_key = self.stdscr.getkey()
                if user_key == "KEY_UP" and selected_item > 0:
                    # Go up one menu item if not already at the top.
                    self.menu_items[selected_item]._deselect()
                    selected_item -= 1
                    self.menu_items[selected_item]._select()
                    self.draw()
                elif (user_key == "KEY_DOWN"
                      and selected_item < len(self.menu_items) - 1):
                    # Go down one menu item if not already at the bottom.
                    self.menu_items[selected_item]._deselect()
                    selected_item += 1
                    self.menu_items[selected_item]._select()
                    self.draw()
                elif user_key == "\n":
                    # User pressed enter, return choice.
                    self.clear_display()
                    return self.menu_items[selected_item].name        
                elif user_key == "q":
                    self.clear_display()
                    # quit()
                    return None  # Handle this in program.
        except KeyboardInterrupt:
            # Don't throw an error, clear_display() restores terminal state.
            pass

        self.clear_display()


class MenuItem(object):
    """Base object for each menu item. Allows selection and text editing."""
    def __init__(self, name, stdscr):
        self.name = name
        global y_pos
        self.y_pos = y_pos
        y_pos += 1  # Put each item on a new line.
        maxyx = stdscr.getmaxyx()
        # Horizontally center-justify each line.
        self.x_pos = (maxyx[1] - len(self.name)) // 2
        self.attr = curses.A_NORMAL
    def _select(self):
        # Highlight text.
        self.attr = curses.A_REVERSE
    def _deselect(self):
        # Undo highlight text.
        self.attr = curses.A_NORMAL

