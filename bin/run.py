import argparse

from audioset_dl import dl_audioset, dl_audioset_strong, dl_seglist, dl_vggsound

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--save_path")
    parser.add_argument("--dl_balanced_train", default=False, action="store_true")
    parser.add_argument("--dl_unbalanced_train", default=False, action="store_true")
    parser.add_argument("--dl_eval", default=False, action="store_true")
    parser.add_argument("--dl_train_strong", default=False, action="store_true")
    parser.add_argument("--dl_eval_strong", default=False, action="store_true")
    parser.add_argument("--dl_vgg_train", default=False, action="store_true")
    parser.add_argument("--dl_vgg_test", default=False, action="store_true")
    parser.add_argument("--percent_from", default=0, type=int)
    parser.add_argument("--percent_to", default=100, type=int)
    parser.add_argument("--num_processes", default=1, type=int)
    parser.add_argument("--target", choices=['audio', 'video'], type=str)
    parser.add_argument("--seglist")
    parser.add_argument("--segid")

    args = parser.parse_args()

    if args.dl_balanced_train:
        dl_audioset(args.save_path, split="balanced_train", args=args)
    elif args.dl_unbalanced_train:
        dl_audioset(args.save_path, split="unbalanced_train", args=args)
    elif args.dl_eval:
        dl_audioset(args.save_path, split="eval", args=args)
    elif args.dl_train_strong:
        dl_audioset_strong(args.save_path, split="train", args=args)
    elif args.dl_vgg_train:
        dl_vggsound(args.save_path, split="train", args=args)
    elif args.dl_vgg_test:
        dl_vggsound(args.save_path, split="test", args=args)
    elif args.seglist is not None:
        dl_seglist(args.save_path, args.seglist, args=args)
    else:
        raise NotImplementedError
