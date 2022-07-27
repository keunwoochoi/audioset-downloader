# audioset-downloader
[Google AudioSet](https://research.google.com/audioset/) download python package

## Usage
```bash
# download balanced_train_segments.csv
python bin/run.py --save_path ${SAVE_PATH} --dl_balanced_train
# download balanced_train_segments.csv, but first 30%
python bin/run.py --save_path ${SAVE_PATH} --dl_balanced_train --percent_from 0 --percent_to 50
# download unbalanced_train_segments.csv
python bin/run.py --save_path ${SAVE_PATH} --dl_unbalanced_train
# download eval_segments.csv
python bin/run.py --save_path ${SAVE_PATH} --eval
# download audioset_train_strong.tsv
python bin/run.py --save_path ${SAVE_PATH} --dl_train_strong
# download audioset_eval_strong.tsv
python bin/run.py --save_path ${SAVE_PATH} --dl_eval_strong
# download segment_id
python bin/run.py --save_path ${SAVE_PATH} --segid ${SEGID}
```

## Tests
```bash
pytest -s tests
```
