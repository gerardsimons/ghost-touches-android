#!/bin/bash

adb shell getevent -lt /dev/input/event4 | tee adb_logs/touch_log_labeled_date$(date +%Y%m%d).txt

