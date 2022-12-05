import time
import yaml
import os
import glob
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from datasets import load_dataset
import torch
import librosa


def stats(args):
    config_path = args.conf_dir
    config = yaml.load(open(config_path, 'r'), Loader=yaml.FullLoader)
    data_path = config['Data']['path']
    out_path = config['Data']['out_path']
    input_folder = os.path.join(out_path, config['Speaker_separation']['output_folder']) # output from speaker separation
    speaker = config['Stats']['speaker']
    
    task_list = os.listdir(input_folder)
    total_t, total_wrd_num = 0.0, 0
    task_sr = {}
    for task in task_list:
        task_spk_wrd = os.path.join(input_folder, task, speaker)
        task_spk_textgrid = task_spk_wrd + '_PHONE'
        ## Compute speaking rate num_word/duration
        wrd_path_list = glob.glob(task_spk_wrd + '/*.txt')
        wav_path_list = glob.glob(task_spk_wrd + '/*.wav')
        
        if len(wrd_path_list) != len(wav_path_list):
            raise Exception("Numbers of wav and label files are mismatch, this probably due to the very short wav files, please check!")
        t = 0.0
        wrd_num = 0
        for i in range(len(wrd_path_list)):
            _t = librosa.get_duration(filename=wav_path_list[i])
            f = open(wrd_path_list[i], 'r')
            l = f.readlines()
            if len(l) > 0:
                sent = l[0]
                _wrd_num = len(sent.split(' '))
            t += _t
            wrd_num += _wrd_num
            
        task_speaking_rate = wrd_num / t
        task_sr[task] = task_speaking_rate
        total_t += t
        total_wrd_num += wrd_num
    total_speaking_rate = total_wrd_num / total_t
    output_file = os.path.join(out_path, 'stats.txt')
    f = open(output_file, 'w')
    for task_name, sr in task_sr.items():
        s = 'The speaker rate of task: ' + task_name + ' is ' + str(sr) + '\n'
        f.write(s)
    ss = 'The overall speaker rate is ' + str(total_speaking_rate) + '\n'
    f.write(ss)

    f.close()

    
        

    


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--conf_dir', default = 'configuration.yaml')

    args = parser.parse_args()
    stats(args)
