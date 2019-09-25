import argparse
import datetime
import json
import numpy as np
import pandas as pd
import os
import pickle
import pymotutils
import warnings

import min_cost_flow_pymot
from okutama_modules.action_master import ActionMaster
from okutama_modules.FileWriter import FileWriter
from okutama_modules.okutama_main_loop import MainLoop

warnings.filterwarnings("default", category=DeprecationWarning)


def parse_args():
    parser = argparse.ArgumentParser(description="Min-cost flow tracking")
    parser.add_argument('--data_root', help='okutama-Action dataset dir')
    parser.add_argument('--model_save_dir', default='.', help='save model dir')
    parser.add_argument('--tsn_modality', required=True,
                        choices=['rgb', 'flow', 'fusion', 'none'])
    parser.add_argument(
        "--min_confidence", help="Detector confidence threshold", type=float,
        default=None)
    parser.add_argument(
        "--max_num_misses",
        help="Maximum number of consecutive misses before a track should be "
        "dropped.", type=int, default=5)
    parser.add_argument(
        "--n_estimators", help="Number of gradient boosting stages", type=int,
        default=200)
    parser.add_argument("--model_prefix", default='')
    return parser.parse_args()


def main():
    args = parse_args()

    rgb_dir = os.path.join(args.data_root, 'images')
    label_dir = os.path.join(args.data_root, 'labels/train')
    os.makedirs(args.model_save_dir, exist_ok=True)

    does_use_tsn = args.tsn_modality != 'none'
    trainer = min_cost_flow_pymot.MinCostFlowTrainer(does_use_tsn)

    for label_file in sorted(os.listdir(label_dir)):
        label_path = os.path.join(label_dir, label_file)
        print('collecting training data from {}'.format(label_path))

        movie_name, _ = os.path.splitext(label_file)
        image_dir = os.path.join(rgb_dir, movie_name)

        with open(os.path.join(image_dir, 'feature_results/det.txt'), 'r') as f:
            lines = f.readlines()
        cnn_f = open(os.path.join(image_dir, 'feature_results/cnn.txt'), 'r')
        if does_use_tsn:
            tsn_f = open(os.path.join(image_dir, 'feature_results/{}_tsn.txt'.format(args.tsn_modality)))
        else:
            tsn_f = None

        detections = _read_detections(lines, cnn_f, tsn_f)
        ground_truth = _read_groundtruth(label_path)
        trainer.add_dataset(ground_truth, detections, args.max_num_misses)

    print("Training observation cost model ...")
    observation_cost_model = trainer.train_observation_cost_model()
    obserbasion_cost_model_path = os.path.join(
        args.model_save_dir, args.model_prefix + '_observation_cost_model.pkl')
    with open(obserbasion_cost_model_path, "wb") as f:
        pickle.dump(observation_cost_model, f)

    print("Training transition cost model ...")
    transition_cost_model = trainer.train_transition_cost_model(
        args.n_estimators)
    transition_cost_model_path = os.path.join(
        args.model_save_dir, args.model_prefix + '_transition_cost_model.pkl')
    with open(transition_cost_model_path, "wb") as f:
        pickle.dump(transition_cost_model, f)

    print("Done")


def _read_detections(lines, cnn_f, tsn_f):
    # see motchallenge_devkit.py create_data_source
    detections = {i: [] for i in range(len(lines))}
    for frame_idx, line in enumerate(lines):
        _, boxes = line.split(' ')  # no use image_filename
        box_list = json.loads(boxes)
        cnn = json.loads(cnn_f.readline())
        cnn_features = np.array([dic['features'] for dic in cnn])

        if tsn_f is not None:
            tsn = json.loads(tsn_f.readline())
            tsn_features = np.array([dic['before_fc_features'] for dic in tsn])

        # flow, fusionの場合1フレーム目のデータが存在しないのでスキップ
        if frame_idx == 0:
            continue

        boxes = np.array([dic['box'] for dic in box_list])
        boxes = np.array([(box[0], box[1], box[2] - box[0], box[3] - box[1])
                          for box in boxes], dtype=float)
        box_scores = np.array([dic['score'] for dic in box_list], dtype=float)

        for i in range(len(boxes)):
            detections[frame_idx].append(
                pymotutils.RegionOfInterestDetection(
                    frame_idx, boxes[i], box_scores[i], xyz=None))
            # see pymotutils.py compute_features
            setattr(detections[frame_idx][i], 'feature',
                    cnn_features[i])
            if tsn_f is not None:
                setattr(detections[frame_idx][i], 'tsn_feature',
                        tsn_features[i])
    return detections


def _read_groundtruth(label_file):
    """
    label_file: VATIC format filepath
        local_id
        xmin
        ymin
        xmax
        ymax
        frame
        lost
        occuluded
        generated
        name
        action
    """

    # see motchallnge_io.py read_groundtruth
    ground_truth = pymotutils.TrackSet()
    df = pd.read_csv(label_file, sep=' ', names=[
                     0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    # ignore when lost or occuluded
    df = df[(df[6] != 1) & (df[7] != 1)]
    # change bbox format from (xmin, ymin, xmax, ymax)
    # to (xmin, ymin, width, height)
    df[3] -= df[1]
    df[4] -= df[2]
    for i in range(len(df)):
        row = df.iloc[i]
        frame_idx, track_id = int(row[5]), int(row[0])
        sensor_data = np.asarray(row[1:5])
        if track_id not in ground_truth.tracks:
            ground_truth.create_track(track_id)
        ground_truth.tracks[track_id].add(
            pymotutils.Detection(frame_idx, sensor_data, do_not_care=False))

    return ground_truth

if __name__ == "__main__":
    main()
