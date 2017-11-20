
import sys, timeit, math, statistics

from smp import NUM_STRATEGIES


def time_smp(N, strat, iters):
    setup = "from smp import smp"
    times = timeit.repeat(stmt="smp(%d,whichstrat=%d,evaluate=False)"%(N,strat), setup=setup,repeat=iters,number=1)
    return statistics.mean(times)


times = []
for i in range(1,4):
    size = math.pow(10,i)
    row = [size]
    print(size)
    for strat in range(NUM_STRATEGIES):
        print(strat)
        time = time_smp(size, strat, 1)
        row.append(time)
    times.append(row)
    
print(times)








