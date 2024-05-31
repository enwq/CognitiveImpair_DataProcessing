import time
import yaml
import os
import glob
from pyannote.audio import Pipeline
from pydub import AudioSegment
import torch

def speaker_separation(args):
    config_path = args.conf_dir
    config = yaml.load(open(config_path, 'r'), Loader=yaml.FullLoader)
    data_path = config['Data']['path']
    out_path = config['Data']['out_path']
    output_folder = os.path.join(out_path, config['Speaker_separation']['output_folder'])
    access_token = config['Speaker_separation']['access_token']
    speaker_num = config['Speaker_separation']['speaker_num']
    duration_threshold = config['Speaker_separation']['remove_clip_shorter_than']
    begin_offset = config['Speaker_separation']['begin_offset']
    end_offset = config['Speaker_separation']['end_offset']

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token = access_token)
        
    wav_path_list = glob.glob(data_path + '/*.wav')
    for wav_path in wav_path_list:
        diarization = pipeline(wav_path, num_speakers = speaker_num)
        task_name = os.path.basename(wav_path)[:-4]
        task_out_folder = os.path.join(output_folder, task_name)
        
        if not os.path.exists(task_out_folder):
            os.makedirs(task_out_folder)
        clip_idx = {}
        prev_speaker, prev_start = None, None
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            if turn.end - turn.start > duration_threshold:        
                speaker_path = os.path.join(task_out_folder, speaker)
                start, end = turn.start - begin_offset, turn.end + end_offset
                if prev_speaker == None and prev_start == None:
                    prev_speaker, prev_start = speaker, start
                elif speaker == prev_speaker:
                    start = prev_start

                if not os.path.exists(speaker_path):
                    os.makedirs(speaker_path)
                if speaker in clip_idx:
                    clip_idx[speaker] += 1
                else:
                    clip_idx[speaker] = 1                
                
                clip_name = speaker + '_' + format(clip_idx[speaker], '02d') + '.wav'
                clip_out_path = os.path.join(speaker_path, clip_name)             
                _wav = AudioSegment.from_wav(wav_path)
                _wav = _wav[start*1000:end*1000]
                _wav.export(clip_out_path, format="wav")
                prev_start = start


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--conf_dir', default = 'configuration.yaml')

    args = parser.parse_args()
    speaker_separation(args)
