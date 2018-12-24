import os
import sys
import re
from collections import defaultdict 

#create dictionary (lexicon)
phoneticDictionary = defaultdict(str)

#set of all non-silent phones
nonSilentPhones = set()

with open('lexicon.txt', 'r') as lexicon:
    for line in lexicon:
        word, *phones = re.split('\s+', line.lower().strip())
        #some words have alternate pronunciations and are written as <word>(1), ignore them
        if(re.match('\([0-9]+\)', word)):
            continue
        #update set
        nonSilentPhones |= set(phones)
        #update dictionary
        phoneticDictionary[word] = ' '.join(phones)

#sil as well as <oov> are in included in file lexicon.txt
nonSilentPhones.remove('sil')

dictFolder = 'data/local/dict'

#create nonsilence_phones.txt and lexicon.txt
dictFolderPath = os.path.join(dictFolder, 'nonsilence_phones.txt')
lexiconPath = os.path.join(dictFolder, 'lexicon.txt')
with open(dictFolderPath, 'w') as nonSilence, open(lexiconPath, 'w') as lexicon:
    lexicon.write('sil sil\n')
    for phone in sorted(nonSilentPhones):
        nonSilence.write(phone + '\n')
        lexicon.write(phone + ' ' + phone + '\n')

#create silence_phones.txt
dictFolderPath = os.path.join(dictFolder, 'silence_phones.txt')
with open(dictFolderPath, 'w') as silence:
    silence.write('sil\n')

#create optional_silence.txt
dictFolderPath = os.path.join(dictFolder, 'optional_silence.txt')
with open(dictFolderPath, 'w') as optSilence:
    optSilence.write('sil\n')

#list of utterances
transcriptList = []
with open('transcription.txt', 'r') as transcript:
    for sentence in transcript:
        transcriptList.append(sentence)

#create extra_questions.txt
extraPath = os.path.join(dictFolder, 'extra_questions.txt')
with open(extraPath, 'w') as _:
    pass

#for each if the datasets create the needed files
dataSets = ['train', 'test', 'dev']
#needs to be absolute so it's provided by the shell script
wavPath = sys.argv[1]
for dataSet in dataSets:
    folder = os.path.join('data', dataSet)
    uttidsPath = os.path.join(folder, 'uttids')
    utt2spkPath = os.path.join(folder, 'utt2spk')
    wavScriptPath = os.path.join(folder, 'wav.scp')
    textPath = os.path.join(folder, 'text')
    lmPath = os.path.join(dictFolder, 'lm_' + dataSet + '.txt')
    #open all files
    with open(uttidsPath, 'r') as uttids, open(utt2spkPath, 'w') as utt2spk, open(wavScriptPath, 'w') as wav, open(textPath, 'w') as text, open(lmPath, 'w') as lm:
        #for each utterance
        for line in uttids:
            line = line.strip()
            speaker, uttID = line.split('_')[2:4]

            #write line of utt2spk
            utt2spk.write(line + ' ' + speaker + '\n')

            #write line of wac.scp
            wavSpeakerPath = os.path.join(wavPath, speaker, line + '.wav')
            wav.write(line + ' ' + wavSpeakerPath + '\n')

            #write line of lm_<Dataset>.txt
            #the regex matches with 
            phones = ' '.join((phoneticDictionary[word] for word in re.findall('[a-z\'\-]+', transcriptList[int(uttID) - 1].lower())))
            text.write(line + ' sil ' + phones + ' sil\n')
            lm.write('<s> sil ' + phones + ' sil </s>\n')