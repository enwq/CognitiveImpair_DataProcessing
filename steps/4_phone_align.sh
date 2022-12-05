#!/bin/bash

for task in Results/speaker_separation/*;do
    mfa align -t ./temp -j 4 $task/SPEAKER_01/ steps/modified_librispeech-lexicon.txt steps/english.zip $task/SPEAKER_01_PHONE/
    rm -rf ./temp
done
