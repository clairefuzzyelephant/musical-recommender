import numpy as np
import pandas as pd
from pathlib import Path
from music21 import converter
from music21.midi.realtime import StreamPlayer

print('loading streams...')

df = pd.read_csv('all_pairs_similarity.csv', index_col=False)

names = list(set(df['name1']))
name_map = {name: i for i, name in enumerate(names)}

stream_map = {}
for path in Path('essen').rglob('*.krn'):
    if path.name in name_map:
    	sc = converter.parse(path)
    	part = sc.parts[0]
    	while len(part) > 10:
    		part.pop(-1)
    	stream_map[path.name] = sc

print('loading precomputed data...')

similarity_arr = np.empty((len(names), len(names)))
similarity_arr[:] = np.nan

np.fill_diagonal(similarity_arr, 1)

for _, row in df.iterrows():
	if row['name1'] in name_map and row['name2'] in name_map:
		similarity_arr[name_map[row['name1']], name_map[row['name2']]] = row['score']

input('loaded! Press enter to begin...')
print('')

prefs = np.zeros(len(names))

curr = np.random.randint(len(names))

while curr != -1:
	curr_name = names[curr]
	sp = StreamPlayer(stream_map[curr_name])
	print('now playing %s' % curr_name)
	sp.play()
	ans = input('did you like it (q to quit)? (y)/n: ')

	if ans == 'q':
		break

	prefs /= 2
	prefs += similarity_arr[curr] * (-1 if ans == 'n' else 1)
	prefs[curr] = -np.inf
	top = np.argsort(-prefs)[:3]
	for i, t in enumerate(top):
		print('%d. %s' % (i + 1, names[t]))
	try:
		ans = int(input('choose from your new recommendations: ')) - 1
	except:
		ans = 0
	if ans not in range(3):
		ans = 0
	curr = top[ans]

print('goodbye!')
