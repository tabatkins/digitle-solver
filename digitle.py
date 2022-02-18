import abc
import argparse
import dataclasses
import itertools
import typing

from collections.abc import Sequence, Iterator
from typing import Optional, List, Tuple, Generator, Union, Set


T = typing.TypeVar("T")
MathNode = Union[int, "MathOp"]


def makeOps(val1: MathNode, val2: MathNode) -> Generator["MathOp", None, None]:
    # Zeroes are always trivial
    if int(val1) == 0 or int(val2) == 0:
        return
    # Plus is always valid
    yield MathOp(val1, "+", val2)
    # *1 is trivial, otherwise all mul is valid
    if int(val1) != 1 and int(val2) != 1:
        yield MathOp(val1, "*", val2)
    # Negative results are invalid,
    # and 0 results are trivial.
    if int(val1) > int(val2):
        yield MathOp(val1, "-", val2)
    elif int(val2) > int(val1):
        yield MathOp(val2, "-", val1)
    # Fractional results are invalid,
    # and /1 is trivial.
    if int(val2) != 1 and int(val1) % int(val2) == 0:
        yield MathOp(val1, "/", val2)
    if int(val1) != 1 and int(val2) % int(val1) == 0:
        yield MathOp(val2, "/", val1)


def genExprs(nums: Sequence[int]) -> Generator[MathNode, None, None]:
    # Initial list gives the size-1 results
    exprs: List[List["MathNode"]] = [[], list(nums)]

    yield from exprs[1]

    for exprSize in range(2, len(exprs[1]) + 1):
        exprs.append([])
        for lhsSize in range(1, exprSize // 2 + 1):
            rhsSize = exprSize - lhsSize
            pairs: Iterator[Tuple[MathNode, MathNode]]
            if lhsSize == rhsSize:
                pairs = itertools.combinations(exprs[lhsSize], 2)
            else:
                pairs = itertools.product(exprs[lhsSize], exprs[rhsSize])
            for op1, op2 in pairs:
                if tiles(op1) & tiles(op2):
                    continue
                exprs[exprSize].extend(makeOps(op1, op2))
        yield from exprs[exprSize]


def tiles(op: "MathNode") -> Set[int]:
    if isinstance(op, int):
        return set([op])
    else:
        return set(op.tiles)


@dataclasses.dataclass
class MathOp:
    val1: MathNode
    op: str
    val2: MathNode
    _str: Optional[str] = None
    _int: Optional[int] = None

    def __str__(self) -> str:
        def parens(s: str) -> str:
            return f"({s})"

        if self._str is None:
            str1 = str(self.val1)
            str2 = str(self.val2)

            # Add parens if necessary for precedence
            if self.op == "+":
                pass
            elif self.op == "*":
                if getOp(self.val1) in "+-":
                    str1 = parens(str1)
                if getOp(self.val2) in "+-":
                    str2 = parens(str2)
            elif self.op == "-":
                if getOp(self.val2) in "+-":
                    str2 = parens(str2)
            elif self.op == "/":
                if getOp(self.val1) in "+-/":
                    str1 = parens(str1)
                if getOp(self.val2) in "+-*/":
                    str2 = parens(str2)

            self._str = str1 + self.op + str2
        return self._str

    def __int__(self) -> int:
        if self._int is None:
            val1 = int(self.val1)
            val2 = int(self.val2)
            if self.op == "+":
                self._int = val1 + val2
            elif self.op == "-":
                self._int = val1 - val2
            elif self.op == "*":
                self._int = val1 * val2
            elif self.op == "/":
                self._int = val1 // val2
            else:
                raise Exception(f"Unknown op '{self.op}'.")
        return self._int

    @property
    def tiles(self) -> Generator[int, None, None]:
        if isinstance(self.val1, int):
            yield self.val1
        else:
            yield from self.val1.tiles
        if isinstance(self.val2, int):
            yield self.val2
        else:
            yield from self.val2.tiles


def getOp(node: MathNode) -> str:
    if isinstance(node, int):
        return "value"
    else:
        return node.op


def solve(target, nums):
    bestExpr = (None, float("inf"))
    seen = set()
    for i, expr in enumerate(genExprs(nums)):
        val = int(expr)
        error = abs(val - target)
        if error < bestExpr[1] or error == 0:
            bestExpr = (expr, error)
            s = str(expr)
            if s not in seen:
                print(s, error)
                seen.add(s)
    print(f"{i} expressions tested")
    return bestExpr


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description=f"Tries to solve today's digitle: https://c.eev.ee/digitle/"
    )
    argparser.add_argument("target", help="The target value.")
    argparser.add_argument("numbers", nargs="+", help="The starting number tiles.")

    args = argparser.parse_args()
    solve(int(args.target), [int(x) for x in args.numbers])
