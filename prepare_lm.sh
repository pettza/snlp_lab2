#!/bin/bash
. ./path.sh || exit 1

rm -rf data/lang/*
rm -rf data/local/lm_tmp/*
rm -rf data/local/nist_lm/*

python3 prepare_data.py

LOCAL_TMP_FOLDER=./data/local/lm_tmp
LOCAL_NIST_FOLDER=./data/local/nist_lm
DICT_FOLDER=./data/local/dict
LANG_FOLDER=./data/lang
UNI=ug
BI=bg
NGRAM=1
for lm_suffix in ${UNI} ${BI}; do 
    mkdir ${LANG_FOLDER}/${lm_suffix}
    ILM=${LOCAL_TMP_FOLDER}/${lm_suffix}.ilm.gz
    build-lm.sh -i ${DICT_FOLDER}/lm_train.txt -n ${NGRAM} -o ${ILM}


    compile-lm ${ILM} -t=yes /dev/stdout | grep -v unk | gzip -c > ${LOCAL_NIST_FOLDER}/${lm_suffix}.arpa.gz
    ./utils/prepare_lang.sh ${DICT_FOLDER} "<oov>" ${LOCAL_TMP_FOLDER}  ${LANG_FOLDER}/${lm_suffix}

    gunzip -c ${LOCAL_NIST_FOLDER}/${lm_suffix}.arpa.gz | \
        arpa2fst --disambig-symbol=#0 \
                --read-symbol-table=${LANG_FOLDER}/${lm_suffix}/words.txt - ${LANG_FOLDER}/${lm_suffix}/G.fst
    fstisstochastic ${LANG_FOLDER}/${lm_suffix}/G.fst
    ((NGRAM++))
done