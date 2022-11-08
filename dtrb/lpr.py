import string
import argparse
import types

import torch
import torch.backends.cudnn as cudnn
import torch.utils.data
import torch.nn.functional as F

from dtrb.utils import CTCLabelConverter, AttnLabelConverter
from dtrb.dataset import RawDataset, AlignCollate
from dtrb.OCRmodel import Model

import os
from datetime import datetime
import pandas as pd
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
class W_LPR(object):

    def load_ocr():
        
        opt = argparse.Namespace(workers = 4,batch_size = 192,saved_model = f'dtrb/models/best_accuracy.pth',batch_max_length = 25,
        imgH = 32, imgW = 100, character = '0123456789가나다라마거너더러머버서어저고노도로모보소오조구누두루무부수우주아바사자하허호배',
        Transformation = 'TPS', FeatureExtraction = 'VGG', SequenceModeling = 'BiLSTM', Prediction = 'CTC',
        num_fiducial = 20, input_channel = 1, output_channel = 256,hidden_size = 256)

        model = Model(opt)
        model = torch.nn.DataParallel(model).to(device)

        # load model
        print('모델 불러오는중...')
        model.load_state_dict(torch.load(r'models/best_accuracy.pth', map_location=device))

        return model.eval()

    def read_ocr(model,img):
        length_for_pred = torch.IntTensor([25] * 192).to(device)
        text_for_pred = torch.LongTensor(192, 26).fill_(0).to(device)
        preds = model(img, text_for_pred)
        preds_size = torch.IntTensor([preds.size(1)] * 192)
        _, preds_index = preds.max(2)

        preds_str = CTCLabelConverter.decode((preds_index, length_for_pred))
        return preds_str

class CTCLabelConverter(object):
    """ Convert between text-label and text-index """

    def __init__(self, character):
        # character (str): set of the possible characters.
        dict_character = list(character)

        self.dict = {}
        for i, char in enumerate(dict_character):
            # NOTE: 0 is reserved for 'CTCblank' token required by CTCLoss
            self.dict[char] = i + 1

        self.character = ['[CTCblank]'] + dict_character  # dummy '[CTCblank]' token for CTCLoss (index 0)

    def encode(self, text, batch_max_length=25):
        """convert text-label into text-index.
        input:
            text: text labels of each image. [batch_size]
            batch_max_length: max length of text label in the batch. 25 by default

        output:
            text: text index for CTCLoss. [batch_size, batch_max_length]
            length: length of each text. [batch_size]
        """
        length = [len(s) for s in text]

        # The index used for padding (=0) would not affect the CTC loss calculation.
        batch_text = torch.LongTensor(len(text), batch_max_length).fill_(0)
        for i, t in enumerate(text):
            text = list(t)
            text = [self.dict[char] for char in text]
            batch_text[i][:len(text)] = torch.LongTensor(text)
        return (batch_text.to(device), torch.IntTensor(length).to(device))

    def decode(self, text_index, length):
        """ convert text-index into text-label. """
        texts = []
        for index, l in enumerate(length):
            t = text_index[index, :]

            char_list = []
            for i in range(l):
                if t[i] != 0 and (not (i > 0 and t[i - 1] == t[i])):  # removing repeated characters and blank.
                    char_list.append(self.character[t[i]])
            text = ''.join(char_list)

            texts.append(text)
        return texts