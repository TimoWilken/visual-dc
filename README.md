# Visual `dc`

This is an implementation of the [`dc`][wiki] language with a fancy GTK3 user
interface.

## Try it

To run this program:

```{sh}
$ git clone https://github.com/TimoWilken/visual-dc
$ cd visual-dc
$ python3 ui.py
```

## Features

The goal is to implement most commands found on the [`dc(1)` man page][man],
except for some of the printing commands that are unneeded when the stack is
displayed all the time anyway.

Floating-point numbers are supported. In fact, all numbers are stored as Python
`decimal.Decimal`s.

The current implementation reruns the entire script every time the user types,
which could become slow for very long scripts.

A GUI error reporting mechanism would be nice to have -- errors are printed to
`stdout`, but not reported to the user via the UI.

The following screenshot shows the script input in the top half of the window
and the stack after running the script in the bottom half.

![Screenshot][screenshot]

[wiki]: https://en.wikipedia.org/wiki/Dc_(computer_program)
[man]: https://linux.die.net/man/1/dc
[screenshot]: https://github.com/TimoWilken/visual-dc/raw/master/doc/screenshot.png
