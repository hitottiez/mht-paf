# mht-paf

## 要件

NVIDIA driver(>= 410.48)
Docker(>= 17.12.0)
nvidia-docker2
docker-compose(>= 1.21.0)

## セットアップ

クローンして、ビルドを行います。
```
git clone --recursive https://github.com/hitottiez/mht-paf.git
cd mht-paf
cp env.default .env
docker-compose build
```

`docker-compose up -d`で起動します。
```
docker-compose up -d
docker-compose ps
        Name             Command    State          Ports        
----------------------------------------------------------------
mht-paf_deepsort_1      /bin/bash   Up                          
mht-paf_mcf-tracker_1   /bin/bash   Up                          
mht-paf_tsn_1           /bin/bash   Up      0.0.0.0:8888->80/tcp
```

## コンテナログイン＆ログアウト方法

各コンテナには以下のコマンドでログインします。

```
docker-compose exec <deepsort or mcf-tracker or tsn> bash
```

もしくは、各リポジトリのREADME.mdに記述されているログイン方法を使用しても構いません。

コンテナからログアウト場合は`exit`でログアウトします。
```
exit
```

## データセットの準備

注意：  
データセットは`dataset`ディレクトリに置く想定で構成されています。
設置場所を変更したい場合は、`.env`ファイルの`DATASET_DIR`を変更して下さい。

[未定：データセットの設置場所](https://examplle.com)より特徴量ファイル一式をダウンロードします。

ディレクトリ構成は以下の用になっています。
```
dataset
└── images
     ├── 1.1.1
     │   └── feature_results
     │       ├── cnn.txt
     │       ├── det.txt
     │       └── fusion_tsn.txt
     ├── 1.1.2
     ├── 1.1.3
     ...
     ├── 2.2.10
     └── 2.2.11
```

[Okutama-Actionデータセット](https://github.com/miquelmarti/Okutama-Action)から、動画一式とSingleActionTrackingLabels、MultiActionLabelsをダウンロードします。

ラベルは以下のように`images`ディレクトリと同じ階層に設置します。

```
dataset
├── images
│
├── labels # SingleActionTrackingLabels
│   ├── test
│   │   ├── 1.1.8.txt
│   │   ├── 1.1.9.txt
│   │   ...
│   │   └── 2.2.10.txt
│   └── train
│        ├── 1.1.1.txt
│        ├── 1.1.2.txt
│        ...
│        └── 2.2.11.txt
│
└── multi_labels # MultiActionLabels labelsと同様の構成のため、省略
```

動画一式から、以下のffmpegコマンドでJPG画像を作成します。
ffmpegは`deepsort`または`mcf-tracker`コンテナで実行可能です。
```
docker-compose exec deepsort bash

# in deepsort container
ffmpeg -i <path/to/download>/Train-Set/Drone1/Morning/1.1.1.mov  -vcodec mjpeg -start_number 0 <path/to/dataset>/images/1.1.1/%d.jpg
ffmpeg -i <path/to/download>/Train-Set/Drone1/Morning/1.1.10.mp4  -vcodec mjpeg -start_number 0 <path/to/dataset>/images/1.1.10/%d.jpg
...
ffmpeg -i <path/to/download>/Train-Set/Drone2/Noon/2.2.11.mp4  -vcodec mjpeg -start_number 0 <path/to/dataset>/images/2.2.11/%d.jpg &
```

## 追跡、評価

[deepsort](https://github.com/hitottiez/deepsort)、[mcf-tracker](https://github.com/hitottiez/mcf-tracker)のREADMEを参考に、追跡、評価を実行して下さい。