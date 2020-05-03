from music21 import stream, corpus, note, pitch, converter, meter, key, expressions
import re

"""
Average pitch height for phrases of variable length in a score
"""
def melodic_arch(score: stream.Stream, phrase_length: int):
    total_phrases = 0 #total number of phrases
    sum_pitch_height = [0 for i in range(phrase_length)]  #sum of heights for each note position, measured in semitones above middle C
    phrase = [] #phrase is empty at beginning of piece
    for n in score.recurse().getElementsByClass(['Note', 'Rest']):
        if n.tie and (n.tie.type == 'stop' or n.tie.type == 'continue'): #do not count a tied note more than once 
            continue
        if n.isRest or (len(n.expressions) != 0 and 'fermata' == n.expressions[0].name):
            if len(phrase) == phrase_length:
                total_phrases += 1
                for i in range(phrase_length):
                    sum_pitch_height[i] += phrase[i].pitch.ps - 60 #60 is middle C
            phrase = []
        else:
            phrase.append(n)
    #if reached end of score, check the last phrase is of desired length
    if len(phrase) == phrase_length:
        total_phrases += 1
        for i in range(phrase_length):
                    sum_pitch_height[i] += phrase[i].pitch.ps - 60

    if total_phrases == 0:
        return None                
    return [height/total_phrases for height in sum_pitch_height]


"""
Returns average phrase length
"""
def avg_phrase_length(score: stream.Stream):
    total_phrases = 0 #total number of phrases
    length = 0 #phrase is empty at beginning of piece
    phrase_lengths = [] #all the phrase lengths 
    for n in score.recurse().getElementsByClass(['Note', 'Rest']):
        if n.tie and (n.tie.type == 'stop' or n.tie.type == 'continue'): #do not count a tied note more than once 
            continue
        if n.isRest or (len(n.expressions) != 0 and 'fermata' == n.expressions[0].name):
            phrase_lengths.append(length)
            total_phrases += 1
            length = 0
        else:
            length += 1
    #reached end
    if length != 0:
        phrase_lengths.append(length)
        total_phrases += 1

    if total_phrases == 0:
        return None                
    return sum(phrase_lengths)/total_phrases



"""
Returns the starting meter of the piece
"""
def get_meter(score: stream.Stream):
    first_meter = score.recurse().getElementsByClass(meter.TimeSignature)
    if not first_meter:
        return (0, 0)
    else:
        return (first_meter[0].numerator, first_meter[0].denominator)

"""
Returns the starting key signature of the piece as a number of sharps (if negative, number of flats)
"""
def get_key(score: stream.Stream):
    first_key = score.recurse().getElementsByClass(key.KeySignature)
    if not first_key:
        return 0
    else:
        return first_key[0].sharps

"""
Returns proportion of each note length from increments of sixteenths up until a whole note
"""
def get_note_lengths(score: stream.Stream):
    note_lengths = dict()
    note_count = 0.0
    for n in score.recurse().getElementsByClass(['Note', 'Rest']):
        if n.quarterLength not in note_lengths:
            note_lengths[n.quarterLength] = 1
        else:
            note_lengths[n.quarterLength] += 1
        note_count += 1.0
    i = 0
    vector = []
    while i < 4:
        i += 0.25
        if i in note_lengths: 
            vector.append(note_lengths[i]/note_count)
        else:
            vector.append(0)

    return vector
    
    

"""
Returns type of piece as a vector with a 1 in the index that matches type of piece
[chorale, jig, ballad, bach, sonata, symphony, opus]
"""
def piece_name(score: stream.Stream):
    filename = score.filePath.name
    is_chorale = int('chorale' in filename or 'Chorale' in filename)
    is_jig = int('jig' in filename or 'Jig' in filename)
    is_bach = int('bach' in filename or 'Bach' in filename or 'bwv' in filename)
    is_sonata = int('sonata' in filename or 'Sonata' in filename)
    is_symphony = int('symphony' in filename or 'Symphony' in filename)
    is_part_of_opus = int('opus' in filename or 'Op.' in filename or 'Opus' in filename or 'op.' in filename)
    return (is_chorale, is_jig, is_bach, is_sonata, is_symphony, is_part_of_opus)

"""
Basic metadata features
"""
def metadata_attributes(score: stream.Stream):
    return score.metadata.all()


"""
Basic musical features
Returns [meter, key, num_parts, all_instruments]
"""
def musical_attributes(score: stream.Stream):
    meter = get_meter(score)
    key = get_key(score)
    num_parts = len(score.parts)
    all_parts = []
    for part in range(num_parts):
        all_parts.append(score.parts[part].partName)
    return [meter, key, num_parts, all_parts]



piece0 = converter.parse('essen/asia/china/han/han0001.krn')
piece1 = corpus.parse('bach/bwv11.6')
piece2 = corpus.parse('bach/bwv127.5')
piece3 = corpus.parse('beethoven/opus18no3')
piece4 = corpus.parse('mozart/k155/movement1')

pieces = [piece0, piece1, piece2, piece3, piece4]

for p in pieces:
    print(musical_attributes(p))
    print(get_note_lengths(p))
    print(avg_phrase_length(p))
    print(piece_name(p))
    print()




