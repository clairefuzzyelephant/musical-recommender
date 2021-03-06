# musical-recommender
A program that recommends folk music to users based on similarity features.

# TL;DR How to Run

Note: must be using Python 3. Install dependencies:

    $ pip install -r requirements.txt
    
Run the program:

    $ python interactive.py
    
Follow the terminal prompts and discover folk music!

# Overview
There are numerous ML recommender systems out there for recommending trending pop songs to users based on other users' interests. This makes sense for pop songs, but not so much for classical music and folk music, where the musical structure and composition is often more relevant to whether someone enjoys a piece or not, as opposed to whether millions of people also clicked on the same performance. We aim to create a music recommender to a user based on musical similarities between the pieces the user has already liked.


Since the timeframe of this project is limited, we were unable to expand our scope to cover all sorts of music, so we tried to focus on monophonic melodies, but the baseline techniques used may possibly be applied to polyphonic pieces, with tweaking.


# Feature Extraction and Comparison
We used music21 to perform feature extraction, collecting attributes of a piece of music based on certain aspects of its musical structure. 

Aspects we looked at:

- metadata (composer name, composition date, etc.)
- meter
- key signature
- number of parts & part names
- piece name (Sonata, --- Op. ---, Jig, etc.)
- note length composition (percentage of eighth notes, quarter notes, etc.)
- nonharmonic note composition (percentage of nonharmonic tones in piece)
- tonal certainty
- average phrase length (phrase defined by a stretch of continuous notes terminated by a rest or the end of the piece)
- melodic arch (average pitch height for each note of phrases of specified length)
- interval distribution (semitone steps for each melody)

We coded a similarity function that aggregated the results from these aspect comparisons and produced a similarity score between 0 and 1, 0 meaning no similarity at all and 1 meaning exactly the same.

The results were mixed- although we looked at a decent number of musical aspects, there are probably lots more that we glossed over. Some similarity scores made sense and others did not, i.e. a Bach piece vs. a Beethoven piece had a higher similarity score than two of Debussy's own pieces compared to each other.

However, we went ahead and used this function to precompute the similarity scores between ~600 of the songs in the Essen dataset. Thus, we can recommend pieces in real time based on user input in a terminal:

    $ python interactive.py
    loading streams...
    loading precomputed data...
    loaded! Press enter to begin...
    
    now playing han0294.krn

And then after the piece finishes playing...


    did you like it (q to quit)? (y)/n: USER_INPUT
    1. han0022.krn
    2. han0013.krn
    3. han0262.krn
    choose from your new recommendations: USER_INPUT

After user inputs preference, recommender will recommend a similar song (if y) or a different song (if n). As you listen to and like or dislike more songs, the program will take the weighted average of your preferences (weighted towards recency) to recommend more songs. Yay!

Notes: We realized that performance was not very accurate so we decided to try to train a LSTM model on sequences of notes. Scores were read and processed into 31-note sequences that were then fed into the neural network - it would be given a 30-note sequence with the task of predicting the 31st note. However, after hours of training it did not converge well. We decided to scratch this idea and continue with our previous implementation of pure feature extraction, but we recognize that with a well-designed deeper LSTM next time, we may have a better chance of producing even better results. 



