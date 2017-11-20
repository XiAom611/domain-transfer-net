from base_test import BaseTest
from data import SVHNDataset
import digits_model

import numpy as np
import matplotlib.pyplot as plt

import torch
import torchvision
import torch.optim as optim
from torch.autograd import Variable
import torch.nn as nn
from torchvision import datasets, transforms

def imshow(img):
        npimg = img.numpy()
        plt.imshow(np.transpose(npimg, (1, 2, 0)))        
    
class classifierFTest(BaseTest):
    
    def __init__(self, use_gpu=True):
        super(self.__class__, self).__init__(use_gpu)
        self.log['train_accuracy'] = []        
        self.log['val_accuracy'] = []

    
    def create_data_loaders(self, isSVHN):
        #SVHN
        if isSVHN:
            train_set = SVHNDataset(split='extra')
            self.train_loader = torch.utils.data.DataLoader(train_set, batch_size=256,
                                              shuffle=True, num_workers=8)
            test_set = SVHNDataset(split='test')
            self.test_loader = torch.utils.data.DataLoader(test_set, batch_size=128,
                                             shuffle=False, num_workers=8)
        #MNIST
        else:
            self.train_loader = torch.utils.data.DataLoader(
                    datasets.MNIST('./datasets', train=True, download=True,
                    transform=transforms.Compose([
                    transforms.ToTensor(),
                    transforms.Normalize((0.1307,), (0.3081,))
                    ])),
                    batch_size=256, shuffle=True, num_workers=8)

            self.test_loader = torch.utils.data.DataLoader(
                    datasets.MNIST('./datasets', train=False, 
                    transform=transforms.Compose([
                    transforms.ToTensor(),
                    transforms.Normalize((0.1307,), (0.3081,))
                    ])),
                    batch_size=128, shuffle=False, num_workers=8)

    def visualize_single_batch(self):
        # get some random training images
        dataiter = iter(self.train_loader)
        images, labels = dataiter.next()
        print(images.shape)
        
        # show images
        imshow(torchvision.utils.make_grid(images))
        
    def create_model(self):
        self.model = digits_model.F(3, self.use_gpu)
    
    def create_loss_function(self):
        self.loss_function = nn.CrossEntropyLoss()
        if self.use_gpu:
            self.loss_function.type(torch.cuda.FloatTensor)

    def create_optimizer(self):
        #self.optimizer = optim.SGD(self.model.parameters(), lr=0.001, momentum=0.9)
        self.optimizer = optim.RMSprop(self.model.parameters(), lr = 0.001)
    
    def train_model(self, num_epochs, **kwargs):
        for epoch in range(num_epochs):  # loop over the dataset multiple times

            running_loss = 0.0
            correct = 0
            total = 0
            for i, data in enumerate(self.train_loader, 0):
                # get the inputs
                inputs, labels = data
                #inputs = torch.cat((inputs, inputs, inputs), 1)



                # wrap them in Variable
                if not self.use_gpu:
                    inputs, labels = Variable(inputs.float()), Variable(labels.long())
                else:
                    inputs, labels = Variable(inputs.float().cuda()), Variable(labels.long().cuda())

                # zero the parameter gradients
                self.optimizer.zero_grad()

                # forward + backward + optimize
                outputs = self.model(inputs)
                loss = self.loss_function(outputs, labels)
                loss.backward()
                self.optimizer.step()

                running_loss += loss.data[0]
                total += labels.size(0)
                _, predicted = torch.max(outputs.data, 1)
                correct += (predicted == labels.data).sum()

            correct = 1. * correct / total
            print('[%dth epoch]' % (epoch + 1))
            print('training loss: %.4f   accuracy: %.3f%%' % (running_loss, 100 * correct))
            self.log['train_loss'].append(running_loss)
            self.log['train_accuracy'].append(correct)
            self.log['best_model'] = self.model
            self.test_model()

        print('Finished Training')
   
    def test_model(self):
        running_loss = 0.0
        correct = 0
        total = 0
        for i, data in enumerate(self.test_loader, 0):
            inputs, labels = data
            #inputs = torch.cat((inputs, inputs, inputs), 1)    

            
            if not self.use_gpu:
                inputs, labels = Variable(inputs.float()), Variable(labels.long())
            else:
                inputs, labels = Variable(inputs.float().cuda()), Variable(labels.long().cuda())
            
            outputs = self.model(inputs)
            
            loss = self.loss_function(outputs, labels)
            running_loss += loss.data[0]
            total += labels.size(0)
            _, predicted = torch.max(outputs.data, 1)
            correct += (predicted == labels.data).sum()
        
        correct = 1. * correct / total

        print('test loss: %.4f   accuracy: %.3f%%' % (running_loss, 100 * correct))
        self.log['val_loss'].append(running_loss)
        self.log['val_accuracy'].append(correct)


    