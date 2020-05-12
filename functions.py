from music21 import stream, corpus, note, pitch, converter, meter, key, expressions, scale, chord
import re
import numpy as np

"""
Average pitch height for phrases of variable length in a score
"""
def melodic_arch(score: stream.Stream, phrase_length: int):
    total_phrases = 0 #total number of phrases
    sum_pitch_height = [0 for i in range(phrase_length)]  #sum of heights for each note position, measured in semitones above middle C
    phrase = [] #phrase is empty at beginning of piece
    for n in score.recurse().notesAndRests:
        if isinstance(n, chord.Chord):
            n = max(n)
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
    for n in score.recurse().notesAndRests:
        if isinstance(n, chord.Chord):
            n = max(n)
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
Returns key with tonal certainty, and total percentage of notes within the key
"""
def nonharmonic_notes(score: stream.Stream):
    key_sig = score.analyze('key')
    certainty = key_sig.tonalCertainty()
    notes_within_key = [p.name for p in key_sig.pitches]
    for pitch in key_sig.pitches:
        notes_within_key.extend([p.name for p in pitch.getAllCommonEnharmonics()])
    total_notes = 0 #total number of notes
    num_nonharmonic = 0 #total number of nonharmonic notes
    for n in score.recurse().notes:
        if isinstance(n, chord.Chord):
            n = max(n)
        if n.tie and (n.tie.type == 'stop' or n.tie.type == 'continue'): #do not count a tied note more than once
            continue
        else:
            if n.pitch.name not in notes_within_key:
                num_nonharmonic += 1
            total_notes += 1

    if total_notes == 0:
        return None
    return (certainty, 1-num_nonharmonic/float(total_notes))



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
Returns distribution of note lengths from increments of sixteenths up until a whole note
"""
def get_note_lengths(score: stream.Stream):
    note_lengths = dict()
    note_count = 0.0
    for n in score.recurse().notesAndRests:
        if isinstance(n, chord.Chord):
            n = max(n)
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
Computes distribution of intervals within one octave
"""
def get_intervals(score: stream.Stream):
    ints = np.zeros(25)
    notes = score.flat.notes
    for n1, n2 in zip(notes[:-1], notes[1:]):
        if isinstance(n1, chord.Chord):
            n1 = max(n1)
        if isinstance(n2, chord.Chord):
            n2 = max(n2)
        curr_int = int(n2.pitch.ps - n1.pitch.ps)

        # if curr_int is a good interval, count its occurrence
        if abs(curr_int) <= 12:
            ints[abs(curr_int) + 12] += 1

    return ints / ints.sum()


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
    meter = get_meter(score) #gets the first meter of the score
    key = get_key(score) #gets the first key of the score
    num_parts = len(score.parts) #number of instrument parts
    all_parts = []
    for part in range(num_parts):
        all_parts.append(score.parts[part].partName) #list of each part name
    return [meter, key, num_parts, all_parts]


"""
Computes similarity between two pieces based on musical attributes, ideally
"""
def similarity(s1: stream.Stream, s2: stream.Stream):
    features = [] #each entry has a score from 0 to 1 based on similarity
    #comparing metadata
    ma1 = metadata_attributes(s1)
    ma2 = metadata_attributes(s2)
    comp1, comp2 = None, None
    for tup in ma1:
        if tup[0] == 'composer':
            comp1 = tup[1]
    for tup in ma2:
        if tup[0] == 'composer':
            comp2 = tup[1]
    same_composer = False
    if comp1 != None and comp2 != None:
        if (comp1 == comp2 or comp1 in comp2 or comp2 in comp1):
            same_composer = True
        else:
            composer1 = comp1.split()
            composer2 = comp2.split()
            for word in composer1:
                if len(word) > 4 and word in composer2:
                    same_composer = True
                    break
                for word2 in composer2:
                    if word in word2 or word2 in word:
                        same_composer = True
                        break
    if same_composer:
        print("Composer: same composer")
        features.append(1)
        features.append(1) #more weight on composer
        features.append(1)
    else:
        print("Composer: different composer")
        features.append(0)
        features.append(0)
        features.append(0)

    #comparing basic musical data
    ms1 = musical_attributes(s1)
    ms2 = musical_attributes(s2)
    if ms1[0] == ms2[0]:
        print("Meter: same meter")
        features.append(1)
    else:
        print("Meter: different meter")
        features.append(0)
    if ms1[1] == ms2[1]:
        print("Key: same key")
        features.append(1)
    else:
        print("Key: different key")
        features.append(0)
    if set(ms1[3]) == set(ms2[3]):
        print("Instrumentation: same")
        features.append(1)
    else:
        print("Instrumentation: different")
        features.append(0)

    #comparing note lengths
    n1 = get_note_lengths(s1)
    n2 = get_note_lengths(s2)
    note_length_similarites = [min(n1[i], n2[i])/max(n1[i], n2[i]) if max(n1[i], n2[i]) != 0  else 1 for i in range(16)]
    avg_note_length_similarity = sum(note_length_similarites)/16.0
    print("Average note length similarity: %.4f" % avg_note_length_similarity)
    features.append(avg_note_length_similarity)

    #comparing phrase lengths
    pl1 = avg_phrase_length(s1)
    pl2 = avg_phrase_length(s2)
    phrase_length_similarity = min(pl1, pl2)/max(pl1, pl2)
    print("Average phrase length similarity: %.4f" % phrase_length_similarity)
    features.append(phrase_length_similarity)

    #comparing common piece types/names
    p1 = piece_name(s1)
    p2 = piece_name(s2)
    matches = 0
    total = 0
    for i in range(6):
        if p1[i] == 1 and p2[i] == 1:
            total += 1
            matches += 1
        elif not (p1[i] == 0 and p2[i] == 0):
            total += 1
    if total == 0:
        print("Common piece type similarity: 0")
        features.append(0)
    else:
        print("Common piece type similarity: %.4f" % (matches/float(total)))
        features.append(matches/float(total))

    #comparing key confidence and nonharmonic tones
    nn1 = nonharmonic_notes(s1)
    nn2 = nonharmonic_notes(s2)
    key_confidence = min(nn1[0], nn2[0])/max(nn1[0], nn2[0])
    print("Key analysis confidence similarity: %.4f" % key_confidence)
    features.append(key_confidence)
    features.append(key_confidence) #more weight placed on key confidence

    prop_atonal = min(nn1[1], nn2[1])/max(nn1[1], nn2[1])
    print("Proportion of nonharmonic notes similarity: %.4f" % prop_atonal)
    features.append(prop_atonal)
    features.append(prop_atonal) #more weight placed on tonality

    intervals1, intervals2 = get_intervals(s1), get_intervals(s2)
    interval_dot = np.dot(intervals1, intervals2)
    print("Interval distribution similarity metric: %.4f" % interval_dot)
    features.append(interval_dot)

    #comparing melodic arch
    limit_phrase_length = int((pl1+pl2)/2.0 + 5)
    all_diffs = []
    for i in range(5, int((pl1+pl2)/2.0 + 5)):
        arch1 = melodic_arch(s1, i)
        arch2 = melodic_arch(s2, i)
        if arch1 == None or arch2 == None:
            print("Arch difference for length %d phrases: n/a" % i)
            limit_phrase_length -= 1
            continue
        sim = 0
        for n in range(i):
            if max(arch1[n], arch2[n]) == 0:
                continue
            else:
                diff = abs(arch1[n] - arch2[n])
                sim += diff
        sim = sim/i #average difference 
        print("Arch similarity for length %d phrases: %.4f" % (i, 1.0/sim))
        if sim < 1:
            all_diffs.append(1.0)
        else:
            all_diffs.append(1.0/sim)
    
    for i in all_diffs:
        features.append(i)
    

    return sum(features)/float(len(features))



piece0 = converter.parse('essen/asia/china/han/han0001.krn')
piece2 = converter.parse('essen/africa/arabic01.krn')
# piece1 = corpus.parse('bach/bwv11.6')
# piece2 = corpus.parse('bach/bwv127.5')
# piece3 = corpus.parse('beethoven/opus18no3')
# piece4 = corpus.parse('mozart/k155/movement1')
piece1 = converter.parse('piano/bach_prelude.mxl')
#piece2 = converter.parse('piano/chopin_balladeno4.mxl')
piece3 = converter.parse('piano/debussy_clairdelune.mxl')
piece4 = converter.parse('piano/ravel_unebarque.mxl')
piece5 = converter.parse('piano/bartok_romania.mxl')
piece6 = converter.parse('piano/debussy_reverie.mxl')
piece7 = corpus.parse('beethoven/opus74.mxl')

# pieces = [piece1, piece3, piece4]

# for p in pieces:
#     print(musical_attributes(p))
#     print(metadata_attributes(p))
#     print(get_note_lengths(p))
#     print(avg_phrase_length(p))
#     print(piece_name(p))
#     print(nonharmonic_notes(p))
#     print()
print(similarity(piece3, piece6) , "debussy vs. debussy")
print(similarity(piece3, piece4) , "debussy vs. ravel")
print(similarity(piece1, piece5) , "bach vs. bartok")
print(similarity(piece1, piece7) , "bach vs. beethoven")
