#!/bin/bash

inpath=/home/beiming/Desktop/UT_Voice/data_samples
outpath=/home/beiming/Desktop/UT_Voice/data_samples_16k


for f in $inpath/*.wav; do 

  name=$(basename "$f" ".wav")

  ffmpeg -i $f -ar 16000 $outpath/$name.wav;

done
