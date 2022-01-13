#!/usr/bin/bash

#./creplace.py -s datatype    -r stream

./creplace.py -s cpd_filter -r '0'

./creplace.py -s stream.testpair -r "['BUY_tvb3','SELL_tvb3']"
./creplace.py -s display -r 'false'
./creplace.py -s headless -r 'true'
./creplace.py -s datatype -r "'stream'"
./creplace.py -s stream.short_purch_qty -r "0.414"
./creplace.py -s stream.long_purch_qty -r "0.414"

