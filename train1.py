import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
import time
import os
import numpy as np
import configure as c
import pandas as pd
from DB_wav_reader import read_feats_structure
from SR_Dataset import read_MFB, TruncatedInputfromMFB, ToTensorInput, ToTensorDevInput, DvectorDataset, collate_fn_feat_padded
from model.model import background_resnet
import matplotlib.pyplot as plt

def load_data(val_ratio):
    train_db,valid_db=train_val_split(c.TRAIN_FEAT_DIR, val_ratio)
    file_loader = read_MFB
    n_class=0
    return train_data, valid_data,n_class
def train_val_split(dir,ratio):

def main():
    val_ratio=10
    #load data set
    tds,vds,nclass=load_data(val_ratio)
    log_dir="model_saved"



if __name__ == '__main__':
    main()