import datetime as dt
import multiprocessing as mp
import os

import pandas as pd
from tqdm import tqdm
from yt_dlp import YoutubeDL
import time
import subprocess


def _download_video_shell(x):
    ytid, start, end, out_dir,  = x

    start_dt, end_dt = dt.timedelta(milliseconds=start), dt.timedelta(milliseconds=end)
    ydl_opts = {
        "outtmpl": f"{out_dir}/[{ytid}]-[{start // 1000}-{end // 1000}].%(ext)s",
        "format": "(bestvideo[height<=640]/bestvideo[ext=webm]/best)+(bestaudio[ext=webm]/best[height<=640])",
        "postprocessors": [
            {
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',  # one of avi, flv, mkv, mp4, ogg, webm
            }
        ],
        "quiet": True,
        "no-mtime": True,
    }
    yturl = f'https://youtube.com/watch?v={ytid}'
    section_opt = f"*{start_dt}-{end_dt}"
    cmd = f'yt-dlp -f "{ydl_opts["format"]}" {yturl} ' \
          f'--download-sections {section_opt} ' \
          f'--quiet ' \
          f'--output "{ydl_opts["outtmpl"]}"'
    try:
        time.sleep(0.3)
        subprocess.run(cmd, shell=True, timeout=100)
    except subprocess.CalledProcessError as e:
        print(e)
    except KeyboardInterrupt:
        raise


def _download_audio(x):
    ytid, start, end, out_dir,  = x
    start_dt, end_dt = dt.timedelta(milliseconds=start), dt.timedelta(milliseconds=end)
    ydl_opts = {
        "outtmpl": f"{out_dir}/[%(id)s]-[{start//1000}-{end//1000}].%(ext)s",
        "format": "bestaudio[ext=webm]/bestaudio/best",
        "external_downloader": "ffmpeg",
        "external_downloader_args": ["-ss", str(start_dt), "-to", str(end_dt), "-loglevel", "panic"],
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }
        ],
        "quiet": True,
        "no-mtime": True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={ytid}"])
    except KeyboardInterrupt:
        raise
    except Exception:
        pass


def download_ps(ytid, st_list, ed_list, save_path, target, desc=None):
    with mp.Pool(processes=max(mp.cpu_count(), 8)) as pool, tqdm(total=len(ytid), desc=desc) as pbar:
        if target == 'audio':
            for _ in tqdm(pool.imap(_download_audio, zip(ytid, st_list, ed_list, [save_path] * len(ytid))), total=len(ytid)):
                pbar.update()
        elif target == 'video':
            for _ in tqdm(pool.imap(_download_video_shell, zip(ytid, st_list, ed_list, [save_path] * len(ytid)))):
                pbar.update()
        else:
            raise NotImplementedError(f'target {target} is not implemented yet.')


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
