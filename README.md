# Visual `dc`

This is an implementation of the [`dc`][wiki] language with a fancy GTK3 user
interface.

The goal is to implement most commands found on the [`dc(1)` man page][man],
except for some of the printing commands that are unneeded when the stack is
displayed all the time anyway.

Floating-point numbers are supported. In fact, all numbers are stored as Python
`decimal.Decimal`s.

The current implementation reruns the entire script every time the user types,
which could become slow for very long scripts.

A GUI error reporting mechanism would be nice to have -- errors are printed to
`stdout`, but not reported to the user via the UI.

[wiki]: https://en.wikipedia.org/wiki/Dc_(computer_program)
[man]: https://linux.die.net/man/1/dc
