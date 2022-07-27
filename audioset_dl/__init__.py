import datetime as dt
import multiprocessing as mp
import os

import pandas as pd
from tqdm import tqdm
from youtube_dl import YoutubeDL
import time


def _download(x):

    ytid, start, end, out_dir,  = x
    # if ytid != "b0RFKhbpFJA":
    #     print('sleeping....')
    #     time.sleep(10)

    start_dt, end_dt = dt.timedelta(milliseconds=start), dt.timedelta(milliseconds=end)
    print(f"{'-' * 30} | {ytid} {start_dt} to {end_dt} | {'-' * 30}")
    ydl_opts = {
        "outtmpl": f"{out_dir}/[%(id)s]-[{start}ms].%(ext)s",
        # "format": "bestaudio/best",  # 오디오만 나와서 그렇지 구간 자르는거랑 개잘됨.
        # "format": "bestvideo/best",  # 비디오만 나오지만 구간 잘 자름.
        # "format": "bestvideo/best+bestaudio/best", # 비디오만 나옴. 구간 굿.
        # "format": "bestvideo[ext=mp4]/best+bestaudio/best", # 비디오만 나옴. 구간 굿.
        # "format": "(bestvideo[ext=mp4]/best)+(bestaudio/best)",  # 소리 나오지만 개판인거 생김
        # "format": "(bestvideo[ext=mp4]/best)+(bestaudio[ext=m4a]/best)",  # 아아 마찬가지 아아아
        "format": "(bestvideo[height<=640]/bestvideo[ext=mp4]/best)+(bestaudio[ext=webm]/best[height<=640])",
        # "format": "bestvideo+bestaudio/best",
        # "format": "135",
        # "format": "135/bestvideo/best+bestaudio/best",
        # "format": "(135[ext=mp4]/135/bestvideo/best)+(bestaudio/best)",  # it works. but some of thme has audio sync issue

        "external_downloader": "ffmpeg",
        "external_downloader_args": ["-ss", f"{str(start_dt)}", "-t", f"0:00:10.00", "-loglevel", "info"],
        # "external_downloader_args": ["-ss", f"{str(start_dt)}.00", "-to", f"{str(end_dt)}.00", "-loglevel", "info"],
        # "external_downloader_args": ["-ss", str(start_dt), "-to", str(end_dt), "-loglevel", "panic"],

        "postprocessors": [
            {
                # "key": "FFmpegExtractAudio",
                # "preferredcodec": "wav",
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',  # one of avi, flv, mkv, mp4, ogg, webm
                # "postprocessor-args": f" -ss {str(start_dt)} -to {str(end_dt)} ",  #  안됨. 엄청빨리 루프가 돌아가고 다운로드가 안됨.

                # "codec": "copy",

            }
        ],
        # "postprocessor_args": ["-ss", str(start_dt), "-to", str(end_dt)],  # 이건 먹히지 않음. postprocessor_args 라는 키가 ffmpeg에 존재하지 않음
        "quiet": True,
        "no_mtime": True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={ytid}"])
    except KeyboardInterrupt:
        raise
    except Exception:
        pass


def download_ps(ytid, st_list, ed_list, save_path, desc=None):
    # with mp.Pool(processes=mp.cpu_count() // 2) as pool, tqdm(total=len(ytid), desc=desc) as pbar:
    with mp.Pool(processes=4) as pool, tqdm(total=len(ytid), desc=desc) as pbar:
        for _ in tqdm(pool.imap(_download, zip(ytid, st_list, ed_list, [save_path] * len(ytid)))):
            pbar.update()


def dl_audioset_strong(save_path, split, percent_from, percent_to):
    path = f"{save_path}/{split}_strong"
    os.makedirs(path, exist_ok=True)
    meta = pd.read_csv(f"audioset_dl/metadata/audioset_{split}_strong.tsv", sep="\t")
    segment_id = pd.Series(meta.segment_id.unique())
    ytid = segment_id.str[:11]
    ytid = _select_id(ytid, percent_from, percent_to)
    start_time = segment_id.str[12:].astype(int)
    end_time = start_time + 10000
    download_ps(ytid, start_time, end_time, path, desc=f"dl_{split}_strong")


def _select_id(ytid, percent_from: int, percent_to: int):
    total = len(ytid)
    idx_from = int(total * (percent_from / 100.))
    idx_to = int(total * (percent_to / 100.))
    return ytid[idx_from : idx_to]


def dl_audioset(save_path, split, percent_from, percent_to):
    path = f"{save_path}/{split}"
    os.makedirs(path, exist_ok=True)
    meta = pd.read_csv(f"audioset_dl/metadata/{split}_segments.csv", header=2, quotechar='"', skipinitialspace=True)
    ytid = meta["# YTID"]
    ytid = _select_id(ytid, percent_from, percent_to)
    start_time = (meta.start_seconds * 1000).astype(int)
    end_time = (meta.end_seconds * 1000).astype(int)
    download_ps(ytid, start_time, end_time, path, desc=f"dl_{split}")


def dl_seglist(save_path, seglist_path):
    path = f"{save_path}/seglist"
    os.makedirs(path, exist_ok=True)
    segment_id = pd.Series(open(seglist_path, "r").read().splitlines())
    ytid = segment_id.str[:11]
    start_time = segment_id.str[12:].astype(int)
    end_time = start_time + 10000
    download_ps(ytid, start_time, end_time, path, desc="dl_seglist")
