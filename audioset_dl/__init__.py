import datetime as dt
import multiprocessing as mp
import os

import pandas as pd
from tqdm import tqdm
from yt_dlp import YoutubeDL
import time
import subprocess
from subprocess import Popen, PIPE



def _download_shell(x):
    ytid, start, end, out_dir,  = x

    start_dt, end_dt = dt.timedelta(milliseconds=start), dt.timedelta(milliseconds=end)
    # print(f"{'-' * 30} | {ytid} {start_dt} ({start}) to {end_dt} ({end}). Section: *{start//1000}-{end//1000} | {'-' * 30}")
    ydl_opts = {
        "outtmpl": f"{out_dir}/[{ytid}]-[{start // 1000}-{end // 1000}].%(ext)s",
        "format": "(bestvideo[height<=640]/bestvideo[ext=webm]/best)+(bestaudio[ext=webm]/best[height<=640])",

        "postprocessors": [
            {
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',  # one of avi, flv, mkv, mp4, ogg, webm
            }
        ],
        # "postprocessor_args": ["-ss", str(start_dt), "-to", str(end_dt)],  # 이건 먹히지 않음. postprocessor_args 라는 키가 ffmpeg에 존재하지 않음
        "quiet": True,
        "no-mtime": True,
    }

    yturl = f'https://youtube.com/watch?v={ytid}'
    # yturl = f'https://www.youtube.com/watch?v={ytid}'
    # section_opt = f"*{start // 1000}-{end // 1000}"
    section_opt = f"*{start_dt}-{end_dt}"
    cmd = f'yt-dlp -f "{ydl_opts["format"]}" {yturl} ' \
          f'--download-sections {section_opt} ' \
          f'--quiet ' \
          f'--output "{ydl_opts["outtmpl"]}"'
    print(cmd)
    try:
        time.sleep(0.3)
        # subprocess.run("exit 1", shell=True, check=True, timeout=15, capture_output=True)
        subprocess.run(cmd, shell=True, timeout=100)
    except subprocess.CalledProcessError as e:
        print(e)
    except KeyboardInterrupt:
        raise


def _download(x):

    ytid, start, end, out_dir,  = x
    # if ytid != "b0RFKhbpFJA":
    #     print('sleeping....')
    #     time.sleep(10)

    start_dt, end_dt = dt.timedelta(milliseconds=start), dt.timedelta(milliseconds=end)
    print(f"{'-' * 30} | {ytid} {start_dt} ({start}) to {end_dt} ({end}). Section: *{start//1000}-{end//1000} | {'-' * 30}")
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

        # "external_downloader_args": ["-ss", f"{str(start_dt)}.00", "-to", f"{str(end_dt)}.00", "-loglevel", "info"],
        # "external_downloader_args": ["-ss", str(start_dt), "-to", str(end_dt), "-loglevel", "panic"],


        # "external_downloader": "ffmpeg",
        # "external_downloader_args": ["-ss", f"{str(start_dt)}", "-t", f"0:00:10.00", "-loglevel", "info"],
        # "download-sections": f"*{start_dt}-{end_dt}",
        # "download-sections": f"*{start//1000}-{end//1000}",

        # "download_ranges": lambda x: [
        #     {'start_time': str(start // 1000),
        #      'end_time': str(end // 1000)}
        # ],
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
        "no-mtime": True,
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
        # for _ in tqdm(pool.imap(_download, zip(ytid, st_list, ed_list, [save_path] * len(ytid)))):
        for _ in tqdm(pool.imap(_download_shell, zip(ytid, st_list, ed_list, [save_path] * len(ytid)))):
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
