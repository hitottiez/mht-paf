import colorsys
import os
import random

import cv2

from .util import json_encode


def get_basename(path):
    if path == '':
        raise RuntimeError('パスが不正')
    basename = os.path.basename(path)
    if basename == '':
        return get_basename(os.path.dirname(path))
    else:
        return os.path.splitext(basename)[0]


class FileWriter(object):
    """
    出力結果をファイルに書き出すクラス

    Arguments:
        output: 出力先ディレクトリ
        skip_context: Trueならコンテキストデータを出力しない
        skip_benchmark: Trueならbenchmarkは出力しない
        skip_video: Trueなら動画出力しない
    """

    def __init__(self, output, skip_context=False, skip_benchmark=False, skip_video=False, **kwargs):
        # ルートディレクトリ作成
        self.__makedirs(output)
        # コンテキストログデータ出力ファイル名
        self.context_outpath = os.path.join(output, 'contextlog.dat')
        self.skip_context = skip_context
        self.context_fp = None
        # ベンチマーク出力
        self.benchmark_outpath = os.path.join(output, 'benchmark.dat')
        self.skip_benchmark = skip_benchmark
        self.benchmark_fp = None
        # 動画出力
        self.video_outpath = os.path.join(output, 'video.avi')
        self.skip_video = skip_video
        self.video_fp = None
        self._local_id_color_pairs = {}

    def writeContextData(self, frame_no, timestamp, context_data):
        if self.skip_context:
            return
        result_data = {
            'frame_no': frame_no,
            'timestamp': timestamp,
            'context': context_data
        }
        if self.context_fp is None:
            self.context_fp = open(self.context_outpath, 'w')
        self.context_fp.write(json_encode(result_data) + '\n')

    def writeFrame(self, frame, context_data):
        if self.skip_video:
            return
        h, w, _ = frame.shape
        if self.video_fp is None:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.video_fp = cv2.VideoWriter(self.video_outpath, fourcc, 15.0, (w, h))
        self.video_fp.write(self.__draw_frame(frame, context_data))

    def release(self):
        logger.info('Writer Release')
        if self.context_fp is not None:
            self.context_fp.close()
        if self.benchmark_fp is not None:
            self.benchmark_fp.close()
        if self.video_fp is not None:
            self.video_fp.release()

    def __makedirs(self, dirpath):
        """
        出力ディレクトリを作成する

        Arguments:
            dirpath: 出力ディレクトリ
        """
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

    def __draw_frame(self, frame, context_data):
        """
        フレームにコンテキストデータを描画する

        Arguments:
            frame: 画像データ
            context_data: 当該フレームのコンテキストデータ
        """
        frame = frame.copy()
        white = (255, 255, 255)
        for context in context_data:
            loc = [int(x) for x in context['location']]
            color = self._generate_random_color(context['local_id'])
            cv2.rectangle(frame, (loc[0], loc[1]), (loc[2], loc[3]),
                          color, 2)

            cv2.putText(frame, str(context['local_id']), (loc[0], loc[1] + 15),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7,
                        color=white, thickness=2)
            label_y_offset = 35
            for label in context['action']['label']:
                if label != 'NoAction':
                    cv2.putText(frame, label, (loc[0], loc[1] + label_y_offset),
                                fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7,
                                color=white, thickness=2)
                    label_y_offset += 20
        return frame

    def _generate_random_color(self, local_id):
        if local_id in self._local_id_color_pairs:
            return self._local_id_color_pairs[local_id]

        h = random.random()
        s = 0.3 + random.random() / 2.0
        l = 0.3 + random.random() / 5.0
        self._local_id_color_pairs[local_id] = \
            [int(255 * i) for i in colorsys.hls_to_rgb(h, l, s)]
        return self._local_id_color_pairs[local_id]
