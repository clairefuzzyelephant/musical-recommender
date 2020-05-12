import random
import torch
from torch.utils.data import Dataset

class SnipsDataset(Dataset):
    
    def __init__(self, snips, transform=None):
        self.inputs = []
        self.outputs = []
        for i, o in snips:
            self.inputs.append(i)
            self.outputs.append(o)
        self.inputs = torch.Tensor(self.inputs).long()
        self.outputs = torch.Tensor(self.outputs).long()
        self.transform = transform
    
    def __len__(self):
        return len(self.outputs)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        ret = (self.inputs[idx], self.outputs[idx])
        if self.transform:
            ret = self.transform(ret)
        return ret

class RandomShift(object):

    def __init__(self, max_shift):
        self.max_shift = max_shift

    def __call__(self, data):
        shift = random.randint(-self.max_shift, self.max_shift + 1)
        return data[0] + shift, data[1] + shift