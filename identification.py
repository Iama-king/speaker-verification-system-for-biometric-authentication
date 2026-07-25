import torch
import torch.nn.functional as F
from torch.autograd import Variable

import pandas as pd
import math
import os
import configure as c

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

def perform_identification(use_cuda, model, embeddings, test_filename, test_frames, spk_list):
    test_embedding = get_embeddings(use_cuda, test_filename, model, test_frames)
    max_score = -10**8
    best_spk = None
    for spk in spk_list:
        score = F.cosine_similarity(test_embedding, embeddings[spk])
        score = score.data.cpu().numpy() 
        if score > max_score:
            max_score = score
            best_spk = spk
    print(test_filename)
    print("Speaker identification result : %s" %best_spk)
    true_spk = os.path.basename(os.path.dirname(test_filename)).split('_')[0]
    print("\n=== Speaker identification ===")
    print("True speaker : %s\nPredicted speaker : %s\nResult : %s\n" %(true_spk, best_spk, true_spk==best_spk))
    print("matched percent")
    print(max_score)
    return max_score,best_spk

def main(test_speaker='103F3021', filename='test.p', test_dir=c.TEST_FEAT_DIR):

    log_dir = 'model_saved'          # Where the checkpoints are saved
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

    # Load enroll embeddings; the enrolled speakers form the identification gallery
    embeddings = load_enroll_embeddings(embedding_dir, use_cuda)
    spk_list = list(embeddings.keys())

    # Set the test utterance path: <test_dir>/<speaker>/<filename>
    test_path = os.path.join(test_dir, test_speaker, filename)

    # Perform the test
    sc, best_spk = perform_identification(use_cuda, model, embeddings, test_path, test_frames, spk_list)
    return sc, best_spk

if __name__ == '__main__':
    # Example: identify the 'test.p' utterance of speaker '103F3021' against all enrolled speakers.
    # (Uses one of the bundled anonymized dataset speakers so this runs out-of-the-box on a fresh
    # clone; swap in your own speaker name once you've enrolled one with enroll.py.)
    test_speaker = '103F3021'
    filename = "test.p"
    main(test_speaker, filename)