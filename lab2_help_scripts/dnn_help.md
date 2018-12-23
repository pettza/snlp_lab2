## Training

- If you do not want to use PyTorch, make the TorchSpeechDataset class inherit the `object` python class and delete the pytorch dependency.

  ```python
  # Example of TorchSpeechDataset class
  trainset = TorchSpeechDataset(recipe_dir='/my/path/to/recipe/usc',
                                ali_dir='tri1_ali',
                                feature_context=3,
                                dset='train')
  ```

- Do not forget to standardize your data!



## Calculating the output posteriors

- Import the library kaldi_io: 

  ```python
  import kaldi_io
  ```

- Predict all the test set posteriors and save them into a numpy array. **Be careful**: We want the posteriors at this step and not a single label (i.e. no Softmax)

  ```python
  posts = model.calculate_posteriors(testset.feats)  # this is an example ofc
  ```

- Open the .ark file to write the posteriors: 

  ```python
  post_file = kaldi_io.open_or_fd('/my/path/kaldi/egs/usc/exp/dnn/posteriors.ark', 'wb')
  ```

- Write the posteriors per utterance:

  ```python
  start_index = 0
  testset.end_indexes[-1] += 1
  for i, name in enumerate(testset.uttids):
      out = posts[start_index:testset.end_indexes[i]]
      start_index = testset.end_indexes[i]
      kaldi_io.write_mat(post_file, out, testset.uttids[i])
  
  ```