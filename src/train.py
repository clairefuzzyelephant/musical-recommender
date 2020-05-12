import pickle
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader

from dataset import SnipsDataset
from model import ScoreEncoder

device = "cuda" if torch.cuda.is_available() else "cpu"
device = torch.device(device)
print('on device', device)
CHECKPOINT_PATH = 'model/score-encoder.ckpt'


# DEFINE MODEL HYPERPARAMETERS
NUM_ELEMENTS = 111
HIDDEN_SIZE = 256
NUM_LAYERS = 3
KEY_SIZE = 256

LR = 1e-4
NUM_EPOCHS = 1
loss_fn = nn.CrossEntropyLoss().to(device)
DROPOUT = 0


# LOAD TRAINING EXAMPLES
with open('essen_data/snips.pickle', 'rb') as handle:
    snips = pickle.load(handle)

dataset = SnipsDataset(snips)
train_data = DataLoader(dataset, batch_size=4,
                        shuffle=True, num_workers=0)


model = ScoreEncoder(NUM_ELEMENTS, HIDDEN_SIZE, NUM_LAYERS, KEY_SIZE, DROPOUT)
optimizer = optim.Adam(model.parameters(), lr=LR)

model = model.to(device)

for epoch in range(NUM_EPOCHS):
    total_loss = 0
    model.train()
    for i, data in enumerate(train_data):
        if i % 5000 == 0:
            print('Epoch {} Batch {}'.format(epoch, i))

        # get training inputs from corpus
        inputs, outputs = data[0].to(device), data[1].to(device)

        optimizer.zero_grad()
        preds = model(inputs)
        loss = loss_fn(preds, outputs)
        total_loss += loss.item()
        loss.backward()
        optimizer.step()

    torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'total_loss': total_loss,
            }, CHECKPOINT_PATH)

    print('Epoch %d, train loss=%.4f' % (epoch, total_loss / len(train_data)))

    # TODO SET UP VALIDATION

    # total_loss = 0
    # model.eval()
    # for i in range(len(corpus_valid)):
    #     # get validation inputs from corpus
    #     inputs, outputs = None, None

    #     preds = model(inputs)
    #     loss = loss_fn(preds, outputs)
    #     total_loss += loss.item()

    # print('Epoch %d, valid loss=%.4f' % (epoch, total_loss / len(valid_data)))

