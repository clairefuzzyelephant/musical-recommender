import torch
from torch.utils.data import Dataset

class SnipsDataset(Dataset):
    
    def __init__(self, snips):
        self.inputs = []
        self.outputs = []
        for i, o in snips:
            self.inputs.append(i)
            self.outputs.append(o)
        self.inputs = torch.Tensor(self.inputs).long()
        self.outputs = torch.Tensor(self.outputs).long()
    
    def __len__(self):
        return len(self.outputs)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        return self.inputs[idx], self.outputs[idx]
