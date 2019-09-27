#!/usr/bin/env python3
# pylint: disable=wrong-import-position,arguments-differ

'''GTK front-end for dcparse.'''

import decimal

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk, Gio as gio, Pango as pango

import dcparse


class VisualDC(gtk.Application):
    '''Common application actions.'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, application_id='uk.ac.cam.tw466.vdc',
                         flags=gio.ApplicationFlags.HANDLES_COMMAND_LINE)

        self.window = None
        if self.prefers_app_menu():
            self.set_app_menu(...)
        else:
            # menu bar etc
            pass

    def do_activate(self):
        if not self.window:
            self.window = ApplicationWindow(application=self)
        self.window.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict().end().unpack()
        self.activate()
        return 0


class ApplicationWindow(gtk.ApplicationWindow):
    '''Main application window.'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, title='Visual dc', border_width=5)

        box = gtk.Box(orientation=gtk.Orientation.VERTICAL, spacing=5)
        self.add(box)

        self.stack = DCStack()
        box.pack_end(self.stack, expand=True, fill=True, padding=0)

        code_entry = gtk.TextView(editable=True, cursor_visible=True)
        code_entry.get_buffer().connect('changed', self._on_code_changed)
        box.pack_start(code_entry, expand=True, fill=True, padding=0)

    def _on_code_changed(self, widget):
        cmds = dcparse.CommandSequence(widget.get_text(
            widget.get_start_iter(), widget.get_end_iter(),
            include_hidden_chars=False))
        self.stack.clear()
        try:
            self.stack.run_commands(cmds)
        except dcparse.EmptyStackError as err:
            pass
        except dcparse.UnknownCommandError as err:
            str_position, *_ = err.args


class DCStack(dcparse.Stack, gtk.ListBox):
    '''A ListBox representing a dc stack.'''
    def __init__(self):
        super().__init__()
        gtk.ListBox.__init__(self, selection_mode=gtk.SelectionMode.NONE)
        placeholder = gtk.Label(label='Empty stack')
        self.set_placeholder(placeholder)

    def clear(self):
        for widget in self._stack:
            self.remove(widget)
        super().clear()
        self.show_all()

    def pop(self):
        widget = super().pop()
        self.remove(widget)
        self.show_all()
        return widget.value

    def push(self, *values):
        for value in values:
            widget = StackValue(value)
            self.add(widget)
            super().push(widget)
        self.show_all()


class StackValue(gtk.ListBoxRow):
    '''A ListBoxItem representing a numerical value on the stack.'''
    def __init__(self, value):
        super().__init__()
        self.value = value
        label = gtk.Label(label=str(value), selectable=True)
        label.set_line_wrap(True)
        label.set_line_wrap_mode(pango.WrapMode.CHAR)
        label.set_ellipsize(pango.EllipsizeMode.MIDDLE)
        label.set_lines(3)
        self.add(label)

    def __repr__(self):
        return f'StackValue({self.value!r})'


def main():
    '''Main entry point.'''
    win = ApplicationWindow()
    win.connect('destroy', gtk.main_quit)
    win.show_all()
    gtk.main()


if __name__ == '__main__':
    main()
