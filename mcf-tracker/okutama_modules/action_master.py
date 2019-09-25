# 行動マスタ取得

import logging
logger = logging.getLogger(__name__)

class ActionMaster:

    def __init__(self, data_type):
        if data_type == 'poc2':
            action_list = ['Working', 'Sleeping', 'Cooking', 'Exercise',
                           'Cleaning', 'Eating', 'Reading', 'Internet',
                           'Relaxing', 'Communication']
        elif data_type == 'ucf24':
            action_list = ['Basketball', 'BasketballDunk', 'Biking',
                           'CliffDiving', 'CricketBowling', 'Diving',
                           'Fencing', 'FloorGymnastics', 'GolfSwing',
                           'HorseRiding', 'IceDancing', 'LongJump',
                           'PoleVault', 'RopeClimbing', 'SalsaSpin',
                           'SkateBoarding', 'Skiing', 'Skijet',
                           'SoccerJuggling', 'Surfing', 'TennisSwing',
                           'TrampolineJumping', 'VolleyballSpiking',
                           'WalkingWithDog']
        elif data_type == 'okutama':
            action_list = ['Calling', 'Carrying', 'Drinking', 'Hand Shaking',
                            'Hugging', 'Lying', 'Pushing/Pulling', 'Reading',
                            'Running', 'Sitting', 'Standing', 'Walking']
        else:
            raise Exception('ivalid action data_type:{}'.format(data_type))
            
        # TODO: 修正前と整合性を取るために-1,-2を定義しているが、-2はいらないかも。
        self._master = {idx: name for idx, name in enumerate(action_list)}
        self._master[-1] = 'NoAction'
        self._master[-2] = 'SomeOne'
        self._data_type = data_type

    def findByModelID(self, model_id):
        """
        モデルのIDから行動ラベルデータを取得

        Arguments:
            model_id: モデルが出力する行動ID(0オリジン)
        Rerurn:
            ActionMstオブジェクト
        """
        if model_id not in self._master:
            logger.warning('not found specified ID {} in master [data_type=={}]'.format(
                model_id, self._data_type))
            return 'NoAction'
        else:
            return self._master[model_id]

    def getNameMap(self):
        results = {}
        for model_id, name in self._master.items():
            results[name] = model_id
        return results

    def __dict__(self):
        return self._master

    def __len__(self):
        raise Exception('debug')
