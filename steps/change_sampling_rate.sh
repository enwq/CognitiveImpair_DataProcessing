#!/bin/bash

inpath=/home/ys22999@austin.utexas.edu/CognitiveImpair_DataProcessing/Data
outpath=/home/ys22999@austin.utexas.edu/CognitiveImpair_DataProcessing/Data_16k


for f in $inpath/*.wav; do 

  name=$(basename "$f" ".wav")

  ffmpeg -i $f -ar 16000 $outpath/$name.wav;

done
