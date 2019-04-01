#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import curses
import curses.textpad
import zmq
import select


context = zmq.Context()
publisher = context.socket(zmq.PUB)
publisher.connect("ipc://./.log.sock")


def z_log(text):
    publisher.send_multipart([b"LOG", str(text).encode()])


class Console:
    def __init__(self, stdscr):

        self._stop = False

        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_GREEN)
        # curses.curs_set(False)

        self.stdscr = stdscr
        y, x = stdscr.getmaxyx()
        z_log("stdscr: {}x{}".format(x, y))

        self.win_messages = curses.newwin(curses.LINES - 1, curses.COLS)
        self.win_prompt = curses.newwin(1, curses.COLS - 5, curses.LINES - 1, 5)
        self.win_state = curses.newwin(5, curses.COLS, curses.LINES - 1, 0)

        self.win_messages.bkgd(" ", curses.color_pair(1))
        self.win_prompt.bkgd(" ", curses.color_pair(2))
        self.win_state.bkgd(" ", curses.color_pair(3))

        self.win_state.addstr("  0> ")
        self.win_state.refresh()
        self.win_prompt.refresh()

        self.win_prompt.nodelay(True)

        self.win_messages.scrollok(True)
        self.win_messages.idlok(True)

        self.edit = curses.textpad.Textbox(self.win_prompt, insert_mode=True)

        self.win_prompt.keypad(True)
        self.win_prompt.move(0, 0)

        self.history = [""]
        self.history_index = 0

    def stop(self):
        return self._stop

    def msg(self, text):
        y, x = self.win_prompt.getyx()
        self.win_messages.addstr("\n{}".format(text))
        self.win_prompt.move(y, x)
        self.win_messages.refresh()
        self.win_prompt.refresh()

    def do_command(self):
        key = self.win_prompt.getch()
        if key == -1:
            return

        if key == ord("@") or key == curses.ascii.EOT:
            self._stop = True
            return

        if key == curses.KEY_RESIZE or key == curses.ascii.FF:
            curses.update_lines_cols()
            z_log("resize {}x{}".format(curses.COLS, curses.LINES))
            self.win_messages.refresh()
            self.win_prompt.refresh()
            self.win_state.refresh()
            return

        if key == 10:
            cmd = self.edit.gather().strip()
            z_log("edit " + cmd)
            self.win_prompt.erase()

            if cmd != "":
                self.history[self.history_index] = cmd
                self.history.append("")
                self.history_index += 1
                z_log("command: " + repr(self.history))
                return cmd

        elif key == curses.KEY_UP:
            if self.history_index <= 0:
                # aucune commande mémorisée ou déjà en haut: ne rien faire
                return
            z_log("up")
            self.history_index -= 1

            self.win_prompt.erase()
            self.win_prompt.addstr(0, 0, self.history[self.history_index])

            self.win_state.erase()
            self.win_state.addstr(0, 0, "{:3d}> ".format(self.history_index))
            self.win_state.refresh()

        elif key == curses.KEY_DOWN:
            if self.history_index == len(self.history) - 1:
                # aucune commande mémorisée ou en bas: ne rien faire
                return
            self.history_index += 1
            z_log("down")
            self.win_prompt.erase()
            self.win_prompt.addstr(0, 0, self.history[self.history_index])

            self.win_state.erase()
            self.win_state.addstr(0, 0, "{:3d}> ".format(self.history_index))
            self.win_state.refresh()

        else:
            z_log("key: 0x{:x}".format(key))

            y, x = self.win_prompt.getyx()
            self.win_messages.addstr("\nkey pressed 0x{:x}".format(key))
            self.win_prompt.move(y, x)
            self.win_messages.refresh()

            if key == curses.ascii.DEL:  # ⌫
                key = curses.KEY_BACKSPACE
            elif key == curses.KEY_DC:  # ⌦
                key = curses.ascii.EOT

            if self.edit.do_command(key):
                self.win_prompt.refresh()


def run_console(loop):
    curses.wrapper(lambda stdscr: loop(Console(stdscr)))


def loop(console):
    now = time.time()
    count = 0

    while not console.stop():
        o, _, _ = select.select([0], [], [], 0.01)

        if 0 in o:
            cmd = console.do_command()
            if cmd:
                if cmd.lower() == "quit":
                    break
                console.msg("commande: {}".format(cmd))

        if time.time() >= now + 0.5:
            now = time.time()
            count += 1
            console.msg("coucou {} @ {}".format(count, now))

    z_log("sortie")


if __name__ == "__main__":
    run_console(loop)
