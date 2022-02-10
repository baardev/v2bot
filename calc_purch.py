#!/usr/bin/python
import lib_v2_globals as g
import lib_v2_ohlc as o
import toml

g.cvars = toml.load(g.cfgfile)
g.datatype = g.cvars["datatype"]

reserve_seed = 10
max_long_buys = 5

def get_purch_qty(reserve_seed):
    max_long_buys = 5
    purch_mult = g.cvars[g.datatype]['purch_mult']
    for i in range(0,1000,1):
        purch_qty = float(i/1000)
        for long_buys in range(max_long_buys):
            last_pq = int((purch_qty * 990)-0)/1000
            pq =  purch_qty * purch_mult ** long_buys
            if pq > reserve_seed:
                return last_pq

def get_purch_qty2(reserve_seed):
    max_long_buys = 5
    purch_mult = g.cvars[g.datatype]['purch_mult']
    for i in range(0,1000,1):
        purch_qty = float(i/1000)
        for long_buys in range(max_long_buys):
            last_pq = int((purch_qty * 990)-0)/1000
            pq =  purch_qty * purch_mult ** long_buys
            if pq > reserve_seed:
                return last_pq

print(get_purch_qty(reserve_seed))
print(get_purch_qty2(reserve_seed))
