import librosa
import os
import numpy as np
import pandas as pd
import librosa.display
import matplotlib.pyplot as plt
from python_speech_features import fbank
import pickle
def pic(filter_bank_features):
   """ mfcc_df = pd.DataFrame(mfcc_features, columns=['mfcc_Features', 'Class'])
    display(mfcc_df.to_string())  # mfcc"""
   filter_features_df = pd.DataFrame(filter_bank_features, columns=['filter_bank_Features', 'Class'])
   print(filter_features_df)
   """with open('feature_mfcc.pickle', 'wb') as f:
       pickle.dump(mfcc_df, f)"""
   with open('D:/speaker verification/feature_logmelbank.pickle', 'wb') as f:
        pickle.dump(filter_features_df, f)

def normalize_frames(m, Scale=True):
    if Scale:
        return (m - np.mean(m, axis=0)) / (np.std(m, axis=0) + 2e-12)
    else:
        return (m - np.mean(m, axis=0))

# log mel filter banks
def extract_filterbank_feature(filename):
    audio, sr = librosa.load(filename, sr=16000, mono=True)
    filter_banks, energies = fbank(audio, samplerate=sr, nfilt=40, winlen=0.025)
    # f = filter_banks
    filter_banks = 20 * np.log10(np.maximum(filter_banks, 1e-5))
    feature = normalize_frames(filter_banks, Scale=False)
    return feature

def wav_loader(data_directory):
    path_ids = []
    for folder in os.listdir(data_directory):
        if folder == "_background_noise_" :
            break
        k =  os.path.join(data_directory,folder)#join one or more path components
        for i in os.listdir(k):
            #print(k +"  "+folder+"  "+ i)
            if '.wav' in i:
                d = os.path.join(k , i)
                path_ids.append([d , folder , i[:-4]])
    path_id_df = pd.DataFrame(path_ids,columns = ['path_to_file' , 'Speaker_id','data_set_id'])
    return path_id_df
def fet_loader(data_directory):
    path_ids = []
    for folder in os.listdir(data_directory):
        if folder == "_background_noise_" :
            break
        k =  os.path.join(data_directory,folder)#join one or more path components
        for i in os.listdir(k):
            #print(k +"  "+folder+"  "+ i)
            if '.p' in i:
                d = os.path.join(k , i)
                path_ids.append([d , folder , i[:-4]])
    path_id_df = pd.DataFrame(path_ids,columns = ['path_to_file' , 'Speaker_id','data_set_id'])
    return path_id_df
k = wav_loader("test_wavs")
print(k)
filter_bank_features = []
def datdir(data_directory):
    for folder in os.listdir(data_directory):
        k = os.path.join(data_directory, folder)  # join one or more path components
        for i in os.listdir(k):
            if '.wav' in i:
                # mfccs
                #data = features_extractor(os.path.join(k, i))
                #mfcc_features.append([data, folder])

                # log_mel_filter_bank
                data1 = extract_filterbank_feature(os.path.join(k, i))
                filter_bank_features.append([data1, folder])
    return filter_bank_features
fet=datdir("test_wavs")
pic(fet)