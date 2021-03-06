import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from utils import to_var
from LayerNorm1d import LayerNorm1d

class Gen_Bot(nn.Module):

    def __init__(self, batch_size, nz, nh, no):
        super(Gen_Bot, self).__init__()

        norm = nn.BatchNorm1d

        self.batch_size = batch_size
        self.nz = nz
        self.l1 = nn.Linear(nz, nh)
        #self.bn1 = norm(nh)
        self.a1 = nn.LeakyReLU(0.02)
        self.l2 = nn.Linear(nh,nh)
        #self.bn2 = norm(nh)
        self.a2 = nn.LeakyReLU(0.02)
        self.l3 = nn.Linear(nh, no)
        self.a3 = nn.Tanh()

    def forward(self, z):
        out = self.l1(z)
        out = self.a1(out)
        out = self.l2(out)
        out = self.a2(out)
        out = self.l3(out)
        out = self.a3(out)
        return out




class Gen_Bot_Conv(nn.Module):
    def __init__(self, batch_size, nz):
        super(Gen_Bot_Conv, self).__init__()
        norm = LayerNorm1d
        self.batch_size = batch_size
        self.nz = nz
        self.l1 = nn.Sequential(
            nn.Linear(nz*2, 512*4*4))
        self.l2 = nn.Sequential(
            nn.UpsamplingBilinear2d(scale_factor=2),
            nn.Conv2d(512, 256, kernel_size=3, padding=1, stride=1),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2),
            nn.Conv2d(256, 256, kernel_size=3, padding=1, stride=1),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2),
            nn.UpsamplingBilinear2d(scale_factor=2),
            nn.Conv2d(256, 128, kernel_size=5, padding=2, stride=1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2),
            nn.Conv2d(128, 128, kernel_size=5, padding=2, stride=1,dilation=1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2),
            nn.UpsamplingBilinear2d(scale_factor=2),
            nn.Conv2d(128, 64, kernel_size=5, padding=2, stride=1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.2),
            nn.Conv2d(64, 64, kernel_size=5, padding=2, stride=1,dilation=1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.2),
            nn.UpsamplingBilinear2d(scale_factor=2),
            nn.Conv2d(64, 64, kernel_size=5, padding=2, stride=1),
            nn.LeakyReLU(0.2),
            nn.Conv2d(64, 1, kernel_size=5, padding=2, stride=1),
            nn.Tanh())
    def forward(self, z):
        z_extra = to_var(torch.randn(self.batch_size, self.nz))
        out = self.l1(torch.cat((z,1.0*z_extra), 1))
        out = out.view(100,512,4,4)
        out = self.l2(out)
        return out


class Gen_Bot_Conv32(nn.Module):
    def __init__(self, batch_size,nz):
        super(Gen_Bot_Conv32, self).__init__()
        self.batch_size = batch_size
        self.l1 = nn.Sequential(
            nn.Linear(nz, 512*4*4))
        self.l2 = nn.Sequential(
            nn.Conv2d(512, 256, kernel_size=5, padding=2, stride=1),
            nn.BatchNorm2d(256),
            nn.UpsamplingBilinear2d(scale_factor=2),
            nn.LeakyReLU(0.02),
            nn.Conv2d(256, 128, kernel_size=5, padding=2, stride=1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.02),
            nn.UpsamplingBilinear2d(scale_factor=2),
            nn.Conv2d(128, 64, kernel_size=5, padding=2, stride=1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.02),
            nn.UpsamplingBilinear2d(scale_factor=2),
            nn.Conv2d(64, 3, kernel_size=5, padding=2, stride=1),
            nn.Tanh())
    def forward(self, z, give_pre=False):
        if give_pre:
            out = z
        else:
            out = self.l1(z)
            out = out.view(self.batch_size,512,4,4)
        out = self.l2(out)
        return out


class Gen_Bot_Conv32_deep1(nn.Module):
    def __init__(self, batch_size,nz):
        super(Gen_Bot_Conv32_deep1, self).__init__()
        self.batch_size = batch_size
        self.l1 = nn.Sequential(
            nn.Linear(nz, 512*4*4))
        self.l2 = nn.Sequential(
            nn.Conv2d(512, 256, kernel_size=5, padding=2, stride=1),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.02),
            nn.Upsample(scale_factor=2),
            nn.Conv2d(256, 128, kernel_size=5, padding=2, stride=1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.02),
            nn.Conv2d(128, 64, kernel_size=5, padding=2, stride=1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.02),

            nn.Upsample(scale_factor=2),
            nn.Conv2d(64, 32, kernel_size=5, padding=2, stride=1),
            nn.BatchNorm2d(32),
            nn.LeakyReLU(0.02),

            nn.Upsample(scale_factor=2),
            nn.Conv2d(32, 32, kernel_size=5, padding=2, stride=1),
            nn.BatchNorm2d(32),
            nn.LeakyReLU(0.02),
            nn.Conv2d(32, 32, kernel_size=1, padding=0, stride=1),
            nn.BatchNorm2d(32),
            nn.LeakyReLU(0.02),
            nn.Conv2d(32, 3, kernel_size=1, padding=0, stride=1),
            nn.Tanh())
    def forward(self, z, give_pre=False):
        if give_pre:
            out = z
        else:
            out = self.l1(z)
            out = out.view(self.batch_size,512,4,4)
        out = self.l2(out)
        return out

class Gen_Bot_Conv32_deepbottleneck(nn.Module):
    def __init__(self, batch_size,nz):
        super(Gen_Bot_Conv32_deepbottleneck, self).__init__()
        self.batch_size = batch_size
        self.l1 = nn.Sequential(
            nn.Linear(nz, 32*4*4))
        self.l2 = nn.Sequential(
            nn.Conv2d(32, 256, kernel_size=5, padding=2, stride=1),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.02),
            nn.Upsample(scale_factor=2),
            nn.Conv2d(256, 128, kernel_size=5, padding=2, stride=1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.02),
            nn.Conv2d(128, 64, kernel_size=5, padding=2, stride=1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.02),

            nn.Upsample(scale_factor=2),
            nn.Conv2d(64, 32, kernel_size=5, padding=2, stride=1),
            nn.BatchNorm2d(32),
            nn.LeakyReLU(0.02),

            nn.Upsample(scale_factor=2),
            nn.Conv2d(32, 32, kernel_size=5, padding=2, stride=1),
            nn.BatchNorm2d(32),
            nn.LeakyReLU(0.02),
            nn.Conv2d(32, 32, kernel_size=1, padding=0, stride=1),
            nn.BatchNorm2d(32),
            nn.LeakyReLU(0.02),
            nn.Conv2d(32, 3, kernel_size=1, padding=0, stride=1),
            nn.Tanh())
    def forward(self, z, give_pre=False):
        if give_pre:
            out = z
        else:
            out = self.l1(z)
            out = out.view(self.batch_size,32,4,4)
        out = self.l2(out)
        return out


