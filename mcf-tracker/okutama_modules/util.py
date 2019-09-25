import json
import numpy as np

class JsonEncoder(json.JSONEncoder):
    """
    numpyでもJsonエンコードできるように
    """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super().default(obj)


def json_encode(obj, indent=None):
    """
    Numpy配列にも対応したjsonエンコーダー
    """
    return json.dumps(obj, indent=indent, cls=JsonEncoder, ensure_ascii=False)


def json_decode(jsonstr):
    return json.loads(jsonstr)
