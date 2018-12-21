import os
import re
from collections import defaultdict 

#create dictionary
phoneticDictionary = defaultdict(str)
with open('lexicon.txt', 'r') as lexicon:
    for line in lexicon:
        word, *phones = re.split('\s+', line.lower().strip())
        if(re.match('\([0-9]+\)', word)):
            continue
        phoneticDictionary[word] = ' '.join(phones)

transcriptList = []
with open('transcription.txt', 'r') as transcript:
    for sentence in transcript:
        transcriptList.append(sentence)

folders = ['data/train', 'data/test', 'data/dev']
wavPath = '../../wav/'
for folder in folders:
    uttidsPath = os.path.join(folder, 'uttids')
    utt2spkPath = os.path.join(folder, 'utt2spk')
    wavScriptPath = os.path.join(folder, 'wav.scp')
    textPath = os.path.join(folder, 'text')
    with open(uttidsPath, 'r') as uttids, open(utt2spkPath, 'w') as utt2spk, open(wavScriptPath, 'w') as wav, open(textPath, 'w') as text:
        for line in uttids:
            line = line.strip()
            speaker, uttID = line.split('_')[2:4]
            utt2spk.write(line + ' ' + speaker + '\n')

            wavSpeakerPath = os.path.join(wavPath, speaker, line)
            wav.write(line + ' ' + wavSpeakerPath + '\n')

            phones = ' '.join((phoneticDictionary[word] for word in re.findall('[a-z\'\-]+', transcriptList[int(uttID) - 1].lower())))
            text.write(line + ' sil ' + phones + ' sil\n')