import numpy as np
import numpy.random as npr
from numpy.linalg import inv, cholesky
from scipy.stats import chi2
from torch.utils.data import Dataset
import torch
import matplotlib.pyplot as plt 
import seaborn as sns




class SynthDataset(Dataset):
    def __init__(self, train=True, transform=None):

        self.train = train
        self.transform = transform

        self.ts,self.data=np.load('data/syn_periodproc.npy')
        self.num_exp,self.N,self.D=self.data.shape
        
        self.data=self.data.reshape((self.num_exp,-1)) # (num_exp, ND)


        # Generate sample statistics
        # self.phi = np.array([[1,0.5,0],[0.5,1,0],[0,0,1]])
        # self.nu = 5
        # self.covs = np.array([ inv_wishart_rand(self.nu,self.phi) for i in range(self.num_cov)])


    def __len__(self):
        return self.num_exp

    def __getitem__(self, idx):
        sample = self.data[idx]
        # Generate samples on the fly
        # cov = self.covs[cov_idx]
        # y_i = np.array( [ npr.multivariate_normal(np.zeros((3,)), cov) for j in range(self.num_exp) ] )
        # sample = y_i[idx%self.num_exp,]

        if self.transform:
            sample = self.transform(sample)
        return torch.FloatTensor(sample), torch.FloatTensor(sample)


def gen_periodproc():
    """ generate periodic process """
    # setting up
    M=100; N=200; D=2
    t=np.linspace(0,2,num=N+1); t=t[1:]
    # means
    mu=np.zeros((D,N))
    # covariances
    L=np.zeros((D,D,N)); S=np.zeros((D,D))
    for i in range(D):
        for j in range(0,i+1):
            L[i,j,:]=pow(-1,i+1)*np.sin((i+1)*t*np.pi/D)*pow(-1,j+1)*np.cos((j+1)*t*np.pi/D)
            S[i,j]=np.abs(i-j)+1
    S=S+np.tril(S,-1).transpose()
    Sigma=np.sum(L.reshape((D,1,D,N))*L.reshape((1,D,D,N)),axis=2)/S[:,:,None] # (D,D,N)
    # generate data
    y=np.zeros((M,N,D))
    for m in range(M):
        for n in range(N):
            y[m,n,:]=np.random.multivariate_normal(mu[:,n],Sigma[:,:,n])
    np.save('data/syn_periodproc.npy', (t,y))
#     return t,y
    
if __name__ == '__main__':
    gen_periodproc()
    t,y  = np.load('data/syn_periodproc.npy')

    plt.plot(t, y[1,:,:],'*')
    plt.show()
#     sns.tsplot(y[1,:,:].transpose())
#     plt.show()