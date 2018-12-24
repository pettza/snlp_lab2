import os
import re
from collections import defaultdict 
#create dictionary
phoneticDictionary = defaultdict(str)
nonSilentPhones = set() 
with open('lexicon.txt', 'r') as lexicon:
    for line in lexicon:
        word, *phones = re.split('\s+', line.lower().strip())
        if(re.match('\([0-9]+\)', word)):
            continue
        nonSilentPhones |= set(phones)
        phoneticDictionary[word] = ' '.join(phones)
nonSilentPhones.remove('sil')

dictFolder = 'data/local/dict'
dictFolderPath = os.path.join(dictFolder, 'nonsilence_phones.txt')
lexiconPath = os.path.join(dictFolder, 'lexicon.txt')
with open(dictFolderPath, 'w') as nonSilence, open(lexiconPath, 'w') as lexicon:
    lexicon.write('sil sil\n')
    for phone in sorted(nonSilentPhones):
        nonSilence.write(phone + '\n')
        lexicon.write(phone + ' ' + phone + '\n')

dictFolderPath = os.path.join(dictFolder, 'silence_phones.txt')
with open(dictFolderPath, 'w') as silence:
    silence.write('sil\n')

dictFolderPath = os.path.join(dictFolder, 'optional_silence.txt')
with open(dictFolderPath, 'w') as optSilence:
    optSilence.write('sil\n')

transcriptList = []
with open('transcription.txt', 'r') as transcript:
    for sentence in transcript:
        transcriptList.append(sentence)

extraPath = os.path.join(dictFolder, 'extra_questions.txt')
with open(extraPath, 'w') as _:
    pass
dataSets = ['train', 'test', 'dev']
wavPath = '/home/stathis/Desktop/kaldi/egs/usc/wav'
for dataSet in dataSets:
    folder = os.path.join('data', dataSet)
    uttidsPath = os.path.join(folder, 'uttids')
    utt2spkPath = os.path.join(folder, 'utt2spk')
    wavScriptPath = os.path.join(folder, 'wav.scp')
    textPath = os.path.join(folder, 'text')
    lmPath = os.path.join(dictFolder, 'lm_' + dataSet + '.txt')
    with open(uttidsPath, 'r') as uttids, open(utt2spkPath, 'w') as utt2spk, open(wavScriptPath, 'w') as wav, open(textPath, 'w') as text, open(lmPath, 'w') as lm:
        for line in uttids:
            line = line.strip()
            speaker, uttID = line.split('_')[2:4]
            utt2spk.write(line + ' ' + speaker + '\n')

            wavSpeakerPath = os.path.join(wavPath, speaker, line + '.wav')
            wav.write(line + ' ' + wavSpeakerPath + '\n')

            phones = ' '.join((phoneticDictionary[word] for word in re.findall('[a-z\'\-]+', transcriptList[int(uttID) - 1].lower())))
            text.write(line + ' sil ' + phones + ' sil\n')
            lm.write('<s> sil ' + phones + ' sil </s>\n')