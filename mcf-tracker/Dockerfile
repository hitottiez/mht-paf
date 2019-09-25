FROM nvidia/cuda:8.0-cudnn6-devel-ubuntu16.04

# --------------------------------------------------------------
# Pyenvのインストール
# --------------------------------------------------------------

# apt-get, aptitudeのDL
RUN    apt-get update \
    && apt-get install -y aptitude \
    && apt-get clean

# 周辺コンポーネントのインストール
RUN    aptitude install -y python-pip \
    && aptitude install -y git gcc make openssl libssl-dev libbz2-dev libreadline-dev libsqlite3-dev \
    && apt-get clean

# pyenvダウンロード／設置
RUN    cd /usr/local \
    && git clone https://github.com/yyuu/pyenv.git ./pyenv \
    && cd pyenv \
    && cd ../ \
    && mkdir -p ./pyenv/versions ./pyenv/shims

ENV PYENV_ROOT /usr/local/pyenv
ENV PATH ${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}

# Anacondaインストール
RUN    apt-get update \
    && apt-get install -y aria2 bzip2 \
    && pyenv install -v anaconda3-5.0.1 \
    && pyenv rehash \
    && pyenv global anaconda3-5.0.1 \
    && apt-get clean

# Condaのアップデート
RUN    conda update anaconda \
    && conda update conda \
    && conda update --all

# --------------------------------------------------------------
# OpenCVのインストール
# --------------------------------------------------------------


# 必要なコンポーネントのインストール
RUN    apt-get update \
    && apt-get install -y libopencv-dev  build-essential \
    checkinstall cmake libgtk2.0-dev  pkg-config yasm \
    python-dev python-numpy libdc1394-22 \
    libdc1394-22-dev libjpeg-dev libpng12-dev \
    libjasper-dev libavcodec-dev libavformat-dev \
    libswscale-dev libgstreamer0.10-dev \
    libgstreamer-plugins-base0.10-dev libv4l-dev \
    libtbb-dev libqt4-dev libfaac-dev libmp3lame-dev \
    libopencore-amrnb-dev libopencore-amrwb-dev \
    libtheora-dev libvorbis-dev libxvidcore-dev x264 \
    v4l-utils libxine2-dev libtiff5-dev \
    && apt-get install -y wget \
    && apt-get clean

# OpenCVインストール
RUN    mkdir -p /root/opencv \
    && cd /root/opencv \
    && wget https://github.com/opencv/opencv/archive/3.2.0.tar.gz -O opencv3.2.0.tar.gz \
    && wget https://github.com/opencv/opencv_contrib/archive/3.2.0.tar.gz -O opencv_contrib3.2.0.tar.gz \
    && tar xvzf opencv3.2.0.tar.gz \
    && tar xvzf opencv_contrib3.2.0.tar.gz \
    && cd opencv-3.2.0 \
    && mkdir release \
    && cd release \
    && cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D BUILD_opencv_java=OFF \
    -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib-3.2.0/modules \
    -D WITH_CUDA=ON \
    -D BUILD_TIFF=ON \
    -D BUILD_opencv_python2=OFF \
    -D BUILD_opencv_python3=ON \
    -D PYTHON3_EXECUTABLE=/usr/local/pyenv/shims/python \
    -D PYTHON_INCLUDE_DIR=/usr/local/pyenv/versions/anaconda3-5.0.1/include/python3.6m \
    -D PYTHON3_LIBRARY=/usr/local/pyenv/versions/anaconda3-5.0.1/lib \
    -D PYTHON3_NUMPY_INCLUDE_DIRS=/usr/local/pyenv/versions/anaconda3-5.0.1/lib/python3.6/site-packages/numpy/core/include \
    -D PYTHON3_PACKAGES_PATH=/usr/local/pyenv/versions/anaconda3-5.0.1/lib/python3.6/site-packages \
    .. \
    && make -j$(nproc) \
    && make install \
    && cd /root/opencv \
    && rm opencv3.2.0.tar.gz \
    && rm opencv_contrib3.2.0.tar.gz

# --------------------------------------------------------------
# Boost、Eigen3のインストール
# --------------------------------------------------------------

# Boostライブラリ、Boost.NumPyインストール (libboost_python3でアクセスできるように、シンボリックリンクも作成する)
RUN    conda install -y -c conda-forge boost=1.64.0 \
    && apt-get install -y libeigen3-dev
ENV BOOST_ROOT /usr/local/pyenv/versions/anaconda3-5.0.1/

RUN pip install scikit-learn==0.21.0

# --------------------------------------------------------------
# 言語設定／時間設定インストール
# --------------------------------------------------------------
RUN    apt-get update \
    && apt-get install -y language-pack-ja-base language-pack-ja
ENV LC_ALL ja_JP.UTF-8

# ホストoSのlocaltimeをマウント(読み込み専用)
VOLUME /etc/localtime:/etc/localtime:ro

# タイムゾーン設定
RUN    apt-get install -y tzdata \
    && apt-get clean
ENV TZ Asia/Tokyo

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /opt/multi_actrecog/mcf-tracker
