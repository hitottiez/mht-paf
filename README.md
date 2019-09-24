# mht-paf

***All codes will be available in September.***  
***Video results of all sequences and trained models can be downloaded in [Google drive](https://drive.google.com/open?id=1udPbQyfa8DSMYQARuZQfRng4g_UArVhC).***

Multiple Human Tracking using Multi-Cues including Primitive Action Features  
Hitoshi Nishimura, Kazuyuki Tasaka, Yasutomo Kawanishi, Hiroshi Murase  
https://arxiv.org/abs/1909.08171

MCF
![MCF](https://github.com/hitottiez/mht-paf/blob/master/docs/without.gif)
MHT-PAF
![MHT-PAF](https://github.com/hitottiez/mht-paf/blob/master/docs/with.gif)

## Requirements

- NVIDIA driver (>= 410.48)
- Docker (>= 17.12.0)
- nvidia-docker2
- docker-compose (>= 1.21.0)

## Setup

Clone this repository and build a docker image using docker-compose:
```
git clone --recursive https://github.com/hitottiez/mht-paf.git
cd mht-paf
cp env.default .env
docker-compose build
```

Start a docker container:
```
docker-compose up -d
docker-compose ps
        Name             Command    State          Ports        
----------------------------------------------------------------
mht-paf_deepsort_1      /bin/bash   Up                          
mht-paf_mcf-tracker_1   /bin/bash   Up                          
mht-paf_tsn_1           /bin/bash   Up      0.0.0.0:8888->80/tcp
```

## Login/Logout docker container

Login each container:
```
docker-compose exec <deepsort or mcf-tracker or tsn> bash
```
or, follow the README.md in each repository.

Logout each container:
```
exit
```

## Prepare dataset
Note:  
Dataset is assumed to be in the `dataset` directory.
If you change the dataset directory, change `DATASET_DIR` in the `.env` file.

Download all feature files from [Google drive](https://drive.google.com/open?id=1udPbQyfa8DSMYQARuZQfRng4g_UArVhC).

Directory structure:
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

Download all videos and labels (SingleActionTrackingLabels, MultiActionLabels) from [Okutama-Action dataset](https://github.com/miquelmarti/Okutama-Action).

The labels are set in the `images` directory:
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
└── multi_labels # as same as MultiActionLabels labels
```

Convert videos to JPG images using ffmpeg:
```
docker-compose exec deepsort bash

# in deepsort/mcf-tracker container
ffmpeg -i <path/to/download>/Train-Set/Drone1/Morning/1.1.1.mov  -vcodec mjpeg -start_number 0 <path/to/dataset>/images/1.1.1/%d.jpg
ffmpeg -i <path/to/download>/Train-Set/Drone1/Morning/1.1.10.mp4  -vcodec mjpeg -start_number 0 <path/to/dataset>/images/1.1.10/%d.jpg
...
ffmpeg -i <path/to/download>/Train-Set/Drone2/Noon/2.2.11.mp4  -vcodec mjpeg -start_number 0 <path/to/dataset>/images/2.2.11/%d.jpg &
```

## Tracking and evaluation
Refer [deepsort](https://github.com/hitottiez/deepsort) and [mcf-tracker](https://github.com/hitottiez/mcf-tracker).
