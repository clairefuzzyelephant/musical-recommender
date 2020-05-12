# from music21 import *
import pickle

# 111 classes: C0, ..., C8, rest, unk

# REST_CLASS = 109
# UNK_CLASS = 110

# def stream_to_input_classes(s):
#     classes = []
#     for x in s.parts[0].flat.notesAndRests:
#         # rest
#         if isinstance(x, note.Rest):
#             if len(classes) and classes[-1] != 109:
#                 classes.append(REST_CLASS)
#             continue
        
#         if isinstance(x, chord.Chord):
#             x = max(x)
        
#         # pitch
#         if isinstance(x, note.Note) and 0 <= x.pitch.ps <= 108:
#             classes.append(x.pitch.ps)
#             continue
        
#         classes.append(UNK_CLASS)
        
#     return classes


with open('essen_data/data.pickle', 'rb') as handle:
    d = pickle.load(handle)

input_len = 30
snips = []
for v in list(d.values()):
    for i in range(len(v) - input_len):
        snips.append((tuple(v[i:i + input_len]), v[i + input_len]))

with open('essen_data/snips.pickle', 'wb') as handle:
    pickle.dump(snips, handle, protocol=pickle.HIGHEST_PROTOCOL)