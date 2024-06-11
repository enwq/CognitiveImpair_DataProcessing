import time
import yaml
import os
import glob
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from datasets import load_dataset
import torch
import librosa
import textgrid
import pysptk
from scipy.io import wavfile
import numpy as np


def VUV_stats(args):
    config_path = args.conf_dir
    config = yaml.load(open(config_path, 'r'), Loader=yaml.FullLoader)
    data_path = config['Data']['path']
    out_path = config['Data']['out_path']
    input_folder = os.path.join(out_path, config['Speaker_separation']['output_folder']) # output from speaker separation
    speaker = config['Stats']['speaker']
    
    UV_list = ['F', 'HH', 'K', 'P', 'S', 'SH', 'T', 'TH', 'spn']
    
    task_list = os.listdir(input_folder)
    for task in task_list:
        task_spk_wrd = os.path.join(input_folder, task, speaker)
        task_spk_textgrid = task_spk_wrd + '_PHONE'

        txtgrid_path_list = glob.glob(task_spk_textgrid + '/*.TextGrid')
        wav_path_list = glob.glob(task_spk_wrd + '/*.wav')
        
        txtgrid_path_list.sort()
        wav_path_list.sort()
        
        for i in range(len(txtgrid_path_list)):            

            tg = textgrid.TextGrid.fromFile(txtgrid_path_list[i])
            ph_tg = tg[1]  
            ph_list = []
            ph_start, ph_end = [], []          
            for j in range(len(ph_tg)):           
                _ph = ph_tg[j].mark
                ph = ''.join([i for i in _ph if not i.isdigit()])
                if _ph == '' or ph in UV_list:
                    ph_list.append('unvoiced')
                else:
                    ph_list.append('voiced')                    
                ph_start.append(ph_tg[j].minTime)
                ph_end.append(ph_tg[j].maxTime)
                
            vuv_list = []
            vuv_start, vuv_end = [], []
            for j in range(len(ph_list)):
                if j == 0:
                    vuv_list.append(ph_list[j])
                    vuv_start.append(ph_start[j])
                    vuv_end.append(ph_end[j])                
                elif ph_list[j] == ph_list[j-1]:
                    vuv_end[-1] = ph_end[j]
                    
                else:
                    vuv_list.append(ph_list[j])
                    vuv_start.append(ph_start[j])
                    vuv_end.append(ph_end[j])

            f = open(txtgrid_path_list[i], 'a')
            f.write("    item [3]:\n")
            f.write("        class = \"IntervalTier\" \n")        
            f.write("        name = \"vuv_asr\" \n")
            f.write("        xmin = 0 \n")
            f.write("        xmax = {} \n".format(str(vuv_end[-1])))      
            f.write("        intervals: size = {} \n".format(str(len(vuv_list))))   
            for j in range(len(vuv_list)):
                f.write("        intervals [{}]:\n".format(str(j+1)))    
                f.write("            xmin = {} \n".format(str(vuv_start[j])))
                f.write("            xmax = {} \n".format(str(vuv_end[j]))) 
                f.write("            text = \"{}\"\n".format(str(vuv_list[j])))                                         
            f.close()   
                                 
            fs, x = wavfile.read(wav_path_list[i])
            assert fs == 44100
            f0 = pysptk.rapt(x.astype(np.float32), fs=fs, hopsize=80, min=60, max=200, otype="f0")
            ratio = 0.005
            vuv_audio_list = []
            vuv_audio_start_end = []

            for j in range(len(f0)):
                if j == 0:
                    vuv_audio_start_end.append(j*ratio)
                    if f0[j] == 0.0:
                        vuv_audio_list.append('unvoiced')
                    else:
                        vuv_audio_list.append('voiced')
                else:
                    if f0[j-1] == 0.0 and f0[j] != 0.0:
                        vuv_audio_start_end.append(j*ratio)
                        vuv_audio_list.append('voiced') 
                    if f0[j-1] != 0.0 and f0[j] == 0.0:
                        vuv_audio_start_end.append(j*ratio)
                        vuv_audio_list.append('unvoiced')  
                        
            vuv_audio_start_end.append(vuv_end[-1])
            f = open(txtgrid_path_list[i], 'a')
            f.write("    item [4]:\n")
            f.write("        class = \"IntervalTier\" \n")        
            f.write("        name = \"vuv_f0\" \n")
            f.write("        xmin = 0 \n")
            f.write("        xmax = {} \n".format(str(vuv_end[-1])))      
            f.write("        intervals: size = {} \n".format(str(len(vuv_audio_list))))   
            for j in range(len(vuv_audio_list)):
                f.write("        intervals [{}]:\n".format(str(j+1)))    
                f.write("            xmin = {} \n".format(str(vuv_audio_start_end[j])))
                f.write("            xmax = {} \n".format(str(vuv_audio_start_end[j+1]))) 
                f.write("            text = \"{}\"\n".format(str(vuv_audio_list[j])))                                         
            f.close() 
 
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--conf_dir', default = 'configuration.yaml')

    args = parser.parse_args()
    VUV_stats(args)
