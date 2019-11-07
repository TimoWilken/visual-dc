#!/usr/bin/env python3
# pylint: disable=wrong-import-position,arguments-differ

'''GTK front-end for dcparse.'''

import os.path

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk, Gio as gio, Pango as pango

import dcparse


class ApplicationEventHandler:
    def __init__(self, stack):
        self.stack = stack

    def on_destroy_main(self, *_):
        gtk.main_quit()

    def on_change_code(self, widget):
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
    # Needed for gtk.Builder to recognise this class.
    # https://eeperry.wordpress.com/2013/01/05/pygtk-new-style-python-class-using-builder/
    __gtype_name__ = 'DCStack'

    def __init__(self):
        super().__init__()
        gtk.ListBox.__init__(self, selection_mode=gtk.SelectionMode.NONE)
        self.set_placeholder(gtk.Label(label='Empty stack'))

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
    builder = gtk.Builder.new_from_file(os.path.join(os.path.dirname(__file__), 'ui.xml'))
    builder.connect_signals(ApplicationEventHandler(builder.get_object('main_stack')))
    builder.get_object('main_window').show_all()
    gtk.main()


if __name__ == '__main__':
    main()
