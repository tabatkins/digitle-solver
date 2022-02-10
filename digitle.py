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
    yield MathOp(val1, "+", val2)
    if int(val1) != 1 and int(val2) != 1:
        yield MathOp(val1, "*", val2)
    if int(val1) > int(val2):
        yield MathOp(val1, "-", val2)
    else:
        yield MathOp(val2, "-", val1)
    if int(val2) not in (0, 1) and int(val1) % int(val2) == 0:
        yield MathOp(val1, "/", val2)
    if int(val1) not in (0, 1) and int(val2) % int(val1) == 0:
        yield MathOp(val2, "/", val1)


def genExprs(nums: Sequence[int]) -> Generator[MathNode, None, None]:
    # Initial list gives the size-1 results
    exprs: List[List["MathOp"]] = [[], [], [], [], [], [], []]

    nums = list(nums)
    yield from nums

    # combine them to get the size-2 results
    for lhs, rhs in itertools.combinations(nums, 2):
        exprs[2].extend(makeOps(lhs, rhs))
    yield from exprs[2]

    # combine the 1 and 2 to get size-3,
    # but check for shared tiles
    for tile, op in itertools.product(nums, exprs[2]):
        if tile in list(op.tiles):
            continue
        exprs[3].extend(makeOps(tile, op))
    yield from exprs[3]

    # combine 1 and 3, and 2 and 2, to get size 4
    for tile, op in itertools.product(nums, exprs[3]):
        if tile in list(op.tiles):
            continue
        exprs[4].extend(makeOps(tile, op))
    for op1, op2 in itertools.combinations(exprs[2], 2):
        if set(op1.tiles) & set(op2.tiles):
            continue
        exprs[4].extend(makeOps(op1, op2))
    yield from exprs[4]

    # 1 and 4, 2 and 3 to get size 5
    for tile, op in itertools.product(nums, exprs[4]):
        if tile in list(op.tiles):
            continue
        exprs[5].extend(makeOps(tile, op))
    for op1, op2 in itertools.product(exprs[2], exprs[3]):
        if set(op1.tiles) & set(op2.tiles):
            continue
        exprs[5].extend(makeOps(op1, op2))
    yield from exprs[5]

    # finally, 1/5, 2/4, and 3/3 for size 6
    for tile, op in itertools.product(nums, exprs[5]):
        if tile in list(op.tiles):
            continue
        exprs[6].extend(makeOps(tile, op))
    for op1, op2 in itertools.product(exprs[2], exprs[4]):
        if set(op1.tiles) & set(op2.tiles):
            continue
        exprs[6].extend(makeOps(op1, op2))
    for op1, op2 in itertools.combinations(exprs[3], 2):
        if set(op1.tiles) & set(op2.tiles):
            continue
        exprs[6].extend(makeOps(op1, op2))
    yield from exprs[6]


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
                if getOp(self.val1) == "-":
                    str1 = parens(str1)
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
    argparser.add_argument("numbers", nargs=6, help="The 6 starting number tiles.")

    args = argparser.parse_args()
    solve(int(args.target), [int(x) for x in args.numbers])
