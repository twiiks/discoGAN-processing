import os
from glob import glob
from tqdm import trange
from itertools import chain

import torch
from torch import nn
import torch.nn.parallel
import torchvision.utils as vutils
from torch.autograd import Variable

from models import *
from data_loader import get_loader


def weights_init(m):
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        m.weight.data.normal_(0.0, 0.02)
    elif classname.find('BatchNorm') != -1:
        m.weight.data.normal_(1.0, 0.02)
        m.bias.data.fill_(0)


class Tester(object):

    def __init__(self, config, a_data_loader, name_pth):
        self.config = config

        self.a_data_loader = a_data_loader

        self.num_gpu = config.num_gpu
        self.dataset = config.dataset

        self.loss = config.loss
        self.lr = config.lr
        self.beta1 = config.beta1
        self.beta2 = config.beta2
        self.optimizer = config.optimizer
        self.batch_size = config.batch_size
        self.weight_decay = config.weight_decay
        self.cnn_type = config.cnn_type

        self.model_dir = config.model_dir
        self.load_path = config.load_path

        self.start_step = 0
        self.log_step = config.log_step
        self.max_step = config.max_step
        self.save_step = config.save_step
        self.name_pth = name_pth

        self.build_model()

        if self.num_gpu == 1:
            self.G_AB.cuda()

        elif self.num_gpu > 1:
            self.G_AB = nn.DataParallel(
                self.G_AB.cuda(), device_ids=list(range(self.num_gpu)))

        if self.load_path:
            self.load_model()

    def build_model(self):
        a_height, a_width, a_channel = self.a_data_loader.shape

        if self.cnn_type == 0:
            #conv_dims, deconv_dims = [64, 128, 256, 512], [512, 256, 128, 64]
            conv_dims, deconv_dims = [64, 128, 256, 512], [256, 128, 64]
        elif self.cnn_type == 1:
            #conv_dims, deconv_dims = [32, 64, 128, 256], [256, 128, 64, 32]
            conv_dims, deconv_dims = [32, 64, 128, 256], [128, 64, 32]
        else:
            raise Exception(
                "[!] cnn_type {} is not defined".format(self.cnn_type))

        self.G_AB = GeneratorCNN(a_channel, a_channel, conv_dims, deconv_dims,
                                 self.num_gpu)
        self.G_AB.apply(weights_init)

    def load_model(self):
        print("[*] Load models from {}...".format(self.load_path))

        # paths = glob(os.path.join(self.load_path, '%s.pth' % name_pth))
        # paths.sort()

        # if len(paths) == 0:
        #     print("[!] No checkpoint found in {}...".format(self.load_path))
        #     return

        # idxes = [
        #     int(os.path.basename(path.split('.')[0].split('_')[-1]))
        #     for path in paths
        # ]
        # self.start_step = max(idxes)

        if self.num_gpu == 0:
            map_location = lambda storage, loc: storage
        else:
            map_location = None

        G_AB_filename = '{}/{}.pth'.format(self.load_path, self.name_pth)
        self.G_AB.load_state_dict(
            torch.load(G_AB_filename, map_location=map_location))

        print("[*] Model loaded: {}".format(G_AB_filename))
    
    def generate_with_A(self, inputs):
        x_AB = self.G_AB(inputs)
        return x_AB.data

    def test(self):
        batch_size = self.config.sample_per_image
        A_loader = iter(self.a_data_loader)

        x_A = self._get_variable(next(A_loader))
        img_AB = self.generate_with_A(x_A)
        return img_AB

    def _get_variable(self, inputs):
        if self.num_gpu > 0:
            out = Variable(inputs.cuda())
        else:
            out = Variable(inputs)
        return out
