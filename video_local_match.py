#!/usr/bin/env python
import torch
import torchvision
import torch.nn as nn
import numpy as np
import torch.utils.data as data
import torchvision.transforms as transforms
import torchvision.datasets as datasets
from torch.autograd import Variable, grad
from torchvision.utils import save_image
import os
slurm_name = os.environ["SLURM_JOB_ID"]
from utils import to_var
from LayerNorm1d import LayerNorm1d
from gradient_penalty import gradient_penalty
import random
import numpy as np

'''
Initially just implement LSGAN on MNIST.  

Then implement a critic.  
'''


def denorm(x):
    out = (x+1)/2
    return out.clamp(0,1)

batch_size = 100

real_labels = to_var(torch.ones(batch_size))
fake_labels = to_var(torch.zeros(batch_size))
boundary_labels = to_var(0.5 * torch.ones(batch_size))

#transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize(mean=(0.5,0.5,0.5), std=(0.5,0.5,0.5))])

#mnist = datasets.MNIST(root='./data/', train=True, download=True, transform=transform)

#data_loader = torch.utils.data.DataLoader(dataset=mnist, batch_size=batch_size, shuffle=True)

mnist = np.load('/u/lambalex/Downloads/mnist_test_seq.npy').astype('float32')

nz = 64
ns = 8

print "ns", ns

#(zL,xL) and (zR,xR)
d_bot = nn.Sequential(
    nn.Linear(784/ns + nz*0, 256),
    nn.LeakyReLU(0.2),
    nn.Linear(256, 256),
    nn.LeakyReLU(0.2),
    nn.Linear(256, 1))

from D_Top import D_Top
d_top = D_Top(batch_size, nz*ns, nz, 256)


from Inf_Bot import Inf_Bot
inf_bot = Inf_Bot(batch_size, nz)

#(zL->xL) and (zR->xR)
from Gen_Bot import Gen_Bot
gen_bot = Gen_Bot(batch_size, nz, 256, 784/ns)

#(zL,zR -> z)
inf_top = nn.Sequential(
    nn.Linear(nz*ns, 256),
    nn.BatchNorm1d(256),
    nn.LeakyReLU(0.2),
    nn.Linear(256, 256),
    nn.BatchNorm1d(256),
    nn.LeakyReLU(0.2),
    nn.Linear(256, nz))

from Gen_Top import Gen_Top
gen_top = Gen_Top(batch_size, nz, 256, ns*nz)

models = [d_top, d_bot, inf_bot, gen_bot, inf_top, gen_top]

if torch.cuda.is_available():
    for model in models: 
        model.cuda()

d_top_optimizer = torch.optim.Adam(d_top.parameters(), lr=0.0003)
d_bot_optimizer = torch.optim.Adam(d_bot.parameters(), lr=0.0003)
inf_bot_optimizer = torch.optim.Adam(inf_bot.parameters(), lr=0.0003)
gen_bot_optimizer = torch.optim.Adam(gen_bot.parameters(), lr=0.0003)
inf_top_optimizer = torch.optim.Adam(inf_top.parameters(), lr=0.0003)
gen_top_optimizer = torch.optim.Adam(gen_top.parameters(), lr=0.0003)


for epoch in range(200):
    for i in range(0,10000-batch_size):

        images = torch.from_numpy(mnist[:,i:i+batch_size,:,:])

        #====
        #Inference Procedure
        #====

        images = to_var(images)

        z_bot_lst = []
        for seg in range(0,ns):
            xs = images[seg]#images[:,seg*(784/ns):(seg+1)*(784/ns)]
            
            xs = xs.view(100,1,64,64)
            zs = inf_bot(xs)

            d_out_bot = d_bot(xs)

            d_loss_bot = ((d_out_bot - real_labels)**2).mean()
            g_loss_bot = 1.0 * ((d_out_bot - boundary_labels)**2).mean()

            print "d loss bot inf", d_loss_bot

            reconstruction = gen_bot(zs)
            rec_loss = ((reconstruction - xs)**2).mean()

            if True:
                g_loss_bot += rec_loss
                print "training with reconstruction loss"
            else:
                print "training without low level reconstruction loss"
            
            print "reconstruction loss", rec_loss

            d_bot.zero_grad()
            d_loss_bot.backward(retain_graph=True)
            d_bot_optimizer.step()

            gen_bot.zero_grad()
            inf_bot.zero_grad()
            d_bot.zero_grad()
            g_loss_bot.backward(retain_graph=True)
            
            if random.uniform(0,1) < 0.1:
                gen_bot_optimizer.step()
                inf_bot_optimizer.step()

            z_bot_lst.append(zs)

        z_bot = torch.cat(z_bot_lst, 1)

        z_bot = Variable(z_bot.data)

        z_top = inf_top(z_bot)

        z_bot_rec = gen_top(z_top)

        reconstruction_loss = ((z_bot - z_bot_rec)**2).mean()

        print "high level rec loss", reconstruction_loss

        d_out_top = d_top(z_bot)

        d_loss_top = ((d_out_top - real_labels)**2).mean()
        g_loss_top = ((d_out_top - boundary_labels)**2).mean()

        print "d loss top inf", d_loss_top

        #d_loss_top += 0.1 * gradient_penalty(d_out_top.norm(2), z_bot)

        if True:
            print "optimizing for high level rec loss"
            g_loss_top += reconstruction_loss
        else:
            print "not optimizing high level rec loss"

        d_top.zero_grad()
        d_loss_top.backward(retain_graph=True)
        d_top_optimizer.step()

        inf_top.zero_grad()
        gen_top.zero_grad()
        d_top.zero_grad()
        g_loss_top.backward(retain_graph=True)
        inf_top_optimizer.step()
        gen_top_optimizer.step()

        print "epoch", epoch
        #============GENERATION PROCESS========================$

        z_top = to_var(torch.randn(batch_size, nz))

        z_bot = gen_top(z_top)

        d_out_top = d_top(z_bot)

        d_top.zero_grad()

        d_loss_top = ((d_out_top - fake_labels)**2).mean()
        
        d_loss_top.backward(retain_graph=True)
        d_top_optimizer.step()

        print "d loss top gen", d_loss_top

        g_loss_top = 1.0 * ((d_out_top - boundary_labels)**2).mean()
        gen_top.zero_grad()
        d_top.zero_grad()
        g_loss_top.backward(retain_graph=True)
        gen_top_optimizer.step()

        z_bot = Variable(z_bot.data)

        gen_x_lst = []
        for seg in range(0,ns):
            seg_z = z_bot[:,seg*nz:(seg+1)*nz]*1.0 + 0.0*to_var(torch.randn(batch_size, nz))
            seg_x = gen_bot(seg_z)

            gen_x_lst.append(seg_x)
            d_out_bot = d_bot(torch.cat((seg_x,),1))
            d_loss_bot = ((d_out_bot - fake_labels)**2).mean()
            
            print "d loss bot gen", d_loss_bot

            d_bot.zero_grad()
            d_loss_bot.backward(retain_graph=True)
            d_bot_optimizer.step()

            print "train with less g loss bot"
            g_loss_bot = 1.0 * ((d_out_bot - boundary_labels)**2).mean()
            gen_bot.zero_grad()
            d_bot.zero_grad()
            g_loss_bot.backward(retain_graph=True)
            if random.uniform(0,1) < 0.1:
                gen_bot_optimizer.step()

        #print d_out_bot

    fake_images = torch.cat(gen_x_lst, 1)

    fake_images = fake_images.view(fake_images.size(0), 1, 28, 28)
    save_image(denorm(fake_images.data), './data/%s_fake_images.png' %(slurm_name))

    
    real_images = images.view(images.size(0), 1, 28, 28)
    save_image(denorm(real_images.data), './data/%s_real_images.png' %(slurm_name))

    
    #z_bot_lst = []
    x_bot_lst = []
    z_bot_lst = []
    for seg in range(0,ns):
        xs = images[:,seg*(784/ns):(seg+1)*(784/ns)]
        zs = inf_bot(xs)
        xr = gen_bot(zs)
        x_bot_lst.append(xr)
        z_bot_lst.append(zs)

    rec_images_bot = torch.cat(x_bot_lst, 1)

    rec_images_bot = rec_images_bot.view(rec_images_bot.size(0), 1, 28, 28)
    save_image(denorm(rec_images_bot.data), './data/%s_rec_images_bot.png' %(slurm_name))

    z_bot = torch.cat(z_bot_lst, 1)
    z_top = inf_top(z_bot)
    z_bot = gen_top(z_top)

    gen_x_lst = []
    for seg in range(0,ns):
        seg_z = z_bot[:,seg*nz:(seg+1)*nz]
        gen_x_lst.append(gen_bot(seg_z))

    rec_images_top = torch.cat(gen_x_lst, 1)

    rec_images_top = rec_images_top.view(rec_images_top.size(0), 1, 28, 28)
    save_image(denorm(rec_images_top.data), './data/%s_rec_images_top.png' %(slurm_name))
