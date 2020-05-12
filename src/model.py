import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

class SelfAttn(nn.Module):
    
    def __init__(self, key_size, value_size):
        super(SelfAttn, self).__init__()
        self.sqrt_key_size = key_size ** 0.5
        self.wq = nn.Linear(value_size, key_size, bias=False)
        self.wk = nn.Linear(value_size, key_size, bias=False)
        self.wv = nn.Linear(value_size, value_size, bias=False)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x_batched):
        return torch.stack([self.attend(x) for x in x_batched])

    def attend(self, x):
        queries = self.wq(x)
        keys = self.wk(x)
        values = self.wv(x)
        weights = self.softmax(torch.mm(queries, keys.T) / self.sqrt_key_size)
        return torch.mm(weights, values)


class ScoreEncoder(nn.Module):

    def __init__(self, num_elements, hidden_size, num_layers, key_size, dropout=0):
        super(ScoreEncoder, self).__init__()
        self.embedding = nn.Embedding(num_elements, hidden_size)
        self.bi_lstm = nn.LSTM(hidden_size, hidden_size, num_layers, batch_first=True, dropout=dropout, bidirectional=True)
        self.self_attn = SelfAttn(key_size, 2 * hidden_size)
        self.lstm = nn.LSTM(2 * hidden_size, 2 * hidden_size, num_layers, batch_first=True, dropout=dropout)
        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(2 * hidden_size, num_elements)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        embeddings = self.embedding(x)
        output, _ = self.bi_lstm(embeddings)
        output = self.self_attn(output)
        output, _ = self.lstm(output)
        output = output[:, -1, :].squeeze()
        output = self.dropout(output)
        output = self.linear(output)
        return self.softmax(output)

