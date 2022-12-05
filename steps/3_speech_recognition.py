import time
import yaml
import os
import glob
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from datasets import load_dataset
import torch
import librosa


def speech_recognition(args):
    config_path = args.conf_dir
    config = yaml.load(open(config_path, 'r'), Loader=yaml.FullLoader)
    data_path = config['Data']['path']
    out_path = config['Data']['out_path']
    input_folder = os.path.join(out_path, config['Speaker_separation']['output_folder']) # output from speaker separation
    speaker = config['Word_recognition']['speaker']
        
    processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h-lv60-self")
    model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h-lv60-self")
    task_list = os.listdir(input_folder)
    for task in task_list:
        task_spk = os.path.join(input_folder, task, speaker)
        wav_path_list = glob.glob(task_spk + '/*.wav')
        for wav_path in wav_path_list:    
            audio, _ = librosa.load(wav_path, sr=16000)
            trans_path = wav_path[:-4] + '.txt'

            input_values = processor(audio, return_tensors="pt", padding="longest").input_values
            logits = model(input_values).logits 
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = processor.batch_decode(predicted_ids)
    
            f = open(trans_path, 'w')
            f.write(transcription[0])
            f.close()
    


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--conf_dir', default = 'configuration.yaml')

    args = parser.parse_args()
    speech_recognition(args)
