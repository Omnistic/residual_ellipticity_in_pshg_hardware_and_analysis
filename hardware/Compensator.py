import CONFIG

from hardware.RotationStage import RotationStage


class Compensator:
    def __init__(self):
        self.hwp_rotation_stage = RotationStage('kdc101', CONFIG.hwp_kcube)
        self.qwp_rotation_stage = RotationStage('kdc101', CONFIG.qwp_kcube)
                
    def close(self):
        self.qwp_rotation_stage.close()
        self.hwp_rotation_stage.close()