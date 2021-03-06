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
from utils import to_var, make_dir_if_not_exists
from LayerNorm1d import LayerNorm1d
from gradient_penalty import gradient_penalty
import random
from timeit import default_timer as timer
import pickle
from math import sqrt
from reg_loss import gan_loss
from incept import get_inception_score
import pickle

'''
Initially just implement LSGAN on MNIST.  

Then implement a critic.  
'''

slurm_name = os.environ["SLURM_JOB_ID"]
DATASET = 'cifar'
DATA_DIR = os.path.join(os.path.abspath('data'), DATASET)
# OUT_DIR = os.path.join('/scratch/nealbray/loc', DATASET, slurm_name)
OUT_DIR = os.path.join('/data/lisatmp4/nealbray/loc/cifar/gan', slurm_name)
MODELS_DIR = os.path.join(OUT_DIR, 'saved_models')
SAVED_MODELS_DIR = MODELS_DIR
CHECKPOINT_INTERVAL = .1 * 60



def denorm(x):
    out = (x+1)/2
    return out.clamp(0,1)


def torch_to_norm(zs):
    return zs.norm(2).data.cpu().numpy()[0]


def var_to_np255(x):
    return (x.data.cpu().numpy() + 1) * 255.0 / 2


batch_size = 100
IMAGE_LENGTH = 32
NUM_CHANNELS = 3

dataset = datasets.CIFAR10('/data/lisa/data/cifar10', train=True, download=False,
                        transform=transforms.Compose([
                        transforms.CenterCrop(IMAGE_LENGTH),
                        transforms.ToTensor(),
                        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
                    ]))
data_loader = torch.utils.data.DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True)

nz = 256


# d_bot = torch.load(os.path.join(SAVED_MODELS_DIR, '%s_dbot.pt' % LOWER_SLURM_ID))
# inf_bot = torch.load(os.path.join(SAVED_MODELS_DIR, '%s_infbot.pt' % LOWER_SLURM_ID))
# gen_bot = torch.load(os.path.join(SAVED_MODELS_DIR, '%s_genbot.pt' % LOWER_SLURM_ID))

# from D_Top import D_Top
# d_top = D_Top(batch_size, nz*ns, nz, 256)
from D_Bot import D_Bot_Conv32
disc = D_Bot_Conv32(batch_size, nz)
from Gen_Bot import Gen_Bot_Conv32_deepbottleneck
gen = Gen_Bot_Conv32_deepbottleneck(batch_size, nz)

if torch.cuda.is_available():
    disc = disc.cuda()
    gen = gen.cuda()
else:
    raise Exception('Cuda not available')

disc_optimizer = torch.optim.Adam(disc.parameters(), lr=0.0001, betas=(0.5,0.99))
gen_optimizer = torch.optim.Adam(gen.parameters(), lr=0.0001, betas=(0.5,0.99))

checkpoint_i = 1
inception_i = 1
start_time = timer()
for epoch in range(200):    
    print 'epoch:', epoch
    for i, (images, _) in enumerate(data_loader):
        images = to_var(images)
        # print 'min:', images.min()
        # print 'max:', images.max()
        # print 'min:', var_to_np255(images).min()
        # print 'max:', var_to_np255(images).max()
        # raise Exception()
        
        # Real images
        d_out_real = disc(images)
        d_loss_real = gan_loss(pre_sig=d_out_real, real=True, D=True, use_penalty=True, grad_inp=images, gamma=1.0)
        
        # Update for real images
        disc.zero_grad()
        d_loss_real.backward()
        disc_optimizer.step()
        
        # Generated images
        z = to_var(torch.randn(batch_size, nz))
        fake_images = gen(z)
        d_out_fake = disc(fake_images)
        d_loss_fake = gan_loss(pre_sig=d_out_fake, real=False, D=True, use_penalty=True, grad_inp=fake_images, gamma=1.0)
        g_loss_fake = gan_loss(pre_sig=d_out_fake, real=False, D=False, use_penalty=False, grad_inp=None, gamma=None, bgan=True)

        # Update for fake images
        disc.zero_grad()
        d_loss_fake.backward(retain_graph=True)
        disc_optimizer.step()
        
        disc.zero_grad()
        gen.zero_grad()
        g_loss_fake.backward()
        gen_optimizer.step()


        #print d_out_bot
        elapsed = timer() - start_time
        if elapsed > CHECKPOINT_INTERVAL:
            print 'Writing images and checkpoints'
            make_dir_if_not_exists(OUT_DIR)
            make_dir_if_not_exists(MODELS_DIR)
        
            save_image(denorm(fake_images.data), os.path.join(OUT_DIR, 'fake_images%04d.png' % checkpoint_i))
            save_image(denorm(images.data), os.path.join(OUT_DIR, 'real_images%04d.png' % checkpoint_i))
        
            # Checkpoint
            print 'Saving generator...'
            torch.save(gen, os.path.join(MODELS_DIR, '%s_gen.pt' % slurm_name))
            print 'Saving discriminator...'
            torch.save(disc, os.path.join(MODELS_DIR, '%s_disc.pt' % slurm_name))
                
                
            # Get inception scores
            im_lst = []
            mi = 255
            ma = 0
            print 'Getting inception score...'
            for _ in xrange(500):
                z = to_var(torch.randn(100, nz))
                fake_images = gen(z)
                fake_np = var_to_np255(fake_images)
                mi = min(mi, fake_np.min())
                ma = max(ma, fake_np.max())
                for i in xrange(100):
                    im_lst.append(fake_np[i, :, :, :])
            print 'fake min:', mi
            print 'fake max:', ma
                
            inception_score = get_inception_score(im_lst)
            print 'inception_score:', inception_score
            inception_scores.append(inception_score)
            
            print 'Saving inception score...'
            with open('inceptions_scores.pkl', 'rb') as f:
                pickle.dump(inception_score, f)
            print 'Done saving!'
            
            start_time = timer()
            checkpoint_i += 1
            
            
                

end_time = timer()
elapsed = end_time - start_time
print 'total time used (in seconds):', elapsed
print 'total time used (in minutes):', elapsed / 60.0
print 'total time used (in hours):', elapsed / 60.0 / 60.0
