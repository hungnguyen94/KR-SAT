#!/usr/bin/env bash
cryptominisat5 | sed -e "/^[c|s]/ d" | sed -e "s/v//g" 
