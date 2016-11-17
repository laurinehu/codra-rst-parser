#!/bin/sh
#  Run from root mallet directory

DATA_DIR=data/
OUTPUT_DIR=results/

if [ ! -e $OUTPUT_DIR ]; then mkdir $OUTPUT_DIR; fi

bin/mallethon scripts/TrainCRF.py \
  -f data/conll03.train10k.txt \
  -m $OUTPUT_DIR/crf.ser.gz \
  -i 5

