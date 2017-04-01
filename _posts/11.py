from math import *
from fractions import Fraction as F
import sys
import os

si = sys.stdin
so = sys.stdout
se = sys.stderr



ans = [0] * 101

p, q, n = 50,75,2

for i in range(101):
    curdist = 0
    l = 1
    lft = 1.
    c = i
    while i < 100:
        curdist += i * l / 100. * lft
        lft *= (1 - i / 100.)
        l += 1
        i += q
    curdist += l * lft
    ans[c] = curdist

print ans
t = 0

for i in range(n):
    if i > p:
        pp = 1
    else:
        cnt = i
        pp = p
        while pp >= 1 and cnt > 0:
            cnt -= 1
            pp = pp / 2.
        pp = int(pp)
        if pp < 1:
            pp = 1
    t += ans[pp]

print t
