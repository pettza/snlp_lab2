import os
import numpy as np
import kaldi_io
from torch.utils.data import Dataset


class TorchSpeechDataset(Dataset):
    def __init__(self, recipe_dir, ali_dir, feature_context=2, dset):
        self.recipe_dir = recipe_dir
        self.ali_dir = ali_dir
        self.feature_context = feature_context
        self.dset = 'dev' if dset == 'valid' else dset

        self.feats, self.labels = self.read_data()
        self.feats, self.labels, self.uttids, self.end_indexes = self.unify_data(self.feats, self.labels)

    def read_data(self):
        feat_path = os.path.join(self.recipe_dir, 'data', self.dset, 'feats.scp')
        if self.dset == 'train':
            label_path = os.path.join(self.recipe_dir, 'exp', self.ali_dir)
        else:
            label_path = os.path.join(self.recipe_dir, 'exp', self.ali_dir + '_' + self.dset)
        feat_opts = "apply-cmvn --utt2spk=ark:{0} ark:{1} ark:- ark:- |". \
            format(os.path.join(self.recipe_dir, 'data', self.dset, 'utt2spk'),
                   os.path.join(self.recipe_dir, 'data', self.dset,
                                self.dset + '_cmvn_speaker.ark'))
        feat_opts += " add-deltas --delta-order=2 ark:- ark:- |"
        if self.feature_context:
            feat_opts += " splice-feats --left-context={0} --right-context={0} ark:- ark:- |". \
                format(str(self.feature_context))
        label_opts = 'ali-to-pdf'

        feats = {k: m for k, m in kaldi_io.read_mat_ark(
            'ark:copy-feats scp:{} ark:- | {}'.format(feat_path, feat_opts))}
        lab = {k: v for k, v in kaldi_io.read_vec_int_ark(
            'gunzip -c {0}/ali*.gz | {1} {0}/final.mdl ark:- ark:-|'.format(label_path, label_opts))
               if k in feats}
        feats = {k: v for k, v in feats.items() if k in lab}

        return feats, lab

    def unify_data(self, feats, lab, optional_array=None):
        fea_conc = np.concatenate([v for k, v in sorted(feats.items())])
        lab_conc = np.concatenate([v for k, v in sorted(lab.items())])
        if optional_array:
            opt_conc = np.concatenate([v for k, v in sorted(optional_array.items())])
        names = [k for k, v in sorted(lab.items())]
        end_snt = 0
        end_indexes = []
        for k, v in sorted(lab.items()):
            end_snt += v.shape[0]
            end_indexes.append(end_snt)

        lab = lab_conc.astype('int64')
        if optional_array:
            opt = opt_conc.astype('int64')
            return fea_conc, lab, opt, names, end_indexes
        return fea_conc, lab, names, end_indexes

    def __getitem__(self, idx):
        return self.feats[idx], self.labels[idx]

    def __len__(self):
        return len(self.labels)
