'''
EffNet: AN EFFICIENT STRUCTURE FOR CONVOLUTIONAL NEURAL NETWORKS
Implementation in Pytorch of Effnet.
https://arxiv.org/abs/1801.06434

'''
import torch
import torch.nn as nn

from tsanley.dynamic import init_analyzer
from tsalib import dim_vars

B, C = dim_vars('Batch(b):20 Channels(c):3')
H, W = dim_vars('Height(h):32 Width(w):32')
N = dim_vars('Nclass(n):10')

class Flatten(nn.Module):
    def forward(self, x):
        x = x.view(x.size()[0], -1)
        return x
     
class EffNet(nn.Module):

    def __init__(self, nb_classes=10, include_top=True, weights=None):
        super(EffNet, self).__init__()
        
        self.block1 = self.make_layers(32, 64)
        self.block2 = self.make_layers(64, 128)
        self.block3 = self.make_layers(128, 256)
        self.flatten = Flatten()
        self.linear = nn.Linear(4096, nb_classes)
        self.include_top = include_top
        self.weights = weights

    def make_layers(self, ch_in, ch_out):
        layers = [
            nn.Conv2d(3, ch_in, kernel_size=(1,1), stride=(1,1), bias=False, padding=0, dilation=(1,1)) 
            if ch_in ==32 else 
            nn.Conv2d(ch_in, ch_in, kernel_size=(1,1),stride=(1,1), bias=False, padding=0, dilation=(1,1)) ,
            self.make_post(ch_in),
            # DepthWiseConvolution2D
            nn.Conv2d(ch_in, 1 * ch_in, groups=ch_in, kernel_size=(1, 3),stride=(1,1), padding=(0,1), bias=False, dilation=(1,1)),
            self.make_post(ch_in),
            nn.MaxPool2d(kernel_size=(2,1), stride=(2,1)),
            # DepthWiseConvolution2D
            nn.Conv2d(ch_in, 1 * ch_in, groups=ch_in, kernel_size=(3, 1), stride=(1,1), padding=(1,0), bias=False, dilation=(1,1)),
            self.make_post(ch_in),
            nn.Conv2d(ch_in, ch_out, kernel_size=(1, 2), stride=(1, 2), bias=False, padding=(0,0), dilation=(1,1)),
            self.make_post(ch_out),
        ]
        return nn.Sequential(*layers)

    def make_post(self, ch_in):
        layers = [
            nn.LeakyReLU(0.3),
            nn.BatchNorm2d(ch_in, momentum=0.99)
        ]
        return nn.Sequential(*layers)

    def forward(self, x):
        x: 'bchw'
        x: 'b,64,h//2,w//2' = self.block1(x)
        x: 'b,128,h//4,w//4' = self.block2(x)
        x: 'b,256,h//8,w//8' = self.block3(x)
        if self.include_top:
            x: 'b,4096' = self.flatten(x)
            x: 'b,n' = self.linear(x)
        return x



def test_effnet ():
    eff = EffNet()
    x: 'bchw' = torch.ones(B, C, H, W)
    init_analyzer(['EffNet.forward'])
    out = eff.forward(x)
    print (out.size())

if __name__ == '__main__':
    test_effnet()