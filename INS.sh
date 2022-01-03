#!/bin/bash

if [ "$1" == "" ]; then
    echo "ERROR: Missing DIR name"
    exit 1
fi

mkdir $1 > /dev/null 2>&1
mkdir $1/data > /dev/null 2>&1
mkdir $1/logs > /dev/null 2>&1
cp data/* $1/data > /dev/null 2>&1

cp *.toml                 $1/
cp b_*                    $1/
cp _session_name.txt      $1/
cp v2.py                  $1/
cp lib_v2_globals.py      $1/
cp lib_v2_ohlc.py         $1/
cp lib_v2_listener.py     $1/
cp lib_v2_tests_class.py  $1/
cp lib_panzoom.py         $1/
cp state.json             $1/
cp lib_binance.py         $1/
#cp auth_client.py     $1/
#cp public_client.py   $1/

cp report.py              $1/
cp view.py                $1/
cp gview.py               $1/
cp dbview.py              $1/
cp merge.py               $1/
cp liveview.py            $1/
cp ohlc_backdata.py       $1/
cp backdata.py            $1/
cp README.md              $1/
cp pread.py               $1/

