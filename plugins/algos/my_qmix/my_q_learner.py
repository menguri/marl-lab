# plugins/algos/my_qmix/my_q_learner.py
from learners.q_learner import QLearner as _BaseQLearner
from modules.mixers.qmix import QMixer
from modules.mixers.vdn import VDNMixer
from modules.mixers.qtran import QTranBase

# 사용자 정의 믹서 임포트
from plugins.algos.my_qmix.mixer import MyMixer

class PatchedQLearner(_BaseQLearner):
    def _build_mixer(self):
        key = getattr(self.args, "mixer", None)
        if key == "qmix":        return QMixer(self.args)
        if key == "vdn":         return VDNMixer(self.args)
        if key == "qtran_base" and QTranBase: return QTranBase(self.args)
        if key == "my_mixer":    return MyMixer(self.args)
        return super()._build_mixer()  # 안전한 폴백