import json
import os

import numpy as np

import cv2
import pymotutils


def interpolate_track_set(track_set):
    """Interpolate sensor data in given track set.

    This method uses linear interpolation to fill missing detections in each
    track of the given track set. Each dimension of the sensor data is
    interpolated independently of all others.

    For example, if the sensor data contains 3-D positions, then the X, Y, and Z
    coordinates of the trajectory are interpolated linearily. The same method
    works fairly well for image regions as well.

    Parameters
    ----------
    track_set : TrackSet
        The track set to be interpolated. The sensor data must be an array_like
        (ndim=1).

    Returns
    -------
    TrackSet
        The interpolated track set, where each target is visible from the first
        frame of appearance until leaving the scene.

    """
    interp_set = pymotutils.TrackSet()
    for tag, track in track_set.tracks.items():
        first, last = track.first_frame_idx(), track.last_frame_idx()
        frame_range = np.arange(first, last + 1)

        # フレームのインデックス
        xp = sorted(list(track.detections.keys()))

        if len(xp) == 0:
            continue  # This is an empty trajectory.

        # BBoxのリスト
        sensor_data = np.asarray([track.detections[i].sensor_data for i in xp])

        # sensor_data
        # array([[1475.,  109.,   99.,   96.],
        #    [1473.,  115.,   95.,   95.],
        #    [1473.,  123.,   92.,   96.],
        #    ...,
        #    [1683., 2083.,   57.,   56.],
        #    [1681., 2091.,   59.,   51.],
        #    [1678., 2097.,   59.,   45.]])

        # fps = [[xmin1, xmin2, ...,], [ymin1, ymin2, ...], ...]
        fps = [sensor_data[:, i] for i in range(sensor_data.shape[1])]
        # fps = [array([1475., 1473., 1473., 1470., 1470., 1467., 1467., 1464., 1464.,
        #    1461., 1461., 1458., 1456., 1453., 1450., 1447., 1444., 1442.,
        #    1439., 1436., 1436., 1433., 1430., 1428., 1428., 1425., 1422.,
        #    1422., 1419., 1416., 1416., 1413., 1413., 1411., 1411., 1408.,
        #    1408., 1405., 1405., 1402., 1402., 1399., 1399., 1397., 1397.,
        #    1394., 1394., 1391., 1391., 1388., 1388., 1388., 1388., 1388., ...]

        # len(fps) = 4

        # 線形補間
        interps = [np.interp(frame_range, xp, fp) for fp in fps]

        # 補完したデータでtrackを作り直し
        itrack = interp_set.create_track(tag)
        for i, frame_idx in enumerate(frame_range):
            sensor_data = np.array([interp[i] for interp in interps])
            do_not_care = frame_idx not in track.detections
            tsn_scores = None if frame_idx not in track.detections else track.detections[frame_idx].tsn_scores
            itrack.add(pymotutils.Detection(frame_idx, sensor_data, do_not_care,
            tsn_scores=tsn_scores))
    return interp_set


class ActionStore(object):
    def __init__(self):
        self.frame_actionscore_pairs = {}

    def store(self, frame_idx, scores):
        self.frame_actionscore_pairs[frame_idx] = scores

    def get_prev_and_future_scores(self, frame_idx, frame_num):
        tsn_scores = []
        for idx in range(frame_idx - frame_num, frame_idx + frame_num + 1):
            if idx in self.frame_actionscore_pairs:
                tsn_scores.append(self.frame_actionscore_pairs[idx])
        return tsn_scores


class MainLoop(object):

    def __init__(self, writer, master, rgb_dir, tracker, does_make_movie=True):
        self.writer = writer
        self.master = master
        self.rgb_dir = rgb_dir

        # cnn.txt tsn.txt, det.txt
        self.features_base_path = os.path.join(rgb_dir, 'feature_results')

        self.tracker = tracker
        self.does_make_movie = does_make_movie

        self.tsn_segment = 7
        self.tsn_score_threshold = 0.4

    def _apply_nonmaxma_suppression(self, boxes, box_scores, cnn_features,
                                    tsn_fetures, tsn_scores, max_bbox_overlap=0.5):
        indicies = pymotutils.preprocessing.non_max_suppression(
            boxes, max_bbox_overlap, box_scores)
        new_boxes = np.asarray([boxes[i] for i in indicies])
        new_scores = np.asarray([box_scores[i] for i in indicies])
        new_cnn_features = np.asarray([cnn_features[i] for i in indicies])
        new_tsn_features = np.asarray([tsn_fetures[i] for i in indicies])
        new_tsn_scores = np.asarray([tsn_scores[i] for i in indicies])
        return new_boxes, new_scores, new_cnn_features, new_tsn_features, new_tsn_scores

    def __call__(self, tsn_modality=None):
        tsn_f = open(os.path.join(self.features_base_path,
                                  '{}_tsn.txt'.format(tsn_modality)))
        cnn_f = open(os.path.join(self.features_base_path, 'cnn.txt'))
        with open(os.path.join(self.features_base_path, 'det.txt'), 'r') as f:
            lines = f.readlines()

        print('process {}'.format(self.rgb_dir))
        process_frame = -1
        for line in lines:
            process_frame += 1

            _, boxes = line.split(' ')  # no use image_filename
            box_list = json.loads(boxes)

            # mcf-trackerの入力は(xmin, ymin, width, height)なので、
            # bboxを (xmin, ymin, xmax, ymax) -> (xmin, ymin, width, height) に変換する
            boxes = [dic['box'] for dic in box_list]
            boxes = np.array([(box[0], box[1], box[2] - box[0],
                               box[3] - box[1]) for box in boxes], dtype=float)
            box_scores = np.array([dic['score']
                                   for dic in box_list], dtype=float)

            cnn = cnn_f.readline()
            cnn = json.loads(cnn)
            cnn_features = np.array([dic['features'] for dic in cnn])

            tsn = tsn_f.readline()
            tsn = json.loads(tsn)

            # flow,fusionの場合、1フレーム目は存在しないのでスキップ
            if process_frame == 0:
                continue

            tsn_features = np.array([dic['before_fc_features'] for dic in tsn])
            tsn_scores = np.array([dic['scores'] for dic in tsn])

            boxes, box_scores, cnn_features, tsn_features, tsn_scores = \
                self._apply_nonmaxma_suppression(
                    boxes, box_scores, cnn_features, tsn_features, tsn_scores)

            # trakcer.processに与える引数のフォーマットは以下（numpy配列）にすればOK
            # boxes
            #   array([[2310.,   95.,   71.,   93.],[1475.,  109.,   99.,   96.]])
            # scores
            #   array([1., 1.])
            # features
            #   array([[ 7.25366399e-02, -9.42650065e-02,  1.90213497e-04, ... -6.15606606e-02, -6.45036027e-02],
            #   [5.69446795e-02, -8.09141099e-02, -8.75954106e-02,
            #   ...
            #   -1.63749605e-02, -2.62882784e-02]], dtype = float32)
            self.tracker.process(boxes, box_scores,
                                 features=cnn_features,
                                 tsn_features=tsn_features,
                                 tsn_scores=tsn_scores)

        # 線形補完＆結果取得
        track_set = self._interpolation()

        frame_range = track_set.frame_range()

        # no tracking, no output
        if len(frame_range) <= 1:
            print('track data is empty')
            return

        # 最初に人が写っていない場合はコンテキストは空
        for frame_idx in range(0, frame_range[0]):
            context = []
            self._output(frame_idx, context)

        # local_id毎の行動認識結果を事前に取得
        tsn_results = {}
        for frame_idx in frame_range:
            context = []
            detections = track_set.collect_detections(frame_idx)
            for local_id, detection in detections.items():
                bbox = detection.sensor_data
                if local_id not in tsn_results:
                    tsn_results[local_id] = ActionStore()
                if detection.tsn_scores is not None:
                    tsn_results[local_id].store(frame_idx, detection.tsn_scores)

        model_ids = [-1, -1, -1, -1]
        action_scores = [0.0, 0.0, 0.0, 0.0]
        for frame_idx in frame_range:
            context = []
            detections = track_set.collect_detections(frame_idx)
            for local_id, detection in detections.items():
                bbox = detection.sensor_data
                tsn_scores = tsn_results[local_id].get_prev_and_future_scores(frame_idx, self.tsn_segment)
                model_ids, action_scores = self._to_action(tsn_scores)

                context.append({
                    'local_id': local_id,
                    'location': from_tlwh_to_tlbr(bbox).astype(int),
                    'action': {
                        'model_id': model_ids,
                        'score': action_scores
                    }
                })
            self._output(frame_idx, context)

        # mcf-trackerのtracking情報に、全フレームの情報があるとは限らず
        # trackingされなくなってからは、フレームの情報がとれない。
        # そうすると、ground_truthとフレームの長さが異なって評価できないので、
        # frame_rangeに存在しないフレーム情報は空で書き込む

        if frame_range[-1] != process_frame - 1:
            empty_range = range(frame_range[-1] + 1, process_frame)
            for frame_idx in empty_range:
                self._output(frame_idx, [])

    def _output(self, frame_idx, context):
        for c in context:
            act_labels = [self.master.findByModelID(model_id) for model_id in c['action']['model_id']]
            c['action']['label'] = act_labels
        self.writer.writeContextData(frame_idx, 0, context)

        if self.does_make_movie:
            filepath = os.path.join(self.rgb_dir, '{:d}.jpg'.format(frame_idx))
            image = cv2.imread(filepath)
            self.writer.writeFrame(image, context)

    def _to_action(self, tsn_scores):
        """
        tsn_scores: all action scores of previous n frames, current frame, and post n frames
        """
        if len(tsn_scores) == 0:
            return [-1, -1, -1, -1], [0.0, 0.0, 0.0, 0.0]

        scores = self._calc_action_scores(tsn_scores)

        # descending sort and get top 4
        top4_idxes = np.argsort(-scores)[:4]
        top4_scores = scores[top4_idxes]

        for i, score in enumerate(top4_scores):
            if score < self.tsn_score_threshold:
                top4_idxes[i] = -1

        return top4_idxes, top4_scores

    def _calc_action_scores(self, tsn_scores):
        tsn_raw_score = np.asarray(tsn_scores)
        tsn_raw_score = tsn_raw_score.mean(axis=0)

        # sigmoid
        return 1 / (1 + np.exp(-tsn_raw_score))

    def _interpolation(self):

        # mcf-trackerオリジナルとほとんど同じ
        # ref:
        #   external/pymotutils/pytmotutils/application/application.py
        #   min_cost_flow_pymot.py

        # just get result
        trajectories = self.tracker.compute_trajectories()

        trajectories = [[
            pymotutils.Detection(
                frame_idx=x[0], sensor_data=x[1], tsn_scores=x[2])
            for x in trajectory
        ] for trajectory in trajectories]

        hypotheses = pymotutils.TrackSet()

        for i, trajectory in enumerate(trajectories):
            track = hypotheses.create_track(i)
            for detection in trajectory:
                track.add(detection)

        # 線形補間
        hypotheses = interpolate_track_set(hypotheses)
        return hypotheses


def from_tlwh_to_tlbr(bbox):
    """
    convert ndarray bounding box
        from (xmin, ymin, width, height)
        to (xmin, ymin, xmax, ymax)
    """
    box = bbox.copy()
    box[2:] = box[:2] + box[2:]
    return box
