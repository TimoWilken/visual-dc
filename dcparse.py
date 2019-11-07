#!/usr/bin/env python3

'''Graphical implementation of the dc calculator.'''

import re
import decimal
import functools as ft
import operator as op
from collections import deque


def flip(function):
    '''Flips the two positional arguments to FUNCTION, preserving **KWARGS.'''
    def flipped(x, y, **kwargs):
        return function(y, x, **kwargs)
    return flipped


class DecimalMultipliableString(str):
    '''A str subclass that can be multiplied by a Decimal.'''
    def __mul__(self, other):
        if isinstance(other, decimal.Decimal):
            return int(other) * self
        return super().__mul__(other)

    def __rmul__(self, other):
        return self.__mul__(other)


class UnknownCommandError(Exception):
    '''The start of a command sequence could not be matched.'''
class EmptyStackError(Exception):
    '''The stack contains too few elements to complete the operation.'''


class Stack:
    '''Represents a dc stack, to which commands can be applied.'''
    def __init__(self, decimal_context=decimal.getcontext()):
        # TODO: use a deque instead of a list
        self._stack = []
        self._context = decimal_context

    def clear(self):
        '''Empty the stack.'''
        self._stack.clear()

    def push(self, *values):
        '''Push a value onto the stack.'''
        self._stack.extend(values)

    def pop(self):
        '''Pop a value off the stack.'''
        return self._stack.pop()

    def pop_many(self, num):
        '''Pop NUM values off the stack, generating them in the order popped.'''
        return tuple(self.pop() for _ in range(num))

    def __len__(self):
        return len(self._stack)

    def __bool__(self):
        return bool(self._stack)

    def __iter__(self):
        return iter(self._stack)

    def __list__(self):
        return list(self._stack)

    def __tuple__(self):
        return tuple(self._stack)

    def __reversed__(self):
        return reversed(self._stack)

    def run_commands(self, parsed):
        '''Run a CommandSequence on the current stack.'''
        with decimal.localcontext(self._context) as _:
            for func in parsed.partial_commands():
                try:
                    func(self)
                except IndexError as err:
                    raise EmptyStackError(err)


class CommandSequence:
    '''Represents a sequence of parsed commands.'''
    _registered_commands = []

    def __init__(self, cmd_text):
        '''Parse CMD_TEXT and initialise the CommandSequence.

        NOTE: This function only ever modifies the left-hand side of CMD_TEXT,
        so the argument to UnknownCommandError is a suffix of CMD_TEXT and its
        length is indicative of how far from the end of CMD_TEXT the error
        occurred.
        '''
        self.commands = [(m.group(0), f) for _, m, f in self.tokenise(cmd_text)]

    @classmethod
    def tokenise(cls, cmd_text):
        '''Split the CMD_TEXT into tokens.'''
        str_position = 0
        while str_position < len(cmd_text):
            for regex, func in cls._registered_commands:
                match = regex.match(cmd_text[str_position:])
                if match:
                    yield str_position, match, func
                    str_position += match.end()
                    break
            else:
                raise UnknownCommandError(str_position)

    def __str__(self):
        '''Return the representation as text of the command.'''
        return ' '.join(text for text, _ in self.commands)

    def partial_commands(self):
        '''Yield partially applied command callbacks requiring only a stack.'''
        for text, func in self:
            yield ft.partial(func, text)

    def __iter__(self):
        return iter(self.commands)

    @classmethod
    def register_command(cls, regex, function):
        '''Register a FUNCTION to be called when REGEX matches.

        The function will be called with the matched text and the current stack.
        '''
        regex = re.compile(regex, re.MULTILINE)
        cls._registered_commands.append((regex, function))


def register_command(regex):
    '''Registers a function with CommandSequence.'''
    return ft.partial(CommandSequence.register_command, regex)


@register_command(r'\s')
def whitespace(*_):
    '''Whitespace, including newlines; no-op.'''


@register_command('#.*$')
def comment(*_):
    '''Comment up to end of line; no-op.'''


@register_command('_?[0-9.]+')
def constant(cmd_text, stack):
    '''Represents a numerical literal.'''
    stack.push(decimal.getcontext().create_decimal(cmd_text.replace('_', '-')))


@register_command(r'\[[^]]+?\]')
def string(cmd_text, stack):
    '''Represents a string literal.'''
    stack.push(DecimalMultipliableString(cmd_text[1:-1]))


@register_command('[IO]')
def get_radix(_, stack):
    '''Push the current input and output radix.'''
    stack.push(decimal.getcontext().radix())


@register_command('K')
def get_precision(_, stack):
    '''Push the decimal precision.'''
    # TODO: This is not the same as what dc does!
    # dc gets the number of *fraction digits*, this gets the number of
    # *significant figures*.
    stack.push(decimal.getcontext().prec)


@register_command('k')
def set_precision(_, stack):
    '''Set the decimal precision.'''
    # TODO: This is not the same as what dc does!
    # dc sets the number of *fraction digits*, this sets the number of
    # *significant figures*.
    decimal.getcontext().prec = int(stack.pop())


@register_command('f')
def print_stack(_, stack):
    '''Prints the entire stack without altering it.'''
    if stack:
        print(*reversed(stack), sep='\n')


@register_command('r')
def swap(_, stack):
    '''Swaps the top two values on the stack.'''
    stack.push(*stack.pop_many(2))


@register_command('R')
def rotate(_, stack):
    '''Rotates the top N elements of the stack.'''
    num_to_rotate = int(stack.pop())
    rotate_down = num_to_rotate >= 0
    num_to_rotate = min(abs(num_to_rotate), len(stack))
    elements = deque(reversed(stack.pop_many(num_to_rotate)))
    # top of stack is on the right
    if rotate_down:
        elements.append(elements.popleft())
    else:
        elements.appendleft(elements.pop())
    stack.push(*elements)


@register_command('c')
def clear(_, stack):
    '''Clears the stack.'''
    stack.clear()


@register_command('d')
def duplicate(_, stack):
    '''Duplicates the top of the stack.'''
    top = stack.pop()
    stack.push(top, top)


@register_command('z')
def stack_depth(_, stack):
    '''Pushes the current stack depth.'''
    stack.push(len(stack))


@register_command('v')
def square_root(_, stack):
    '''Pushes the square root of the top of the stack.'''
    stack.push(stack.pop().sqrt())


@register_command('[-+*/^]')
def common_numerical(cmd_text, stack):
    '''Adds/subtracts/multiplies/divides two numbers.'''
    ops = {'+': op.add, '-': op.sub, '*': op.mul, '/': op.truediv, '^': op.pow}
    stack.push(flip(ops[cmd_text])(*stack.pop_many(2)))


@register_command('%')
def remainder(_, stack):
    '''Computes the remainder of what the "/" command would do.

    Note that this NOT generally an integer remainder, but is affected by the
    current precision!
    '''
    denominator, numerator = stack.pop_many(2)
    # TODO: correct implementation as specified
    stack.push(numerator % denominator)


@register_command('~')
def div_mod(_, stack):
    '''Computes the quotient and remainder of what "/" would do.

    The same caveat as for "%" applies!
    '''
    denominator, numerator = stack.pop_many(2)
    # TODO: correct implementation as specified
    quotient, modulus = divmod(numerator, denominator)
    stack.push(quotient, modulus)


@register_command('\\|')
def mod_exponentiation(_, stack):
    '''Computes (a ^ b) mod c.'''
    modulus, exponent, base = stack.pop_many(3)
    stack.push(pow(base, exponent, modulus))


def main():
    '''Main entry point.'''
    import sys, os  # pylint: disable=multiple-imports
    log_error = ft.partial(print, os.path.basename(sys.argv[0]),
                           file=sys.stderr, sep=': ')

    try:
        cmds = CommandSequence(sys.stdin.read())
    except UnknownCommandError as err:
        log_error('unknown command', err)
        return 1
    stack = Stack(decimal.Context(Emax=100000))
    try:
        stack.run_commands(cmds)
    except EmptyStackError as err:
        log_error('empty stack', err)
        return 2
    stack.run_commands(CommandSequence('f'))
    return 0


if __name__ == '__main__':
    exit(main())
