from music21 import stream, corpus, note, pitch

"""
Average pitch height for phrases of variable length in a score
"""
def melodic_arch(score: stream.Score, phrase_length: int):
    total_phrases = 0 #total number of phrases
    sum_pitch_height = [0 for i in range(phrase_length)]  #sum of heights for each note position, measured in semitones above middle C

    phrase = [] #phrase is empty at beginning of piece
    for n in score.recurse().getElementsByClass(['Note', 'Rest']):
        if n.tie and (n.tie.type == 'stop' or n.tie.type == 'continue'): #do not count a tied note more than once 
            continue
        if n.isRest:
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





