import argparse
import os
import pickle

import min_cost_flow_tracker
from okutama_modules.action_master import ActionMaster
from okutama_modules.FileWriter import FileWriter
from okutama_modules.okutama_main_loop import MainLoop


def parse_args():
    parser = argparse.ArgumentParser(description="Min-cost flow tracking")
    parser.add_argument('--data_root', help='okutama-Action dataset dir')
    parser.add_argument('--save_root', help='save result dir')
    parser.add_argument('--worker', default=4, help='multiprocess num')
    parser.add_argument('--make_movie', default=False, action='store_true')
    parser.add_argument('--tsn_modality', required=True,
                        choices=['rgb', 'flow', 'fusion'])
    parser.add_argument(
        "--observation_cost_model",
        help="Path to pickled observation cost model",
        default="motchallenge_observation_cost_model.pkl")
    parser.add_argument(
        "--transition_cost_model",
        help="Path to pickled transition cost model",
        default="motchallenge_transition_cost_model.pkl")
    parser.add_argument(
        "--entry_exit_cost",
        help="A cost term for starting and ending trajectories. A lower cost "
        "results in increased fragmentations/shorter trajectories.",
        type=float, default=10.0)
    parser.add_argument(
        "--observation_cost_bias",
        help="A bias term that is added to all observation costs. A value "
        "larger than zero results in more object trajectories. A value smaller "
        "than zero results in fewer object trajectories.",
        type=float, default=0.0)
    parser.add_argument(
        "--max_num_misses",
        help="Maximum number of consecutive misses before a track should be "
             "dropped.",
        type=int, default=5)
    parser.add_argument(
        "--miss_rate", help="Detector miss rate in [0, 1]", type=float,
        default=0.3)
    parser.add_argument(
        "--optimizer_window_len",
        help="If not None, the tracker operates in online mode where a "
        "fixed-length history of frames is optimized at each time step. If "
        "None, trajectories are computed over the entire sequence (offline "
        "mode).", type=int, default=30)
    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.observation_cost_model, "rb") as f:
        observation_cost_model = pickle.load(f)
    with open(args.transition_cost_model, "rb") as f:
        transition_cost_model = pickle.load(f)

    rgb_dir = os.path.join(args.data_root, 'images')
    label_dir = os.path.join(args.data_root, 'labels/test')

    for label_file in sorted(os.listdir(label_dir)):
        master = ActionMaster(data_type='okutama')

        movie_name, _ = os.path.splitext(label_file)

        writer = FileWriter(output=os.path.join(args.save_root, movie_name))
        image_dir = os.path.join(rgb_dir, movie_name)

        tracker = min_cost_flow_tracker.MinCostFlowTracker(
            args.entry_exit_cost, observation_cost_model,
            transition_cost_model, args.max_num_misses, args.miss_rate,
            optimizer_window_len=args.optimizer_window_len,
            observation_cost_bias=args.observation_cost_bias)

        mainloop = MainLoop(writer, master, image_dir, tracker,
                            does_make_movie=args.make_movie)
        mainloop(tsn_modality=args.tsn_modality)


if __name__ == "__main__":
    main()
