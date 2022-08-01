from setuptools import setup, find_packages

setup(
    name="audioset_dl",
    version="0.1",
    packages=find_packages(),
    install_requires=["tqdm", "pandas", "yt_dlp"]
)