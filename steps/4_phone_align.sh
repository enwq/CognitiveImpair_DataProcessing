#!/bin/bash

for file in Results_test/speaker_separation/*;do
    mfa align -t ./temp -j 4 $file/SPEAKER_00/ steps/modified_librispeech-lexicon.txt steps/english.zip $file/SPEAKER_00_PHONE/
    # mfa align -t ./temp -j 4 $file/SPEAKER_01/ steps/modified_librispeech-lexicon.txt steps/english.zip $file/SPEAKER_01_PHONE/
    rm -rf ./temp
done