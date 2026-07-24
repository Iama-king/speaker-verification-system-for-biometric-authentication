# import sys
# print('#Hello from python#')
# print('First param:'+sys.argv[1]+'#')
# print('Second param:'+sys.argv[2]+'#')
import os
import librosa
import numpy as np
def features_extractor(file):
    
    #load the file audio
    audio, sample_rate = librosa.load(file,sr = 16000)
    
    #we extract mfcc
    mfcc_features = librosa.feature.mfcc(y=audio, sr=sample_rate,n_mfcc=40)
    mfcc_features = 20 * np.log10(np.maximum( mfcc_features,1e-5))
    #inorder to find out scaled feature we do mean of transpose of value
    feature = normalize_frames(mfcc_features, Scale=False)
   # mfcc_scaled_features = np.mean(mfcc_features.T, axis=0)
    return feature
def normalize_frames(m,Scale=True):
    if Scale:
        return (m - np.mean(m, axis=0)) / (np.std(m, axis=0) + 2e-12)
    else:
        return (m - np.mean(m, axis=0))

# data_directory = "F:\speaker\Enroll"
# for files in os.listdir(data_directory):
#     data = features_extractor(os.path.join(data_directory , files))
print('yes')

   