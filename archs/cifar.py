import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
from operator import mul
# import numpy as np
# from utils import to_var
# from LayerNorm1d import LayerNorm1d

NUM_CHANNELS = 3


def compute_conv_output_size(input_size, kernel_size, padding, stride):
    return (input_size - kernel_size + 2 * padding) / stride + 1

class Disc_High(nn.Module):

    def __init__(self, batch_size):
        super(Disc_High, self).__init__()
        self.batch_size = batch_size
        
        # self.l1 = nn.Sequential(
        #     nn.Linear(nz, 32*16*16))

        self.l2 = nn.Sequential(
            nn.Conv2d(32, 128, kernel_size=5, padding=2, stride=1),
            nn.LeakyReLU(0.02),
            nn.Conv2d(128, 256, kernel_size=5, padding=2, stride=2),
            nn.LeakyReLU(0.02),
            nn.Conv2d(256, 1, kernel_size=1, padding=0, stride=1))

    def forward(self, z):
        # out = self.l1(z)
        z = z.view(self.batch_size, 32, 8, 8)
        out = self.l2(z)
        out = out.view(self.batch_size, -1)
        return out


class Gen_High(nn.Module):

    def __init__(self, batch_size, nz):
        super(Gen_High, self).__init__()
        self.batch_size = batch_size
        self.l1 = nn.Sequential(
            nn.Linear(nz, 32*4*4))
        self.l2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=5, padding=2, stride=1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.02),
            nn.Upsample(scale_factor=2),
            nn.Conv2d(64, 128, kernel_size=5, padding=2, stride=1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.02),
            nn.Conv2d(128, 32, kernel_size=5, padding=2, stride=1),
            nn.LeakyReLU(0.02))

    def forward(self, z):
        out = self.l1(z)
        out = out.view(self.batch_size, 32, 4, 4)
        out = self.l2(out)
        return out

class Disc_High2(nn.Module):

    def __init__(self, batch_size):
        super(Disc_High2, self).__init__()
        self.batch_size = batch_size
        
        # self.l1 = nn.Sequential(
        #     nn.Linear(nz, 32*16*16))

        self.l2 = nn.Sequential(
            nn.Conv2d(32, 128, kernel_size=5, padding=2, stride=1),
            nn.LeakyReLU(0.02),
            nn.Conv2d(128, 256, kernel_size=5, padding=2, stride=1),
            nn.LeakyReLU(0.02),
            nn.Conv2d(256, 512, kernel_size=5, padding=2, stride=2),
            nn.LeakyReLU(0.02),
            nn.Conv2d(512, 1, kernel_size=1, padding=0, stride=1))

    def forward(self, z):
        # out = self.l1(z)
        z = z.view(self.batch_size, 32, 8, 8)
        out = self.l2(z)
        out = out.view(self.batch_size, -1)
        return out


class Gen_High2(nn.Module):

    def __init__(self, batch_size, nz):
        super(Gen_High2, self).__init__()
        self.batch_size = batch_size
        self.l1 = nn.Sequential(
            nn.Linear(nz, 32*4*4))
        self.l2 = nn.Sequential(
            nn.Conv2d(32, 128, kernel_size=5, padding=2, stride=1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.02),
            nn.Upsample(scale_factor=2),
            nn.Conv2d(128, 256, kernel_size=5, padding=2, stride=1),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.02),
            nn.Conv2d(256, 32, kernel_size=5, padding=2, stride=1),
            nn.LeakyReLU(0.02))

    def forward(self, z):
        out = self.l1(z)
        out = out.view(self.batch_size, 32, 4, 4)
        out = self.l2(out)
        return out


class Inf_High(nn.Module):

    def __init__(self, batch_size, nz):
        super(Inf_High, self).__init__()
        self.batch_size = batch_size
        self.l1 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=5, padding=2, stride=1),
            nn.BatchNorm2d(64),
            nn.Conv2d(64, 128, kernel_size=5, padding=2, stride=2),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.02),
            nn.Conv2d(128, 32, kernel_size=5, padding=2, stride=1),
            nn.LeakyReLU(0.02))
        self.l2 = nn.Sequential(
            nn.Linear(32*4*4, nz))

    def forward(self, z):
        out = self.l1(z)
        out = out.view(self.batch_size, -1)
        out = self.l2(out)
        return out
    
    
class Inf_Low16(nn.Module):

    def __init__(self, batch_size, nz):
        super(Inf_Low16, self).__init__()

        self.batch_size = batch_size

        # self.l1 = nn.Sequential(
        #     nn.Conv2d(3, 64, kernel_size=5, padding=2, stride=2),
        #     nn.LeakyReLU(0.02),
        #     nn.Conv2d(64, 128, kernel_size=5, padding=2, stride=1),
        #     nn.LeakyReLU(0.02),
        #     nn.Conv2d(128, 256, kernel_size=5, padding=2, stride=2),
        #     nn.LeakyReLU(0.02),
        #     nn.Conv2d(256, 32, kernel_size=5, padding=2, stride=1),
        #     nn.LeakyReLU(0.02))
        self.l1 = nn.Sequential(
            nn.Conv2d(3, 128, kernel_size=5, padding=2, stride=2),
            nn.LeakyReLU(0.02),
            nn.Conv2d(128, 32, kernel_size=5, padding=2, stride=2),
            nn.LeakyReLU(0.02))

        self.l2 = nn.Sequential(
            nn.Linear(32*4*4, nz))

    def forward(self, x, take_pre=False):
        out = self.l1(x)
        if take_pre:
            return out
        out = out.view(self.batch_size, -1)
        out = self.l2(out)
        return out


class Gen_Low16(nn.Module):

    def __init__(self, batch_size, nz):
        super(Gen_Low16, self).__init__()
        self.batch_size = batch_size
        self.l1 = nn.Sequential(
            nn.Linear(nz, 32*4*4))
        self.l2 = nn.Sequential(
            nn.Upsample(scale_factor=2),
            nn.Conv2d(32, 128, kernel_size=5, padding=2, stride=1),
            nn.LeakyReLU(0.02),
            nn.Upsample(scale_factor=2),
            nn.Conv2d(128, NUM_CHANNELS, kernel_size=5, padding=2, stride=1),
            nn.Tanh())

    def forward(self, z, give_pre=False):
        if give_pre:
            out = z
        else:
            out = self.l1(z)
            out = out.view(self.batch_size,32,4,4)
        out = self.l2(out)
        return out


class Inf_Low_Med16(nn.Module):

    def __init__(self, batch_size, nz):
        super(Inf_Low_Med16, self).__init__()

        self.batch_size = batch_size

        self.l1 = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=5, padding=2, stride=1),
            # nn.BatchNorm2d(64),
            nn.LeakyReLU(0.02),
            nn.Conv2d(64, 128, kernel_size=5, padding=2, stride=2),
            # nn.BatchNorm2d(128),
            nn.LeakyReLU(0.02),
            nn.Conv2d(128, 64, kernel_size=5, padding=2, stride=1),
            # nn.BatchNorm2d(64),
            nn.LeakyReLU(0.02),
            nn.Conv2d(64, 64, kernel_size=5, padding=2, stride=2),
            nn.LeakyReLU(0.02))

        self.l2 = nn.Sequential(
            nn.Linear(64*4*4, nz))

    def forward(self, x, take_pre=False):
        out = self.l1(x)
        if take_pre:
            return out
        out = out.view(self.batch_size, -1)
        out = self.l2(out)
        return out


class Gen_Low_Med16(nn.Module):

    def __init__(self, batch_size, nz):
        super(Gen_Low_Med16, self).__init__()
        self.batch_size = batch_size
        self.l1 = nn.Sequential(
            nn.Linear(nz, 64*4*4))
        self.l2 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=5, padding=2, stride=1),
            # nn.BatchNorm2d(128),
            nn.LeakyReLU(0.02),
            nn.Upsample(scale_factor=2),
            nn.Conv2d(128, 128, kernel_size=5, padding=2, stride=1),
            # nn.BatchNorm2d(128),
            nn.LeakyReLU(0.02),
            nn.Conv2d(128, 64, kernel_size=5, padding=2, stride=1),
            # nn.BatchNorm2d(64),
            nn.LeakyReLU(0.02),
            nn.Upsample(scale_factor=2),
            nn.Conv2d(64, NUM_CHANNELS, kernel_size=5, padding=2, stride=1),
            nn.Tanh())

    def forward(self, z, give_pre=False):
        if give_pre:
            out = z
        else:
            out = self.l1(z)
            out = out.view(self.batch_size,64,4,4)
        out = self.l2(out)
        return out


class Inf_Low_Deep16(nn.Module):

    def __init__(self, batch_size, nz):
        super(Inf_Low_Deep16, self).__init__()

        self.batch_size = batch_size

        self.l1 = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=5, padding=1, stride=1),
            nn.LeakyReLU(0.02),
            nn.Conv2d(32, 64, kernel_size=5, padding=1, stride=1),
            nn.LeakyReLU(0.02),
            nn.Conv2d(64, 128, kernel_size=5, padding=2, stride=2),
            nn.LeakyReLU(0.02),
            nn.Conv2d(128, 256, kernel_size=5, padding=2, stride=1),
            nn.LeakyReLU(0.02),
            nn.Conv2d(256, 32, kernel_size=5, padding=1, stride=1),
            nn.LeakyReLU(0.02))

        self.l2 = nn.Sequential(
            nn.Linear(32*4*4, nz))

    def forward(self, x, take_pre=False):
        out = self.l1(x)
        if take_pre:
            return out
        out = out.view(self.batch_size, -1)
        out = self.l2(out)
        return out


class Gen_Low_Deep16(nn.Module):
    def __init__(self, batch_size, nz):
        super(Gen_Low_Deep16, self).__init__()
        self.batch_size = batch_size
        self.l1 = nn.Sequential(
            nn.Linear(nz, 32*4*4))
        self.l2 = nn.Sequential(
            nn.Conv2d(32, 128, kernel_size=5, padding=2, stride=1),
            nn.LeakyReLU(0.02),
            nn.Conv2d(128, 256, kernel_size=5, padding=2, stride=1),
            nn.LeakyReLU(0.02),
            nn.Upsample(scale_factor=2),

            nn.Conv2d(256, 128, kernel_size=5, padding=2, stride=1),
            nn.LeakyReLU(0.02),
            nn.Conv2d(128, 64, kernel_size=5, padding=2, stride=1),
            nn.LeakyReLU(0.02),
            nn.Upsample(scale_factor=2),

            nn.Conv2d(64, 32, kernel_size=5, padding=2, stride=1),
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


class Disc_Low(nn.Module):
    def __init__(self, batch_size, nx, nz):
        super(Disc_Low, self).__init__()
        self.batch_size = batch_size
        self.nconv1 = compute_conv_output_size(nx, 5, 2, 2)
        self.nconv2 = compute_conv_output_size(self.nconv1, 5, 2, 2)
        self.nconv3 = compute_conv_output_size(self.nconv2, 5, 2, 2)

        self.zo2 = nn.Sequential(
            nn.Linear(nz, 512),
            nn.LeakyReLU(0.02),
            nn.Linear(512, 256 * self.nconv2 * self.nconv2),
            nn.LeakyReLU(0.02))

        self.zo3 = nn.Sequential(
            nn.Linear(nz, 512),
            nn.LeakyReLU(0.02),
            nn.Linear(512, 512 * self.nconv3 * self.nconv3),
            nn.LeakyReLU(0.02))

        self.l1 = nn.Sequential(
            nn.Conv2d(NUM_CHANNELS, 128, kernel_size=5, padding=2, stride=2),
            nn.LeakyReLU(0.02))
        self.l2 = nn.Sequential(
            nn.Conv2d(128, 256, kernel_size=5, padding=2, stride=2),
            nn.LeakyReLU(0.02))

        # self.l3 = nn.Sequential(
        #     nn.Conv2d(256, 512, kernel_size=5, padding=2, stride=2),
        #     nn.LeakyReLU(0.02))

        self.l_end = nn.Sequential(
            nn.Conv2d(256, 1, kernel_size=5, padding=2, stride=2))

    # def forward(self, x):
    def forward(self, x, z):

        zo2 = self.zo2(z).view(self.batch_size, 256, self.nconv2, self.nconv2)
        # zo3 = self.zo3(z).view(self.batch_size, 512, self.nconv3, self.nconv3)

        out = self.l1(x)
        out = self.l2(out) + zo2
        # out = self.l3(out) + zo3
        # out = self.l2(out)
        # out = self.l3(out)
        out = self.l_end(out)
        out = out.view(self.batch_size, -1)
        return out


FC_DIM = 2048
class Gen_High_fc(nn.Module):
    def __init__(self, batch_size, nz, no):
        super(Gen_High_fc, self).__init__()

        self.batch_size = batch_size
        self.l1 = nn.Sequential(
            nn.Linear(nz, FC_DIM),
            nn.BatchNorm1d(FC_DIM),
            nn.LeakyReLU(0.02),
            nn.Linear(FC_DIM, FC_DIM),
            nn.BatchNorm1d(FC_DIM),
            nn.LeakyReLU(0.02),
            nn.Linear(FC_DIM, no))

    def forward(self, z):
        z = z.view(self.batch_size, -1)
        out = self.l1(z)
        return out

class Inf_High_fc(nn.Module):
    def __init__(self, batch_size, nz, no):
        super(Inf_High_fc, self).__init__()

        self.batch_size = batch_size
        self.l1 = nn.Sequential(
            nn.Linear(nz, FC_DIM),
            nn.BatchNorm1d(FC_DIM),
            nn.LeakyReLU(0.02),
            nn.Linear(FC_DIM, FC_DIM),
            nn.BatchNorm1d(FC_DIM),
            nn.LeakyReLU(0.02),
            nn.Linear(FC_DIM, no))

    def forward(self, z):
        z = z.view(self.batch_size, -1)
        out = self.l1(z)
        return out
    
class Disc_High_fc(nn.Module):
    def __init__(self, batch_size, nz):
        super(Disc_High_fc, self).__init__()

        self.batch_size = batch_size
        self.l1 = nn.Sequential(
            nn.Linear(nz, FC_DIM),
            nn.BatchNorm1d(FC_DIM),
            nn.LeakyReLU(0.02),
            nn.Linear(FC_DIM, FC_DIM),
            nn.BatchNorm1d(FC_DIM),
            nn.LeakyReLU(0.02),
            nn.Linear(FC_DIM, 1))

    def forward(self, z):
        z = z.view(self.batch_size, -1)
        out = self.l1(z)
        return out
