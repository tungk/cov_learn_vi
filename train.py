import math
import numpy as np
import torch
import torch.nn as nn
from torch import optim
import torch.utils
import torch.utils.data
from torchvision import datasets, transforms
from torch.autograd import Variable
import matplotlib.pyplot as plt 
import seaborn as sns
from vae import VAE
from syn_wishart import SynthDataset

"""implementation of the Variational Recurrent
Neural Network (VRNN) from https://arxiv.org/abs/1506.02216
using unimodal isotropic gaussian distributions for 
inference, prior, and generating models."""

def train(epoch):
	train_loss = 0

	for batch_idx, (data, _) in enumerate(train_loader):

		#transforming data
		data = Variable(data)
		#data = Variable(data.squeeze().transpose(0, 1))
		#data = (data - data.min().data[0]) / (data.max().data[0] - data.min().data[0])

		#forward + backward + optimize
		optimizer = optim.Adam(model.parameters(), lr=1e-3)
		optimizer.zero_grad()
		kld_loss, nll_loss,(enc_mean, enc_cov), (dec_mean, dec_cov) = model(data)
		
		# loss
		loss = kld_loss + nll_loss
		loss.backward()
		optimizer.step()

		#grad norm clipping, only in pytorch version >= 1.10
		nn.utils.clip_grad_norm(model.parameters(), clip)

		#printing
		if batch_idx % print_every == 0:
			print('Train Epoch: {} [{}/{} ({:.0f}%)]\t KLD Loss: {:.4f} \t NLL Loss: {:.4f} \t ELBO Loss: {:.4f}'.format(
				epoch, batch_idx * len(data), len(train_loader.dataset),
				100. * batch_idx / len(train_loader),
				kld_loss.data[0] / batch_size,
				nll_loss.data[0] / batch_size,
				loss.data[0] /batch_size))

			sample = model.sample_z()
			# sns.kdeplot(sample[:,0], sample[:,1], color="b", shade=True)

			# plt.show()
			# plt.pause(1e-6)
			# plt.gcf().clear()
			 # plt.imshow(sample.numpy())

		train_loss += loss.data[0]


	print('====> Epoch: {} Average loss: {:.4f}'.format(
		epoch, train_loss / len(train_loader.dataset)))

	# Eval p(x)
	avg_mean, avg_cov = model.sample_x()
	print(avg_mean, avg_cov)


def test(epoch):
	"""uses test data to evaluate 
	likelihood of the model"""
	
	mean_kld_loss, mean_nll_loss = 0, 0
	for i, (data, _) in enumerate(test_loader):                                            
		
		#data = Variable(data)
		data = Variable(data.squeeze().transpose(0, 1))
		data = (data - data.min().data[0]) / (data.max().data[0] - data.min().data[0])

		kld_loss, nll_loss, _, _ = model(data)
		mean_kld_loss += kld_loss.data[0]
		mean_nll_loss += nll_loss.data[0]

	mean_kld_loss /= len(test_loader.dataset)
	mean_nll_loss /= len(test_loader.dataset)

	print('====> Test set loss: KLD Loss: {:.4f}, NLL Loss: {:.4f}'.format(
		mean_kld_loss, mean_nll_loss))


#hyperparameters
x_dim = 16 #2
h_dim = 400
z_dim = 16
n_layers =  1
n_epochs = 100
clip = 10
learning_rate = 1e-4
batch_size = 16
seed = 128
print_every = 100
save_every = 10


#manual seed
torch.manual_seed(seed)
plt.ion()

#init model + optimizer + datasets
# SynthDataset(train=True)
# datasets.MNIST('data', train=True, download=True,
# 	transform=transforms.ToTensor())
train_loader = torch.utils.data.DataLoader(
	datasets.MNIST('data', train=True, download=True,
	transform=transforms.ToTensor()),
    batch_size=batch_size, shuffle=True)

test_loader = torch.utils.data.DataLoader(
    datasets.MNIST('data', train=True, download=True,
	transform=transforms.ToTensor()),
    batch_size=batch_size, shuffle=True)



model = VAE(x_dim, h_dim, z_dim)
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

for epoch in range(1, n_epochs + 1):
	
	#training + testing
	train(epoch)
	test(epoch)

	#saving model
	if epoch % save_every == 1:
		fn = 'saves/vae_state_dict_'+str(epoch)+'.pth'
		torch.save(model.state_dict(), fn)
		print('Saved model to '+fn)








