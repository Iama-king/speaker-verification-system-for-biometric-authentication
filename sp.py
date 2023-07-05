#converts .wav to pickle with feature extraction
import librosa
import numpy as np
from python_speech_features import fbank
import tensorflow as tf
import librosa
import pickle
from configure import SAMPLE_RATE
import IPython.display as ipd
import os
def normalize_frames(m,Scale=True):# z score norm
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
def main(name="null",va=0):
    arrayInput = np.zeros((1000,2)) #Trial input
    save = True
    load = True
    if(va==0):
        pt="D:/audio/rsp/splits 30sec/"
        target="D:/audio/rsp/test/"
    else:
        pt = "D:/audio/rsp/newenroll/"
        target = "D:/audio/rsp/feat/"
    la3=os.listdir(pt)
    if(name=="null"):
        for i in la3:
            for j in os.listdir((pt+i)):
                a1=feat(pt+i+"/"+j)
                st1={}
                st1['label']=i
                st1['feat']=a1
                log_dir=target+i
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                filename1 = target+i+'/'+j.split(".")[0]+'t.p'
                fileObject = open(filename1, 'wb')
                if save:
                    pkl.dump(st1, fileObject)
                    fileObject.close()
    else:
        for j in os.listdir((pt + name)):
            a1 = feat(pt + name + "/" + j)
            st1 = {}
            st1['label'] = name
            st1['feat'] = a1
            log_dir = target + name
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            filename1 = target + name + '/' + j.split(".")[0] + '.p'
            fileObject = open(filename1, 'wb')
            if save:
                pkl.dump(st1, fileObject)
                fileObject.close()

if __name__ == '__main__':
    main()
import enroll
import verification as v