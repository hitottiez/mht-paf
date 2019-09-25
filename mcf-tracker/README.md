# mcf-tracker

このリポジトリは、[オリジナル](https://github.com/nwojke/mcf-tracker#installation)をカスタマイズして、学習時に行動認識特徴量を使用するようにしたソースを含んでいます。

## クローン＆Dockerビルド

```
git clone --recursive https://github.com/hitottiez/mcf-tracker.git
cd mcf-tracker
docker build -t <tagname> .
```

## Docker起動&コンテナログイン&セットアップ

もしデータセットを特定のディレクトリで管理している場合は、以下のようにマウントして下さい。

```
docker run -d -it --name <container_name> \
    --mount type=bind,src=/<path/to/mcf-tracker>/,dst=/opt/multi_actrecog/mcf-tracker \
    --mount type=bind,src=/<path/to/dataset>/,dst=/mnt/dataset \
    <image name> /bin/bash
```

正常に起動したら、以下のコマンドでログインします。

```
docker exec -it <container_name> /bin/bash
```

`make`コマンドを実行します。
```
make
```

## 学習

事前にffmpegでokutamaデータセットを画像に展開し、各特徴量ファイル(`det.txt`, `cnn.txt`, `{rgb, flow, fusion}_.txt`)を所定の場所に設置する必要があります。
詳細は[mht-paf](https://github.com/hitottiez/mht-paf)を参照して下さい。

以下はデータセットを`/mnt/dataset/okutama_3840_2160/`に設置し、`rgb_tsn.txt`を使用して学習する例です。
もし行動認識特徴量を使用しない場合は、`--tsn_modality`を`none`にしてください（mcf-trackerオリジナルと同じ挙動になります）。

```
python okutama_trainer.py \
        --data_root /mnt/dataset/okutama_3840_2160/ \
        --tsn_modality rgb \
        --model_prefix rgb
```

実行完了後、同じディレクトリに`rgb_observation_cost_model.pkl`と`rgb_transition_cost_model.pkl`が作成されます。

## 追跡実行

上記コマンドで学習した後は、以下のコマンドで追跡を実行できます。

```
python okutama_tracking_app.py \
    --data_root /mnt/dataset/okutama_action_dataset/okutama_3840_2160/ \
    --save_root /mnt/dataset/okutama_action_dataset/mcf-tracker_tracking_result \
    --tsn_modality rgb \
    --observation_cost_model rgb_observation_cost_model.pkl \
    --transition_cost_model	rgb_transition_cost_model.pkl \
    --observation_cost_bias -3 \
    --make_movie
```

学習時に`--tsn_modality`を`none`した場合でも、`--tsn_modality`は`rgb`で構いません。
内部の処理では行動認識特徴量を無視して処理されます。


実行完了後、`/mnt/dataset/okutama_action_dataset/mcf-tracker_tracking_result`に
以下のディレクトリ構造で結果が`contextlog.dat`に出力されます。

```
/mnt/dataset/okutama_action_dataset/test_result/
├── 1.1.8
│   └── contextlog.dat
├── 1.1.9
├── 1.2.1
├── 1.2.10
├── 1.2.3
├── 2.1.8
├── 2.1.9
├── 2.2.1
├── 2.2.10
└── 2.2.3
```

## 評価

DeepSORTのコンテナにてMOTA,行動認識mAP評価プログラムを実行して下さい。
詳細は[DeepSORTリポジトリ](https://github.com/hitottiez/deepsort)を参照して下さい。