import argparse

from audioset_dl import _download, dl_audioset, dl_audioset_strong, dl_seglist

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--save_path")
    parser.add_argument("--dl_balanced_train", default=False, action="store_true")
    parser.add_argument("--dl_unbalanced_train", default=False, action="store_true")
    parser.add_argument("--dl_eval", default=False, action="store_true")
    parser.add_argument("--dl_train_strong", default=False, action="store_true")
    parser.add_argument("--dl_eval_strong", default=False, action="store_true")
    parser.add_argument("--percent_from", default=0, type=int)
    parser.add_argument("--percent_to", default=100, type=int)
    parser.add_argument("--seglist")
    parser.add_argument("--segid")

    args = parser.parse_args()

    if args.dl_balanced_train:
        dl_audioset(args.save_path, split="balanced_train", percent_from=percent_from, percent_to=percent_to)
    if args.dl_unbalanced_train:
        dl_audioset(args.save_path, split="unbalanced_train", percent_from=percent_from, percent_to=percent_to)
    if args.dl_eval:
        dl_audioset(args.save_path, split="eval", percent_from=percent_from, percent_to=percent_to)
    if args.dl_train_strong:
        dl_audioset_strong(args.save_path, split="train", percent_from=percent_from, percent_to=percent_to)
    if args.dl_eval_strong:
        dl_audioset_strong(args.save_path, split="eval", percent_from=percent_from, percent_to=percent_to)
    if args.seglist is not None:
        dl_seglist(args.save_path, args.seglist)
    if args.segid is not None:
        ytid = args.segid[:11]
        start = int(args.segid[12:])
        end = start + 10000
        _download([ytid, start, end, args.save_path])
