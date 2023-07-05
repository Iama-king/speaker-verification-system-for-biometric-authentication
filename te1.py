import tensorflow as tf
import librosa
import pickle
from configure import SAMPLE_RATE
import IPython.display as ipd
print(tf.config.list_physical_devices('GPU'))
def read_audio(filename, sample_rate=SAMPLE_RATE):
    audio, sr = librosa.load(filename, sr=sample_rate, mono=True)
    audio = audio.flatten()
    return audio
'''ab= read_audio("test_wavs/103F3021/enroll.wav",SAMPLE_RATE)
print(ab)
af3 = "test_wavs/103F3021/enroll.wav"
ipd.Audio(af3)'''

def read_MFB(filename):
    with open(filename, 'rb') as f:
        feat_and_label = pickle.load(f)

    feature = feat_and_label['feat']  # size : (n_frames, dim=40)
    label = feat_and_label['label']
    return feature,label,feat_and_label
f,l,fl=read_MFB("feat_logfbank_nfilt40/test/240M3063/enroll.p")
print(len(fl))
print(fl)
print(type(fl))
print("------------------------------")

import librosa
import numpy as np
from python_speech_features import fbank

def normalize_frames(m,Scale=True):
    if Scale:
        return (m - np.mean(m, axis=0)) / (np.std(m, axis=0) + 2e-12)
    else:
        return (m - np.mean(m, axis=0))
def feat(th):
    audio, sr = librosa.load(th, sr=SAMPLE_RATE, mono=True)
    filter_banks, energies = fbank(audio, samplerate=SAMPLE_RATE, nfilt=40, winlen=0.025)
    filter_banks = 20 * np.log10(np.maximum(filter_banks,1e-5))
    feature = normalize_frames(filter_banks, Scale=False)
    return feature

import pickle as pkl
import numpy as np

arrayInput = np.zeros((1000,2)) #Trial input
save = True
load = True
a1=feat("test_wavs/sanjay/test.wav")
a2=feat("test_wavs/sanjay/enroll.wav")
st1={}
st2={}
st1['label']='240M3111'
st2['label']='240M3111'
st1['feat']=a1
st2['feat']=a2
filename1 = 'feat_logfbank_nfilt40/test/sanjay/test.p'
filename2 = 'feat_logfbank_nfilt40/test/sanjay/enroll.p'
fileObject = open(filename1, 'wb')
fb2=open(filename2, 'wb')
if save:
    pkl.dump(st1, fileObject)
    pkl.dump(st2, fb2)
    fileObject.close()
print("1111111111111111111111111111111111111111111111111111111111")
print(len(a1))
print(type(a1))
print(len(a1[0]))