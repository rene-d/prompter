# prompter

## Description

Example of use of [curses in Python](https://docs.python.org/3/library/curses.html) to implement a command prompt within a console app with a main loop based on [select](https://docs.python.org/3/library/select.html).

A basic logger with [PyZMQ](https://pyzmq.readthedocs.io/en/latest/api/index.html) helps debugging.

Written for Python 3 but still works the legacy Python 2.

![screenshot](screenshot.png)

## TODO

* Manage resize and redraw
* Improve command history
* Add a status line, like [vim](https://www.vim.org)
