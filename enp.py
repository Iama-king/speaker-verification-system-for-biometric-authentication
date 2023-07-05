import librosa
import numpy as np
from python_speech_features import fbank
import tensorflow as tf
import librosa
import pickle
from configure import SAMPLE_RATE
import IPython.display as ipd
import os
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
pt="D:/audio/enro"
la3=os.listdir(pt)
for i in la3:
    a1=feat(pt+"/"+i+"/"+"test.wav")
    a2=feat(pt+"/"+i+"/"+"enroll.wav")
    st1={}
    st2={}
    st1['label']=i
    st2['label']=i
    st1['feat']=a1
    st2['feat']=a2
    log_dir="D:/audio/feat/"+i
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    filename1 = 'D:/audio/feat/'+i+'/test.p'
    filename2 = 'D:/audio/feat/'+i+'/enroll.p'
    fileObject = open(filename1, 'wb')
    fb2=open(filename2, 'wb')
    if save:
        pkl.dump(st1, fileObject)
        pkl.dump(st2, fb2)
        fileObject.close()

import enroll
import verification as v
#enroll.main()
v.main("swarna","swarna")
print()
print(la3)