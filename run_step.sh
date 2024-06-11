#!/bin/bash -e


conf_dir=configuration.yaml

echo "Now performing speaker separation."

python3 steps/2_speaker_separation.py --conf_dir $conf_dir

echo "Now performing speech recognition."

python3 steps/3_speech_recognition.py --conf_dir $conf_dir

echo "Now performing phoneme alignment based on the recognized labels."

bash steps/4_phone_align.sh

echo "Now computing stats."

python3 steps/5_stats.py --conf_dir $conf_dir

echo "Now computing VUV."

python3 steps/6_VUV.py --conf_dir $conf_dir

echo "Done! :)"




