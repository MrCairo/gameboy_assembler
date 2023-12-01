"""Convert an Expression to/from decimal (unless it's a character type)."""

import string
from singleton_decorator import singleton
from collections import namedtuple

from .expression import ExpressionType, Expression
from .descriptor import BaseDescriptor, DescriptorArgs

ECMinMax = namedtuple('ECMinMax', ['min', 'max'])


class Conversion():

    def __init__(self, expression: Expression):
        self._source = expression
        val = expression.value
        desc = expression.descriptor
        self._dec_val = int(val, desc.args.base)

    def to_decimal(self) -> Expression:
        return Expression(self._dec_a
