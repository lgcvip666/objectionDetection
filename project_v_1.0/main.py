from handCtrl import myHandCtrl
import time
mHandCtrl = myHandCtrl()
mHandCtrl.handMovementCtrol(movementType = "setHandNormalizationAngle"  , parameterList = [400,400,400,400,400,400]) 
time.sleep(1)
mHandCtrl.handMovementCtrol(movementType = "setHandNormalizationAngle"  , parameterList = [1000,1000,1000,1000,1000,1000])