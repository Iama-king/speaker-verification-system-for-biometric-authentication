import torch
import torch.nn.functional as F
from torch.autograd import Variable

import pandas as pd
import math
import os
import configure as c
import matplotlib.pyplot as p
from DB_wav_reader import read_feats_structure
from SR_Dataset import read_MFB, ToTensorTestInput
from model.model import background_resnet

def load_model(use_cuda, log_dir, cp_num, embedding_size, n_classes):
    model = background_resnet(embedding_size=embedding_size, num_classes=n_classes)
    if use_cuda:
        model.cuda()
    print('=> loading checkpoint')
    # original saved file with DataParallel
    map_location = 'cuda' if use_cuda else 'cpu'
    checkpoint = torch.load(log_dir + '/checkpoint_' + str(cp_num) + '.pth', map_location=map_location)
    # create new OrderedDict that does not contain `module.`
    model.load_state_dict(checkpoint['state_dict'])
    model.eval()
    return model

def split_enroll_and_test(dataroot_dir):
    DB_all = read_feats_structure(dataroot_dir)
    enroll_DB = pd.DataFrame()
    test_DB = pd.DataFrame()
    
    enroll_DB = DB_all[DB_all['filename'].str.contains('enroll.p')]
    test_DB = DB_all[DB_all['filename'].str.contains('test.p')]
    
    # Reset the index
    enroll_DB = enroll_DB.reset_index(drop=True)
    test_DB = test_DB.reset_index(drop=True)
    return enroll_DB, test_DB

def load_enroll_embeddings(embedding_dir, use_cuda=False):
    embeddings = {}
    map_location = 'cuda' if use_cuda else 'cpu'  # embeddings were saved as CUDA tensors; remap for CPU-only machines
    for f in os.listdir(embedding_dir):
        spk = f.replace('.pth','')
        # Select the speakers who are in the 'enroll_spk_list'
        embedding_path = os.path.join(embedding_dir, f)
        tmp_embeddings = torch.load(embedding_path, map_location=map_location)
        embeddings[spk] = tmp_embeddings

    return embeddings

def get_embeddings(use_cuda, filename, model, test_frames):
    input, label = read_MFB(filename) # input size:(n_frames, n_dims)
    
    tot_segments = math.ceil(len(input)/test_frames) # total number of segments with 'test_frames' 
    activation = 0
    with torch.no_grad():
        for i in range(tot_segments):
            temp_input = input[i*test_frames:i*test_frames+test_frames]
            
            TT = ToTensorTestInput()
            temp_input = TT(temp_input) # size:(1, 1, n_dims, n_frames)
    
            if use_cuda:
                temp_input = temp_input.cuda()
            temp_activation,_ = model(temp_input)
            activation += torch.sum(temp_activation, dim=0, keepdim=True)
    
    activation = l2_norm(activation, 1)
                
    return activation

def l2_norm(input, alpha):
    input_size = input.size()  # size:(n_frames, dim)
    buffer = torch.pow(input, 2)  # 2 denotes a squared operation. size:(n_frames, dim)
    normp = torch.sum(buffer, 1).add_(1e-10)  # size:(n_frames)
    norm = torch.sqrt(normp)  # size:(n_frames)
    _output = torch.div(input, norm.view(-1, 1).expand_as(input))
    output = _output.view(input_size)
    # Multiply by alpha = 10 as suggested in https://arxiv.org/pdf/1703.09507.pdf
    output = output * alpha
    return output

def perform_verification(use_cuda, model, embeddings, enroll_speaker, test_filename, test_frames, thres):
    enroll_embedding = embeddings[enroll_speaker]
    test_embedding = get_embeddings(use_cuda, test_filename, model, test_frames)
    print(test_filename)
    print(test_embedding)
    score = F.cosine_similarity(test_embedding, enroll_embedding)
    score = score.data.cpu().numpy() 

    if score > thres:
        result = 'Accept'
    else:
        result = 'Reject'
        
    test_spk = os.path.basename(test_filename).split('_')[0]
    print("\n=== Speaker verification ===")
    print("True speaker: %s\nClaimed speaker : %s\n\nResult : %s\n" %(enroll_speaker, test_spk, result))
    print("Score : %0.4f\nThreshold : %0.2f\n" %(score, thres))
    return score,result

def main(enroll_speaker='103F3021', test_speaker='103F3021', fname='test.p',
         test_dir=c.TEST_FEAT_DIR, thres=0.96):

    log_dir = 'model_saved'              # Where the checkpoints are saved
    embedding_dir = 'enroll_embeddings'  # Where enrolled speaker embeddings are saved
    # test_dir defaults to the repo-relative feature dir from configure.py
    # (feat_logfbank_nfilt40/test), laid out as <test_dir>/<speaker>/<filename>.

    # Settings
    use_cuda = torch.cuda.is_available()  # Auto-detect GPU; falls back to CPU
    embedding_size = 128  # Dimension of speaker embeddings
    cp_num = 13            # Lowest-EER checkpoint of 40 evaluated on a 31-speaker set
                            # (10 bundled + 21 real enrolled speakers) — see
                            # docs/PROJECT_ANALYSIS.md and docs/eer_plot.png.
    n_classes = 240       # How many speakers in training data?
    test_frames = 100     # Split the test utterance

    # Load model from checkpoint
    model = load_model(use_cuda, log_dir, cp_num, embedding_size, n_classes)

    # Load enroll embeddings
    embeddings = load_enroll_embeddings(embedding_dir, use_cuda)

    # Threshold for accept/reject, set at the EER point (~0.96) measured across a realistic,
    # accent-diverse 31-speaker set — NOT the ~0.89 you'd get from the bundled 10 speakers
    # alone, which understates real-world error rate. See docs/PROJECT_ANALYSIS.md: this model
    # is noticeably less discriminative between speakers whose accent doesn't match its training
    # data. Re-derive for your own population before production use.
    test_path = os.path.join(test_dir, test_speaker, fname)

    # Perform the test
    s, r = perform_verification(use_cuda, model, embeddings, enroll_speaker, test_path, test_frames, thres)
    return s, r

if __name__ == '__main__':
    # Example: does speaker '103F3021's test utterance match the enrolled '103F3021'?
    # (Uses one of the bundled anonymized dataset speakers so this runs out-of-the-box on a fresh
    # clone; swap in your own speaker name once you've enrolled one with enroll.py.)
    enroll_speaker = "103F3021"
    test_speaker = '103F3021'
    fname = 'test.p'
    score, result = main(enroll_speaker, test_speaker, fname)