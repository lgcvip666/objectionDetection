import os
import sys
currentPath = os.getcwd()
if not currentPath+'\\myo' in sys.path:
	sys.path.append(currentPath+'\\myo')

from myoDataAcquire import myMyo