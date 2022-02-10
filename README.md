# digitle-solver
A solver for Eevee's Digitle puzzle https://c.eev.ee/digitle/

Run by invoking the script on the command line,
passing as space-separated argument
the desired result, followed by the available numeric tiles.

For example, the Feb 10 puzzle has a target of 612,
with tiles of 100, 4, 6, 9, 10, and 2.
This would be invoked as:

```sh
python digitle.py 612 100 4 6 9 10 2
```

It will then output to stdout a succession of possible digitle plays,
each more accurate than the last,
until it hits the target precisely
and outputs *all* perfect answers.

TODO: Additionally rank perfect plays by how many intermediate tiles you have to generate to reach the target; less is better.