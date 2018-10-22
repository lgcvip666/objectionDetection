#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from myo_raw import MyoRaw
import sys
import time
import uuid
import numpy as np
import csv 
import os


emgDataSize = 10
actionCategry = 0	#动作类别，由主函数传递过来，给数据加标签
emg_data  = []
# quat_data = []
# acc_data  = []
# gyr_data  = []

dataCounter = 0
displayLength = 10 #the length of data to display

'''
emg data process
'''
def proc_emg(emg, moving):
	global emg_data, actionCategry
	emg = np.append(emg ,actionCategry)
	# print(actionCategry)
	emg_data.append(emg)

# '''
# imu data process
# '''
# def proc_imu(quat, acc, gyr ):
# 	global acc_data , quat_data ,gyr_data

# 	timeStrick = time.time()

# 	quat = np.append(quat , timeStrick )
# 	acc = np.append(acc , timeStrick )
# 	gyr = np.append(gyr , timeStrick )

# 	quat_data.append( quat )
# 	acc_data.append(  acc  )
# 	gyr_data.append(  gyr  )

'''
creat emg files
'''
def createEmgFile(storedPath, data ): 
	fileName = storedPath + 'myo_emg.csv'
	fileExistFlag = os.path.isfile(fileName)

	with open(fileName ,'a+') as f:
		writer = csv.writer(f)
		if fileExistFlag == False:
			writer.writerow(["Channel 0","Channel 1",'Channel 2','Channel 3',
							'Channel 4','Channel 5','Channel 6','Channel 7','actionCategry'])
		writer.writerows(data)

# '''
# creat imu data
# '''
# def creatImuFile(storedPath, data  ,dataFlag = 'acc'):
# 	# - e.g. [storedPath]
# 	# - 'C:\\Users\\Administrator\\Desktop\\EMGSDK\\DataSets\\1526520649\\'
# 	fileName = storedPath + 'myo_' + dataFlag + '.csv'
# 	fileExistFlag = os.path.isfile(fileName)
# 	with open(fileName,'a+') as f:
# 		writer = csv.writer(f)
# 		if dataFlag == 'quat':
# 			if fileExistFlag == False:
# 				writer.writerow(['q1','q2','q3','q4','timeTicks'])
# 		elif dataFlag == 'acc':
# 			if fileExistFlag == False:
# 				writer.writerow(['ax','ay','az','timeTicks'])
# 		elif dataFlag == 'gyr':
# 			if fileExistFlag == False:
# 				writer.writerow(['gx','gy','gz','timeTicks'])
# 		writer.writerows(data)

class EMGHandler(object):
	
	def __init__(self, m, storedPath):
		self.recording = -1
		self.dtype = np.int16
		self.m = m
		self.storedPath = storedPath
		
	def __call__(self, emg, moving):
		self.emg = emg
	    # global emg_data , quat_data , acc_data ,gyr_data ,dataCounter ,displayLength
		global emg_data, dataCounter, displayLength
		if self.recording >= 0:
			if len(emg_data) >= emgDataSize:
				createEmgFile(self.storedPath, emg_data)
				# creatImuFile(self.storedPath, quat_data,'quat')
				# creatImuFile(self.storedPath, acc_data,'acc')
				# creatImuFile(self.storedPath, gyr_data,'gyr')
				# if dataCounter == 0:
				# 	pass
					# print("the length of unit data is :" + str(displayLength))
				if len(emg_data) == displayLength:
					dataCounter += 1
					print ('Saved Data -->>' + str(displayLength * dataCounter))
				emg_data = []
				# quat_data = []
				# acc_data = []
				# gyr_data = []
		else:
			dataCounter = 0
			emg_data = []
			# quat_data = []
			# acc_data = []
			# gyr_data = []


class myMyo(object):

	def __init__(self, storedPath):
		
		self.m =  MyoRaw(sys.argv[1] if len(sys.argv) >= 2 else None)
		self.storedPath = storedPath
		self.hnd = EMGHandler(self.m, self.storedPath)
		self.m.add_emg_handler(self.hnd)
		self.m.add_emg_handler(proc_emg)
		# self.m.add_imu_handler(proc_imu)

	def start(self):
		self.hnd.recording = 1
		print('recording flag --> ' + str(self.hnd.recording))
		self.m.connect()

	def run(self, ActionCategry):
		global actionCategry
		self.m.run()
		actionCategry = ActionCategry

	def stop(self):
		self.hnd.recording = -1
		print('recording flag --> ' + str(self.hnd.recording))
		self.m.disconnect()

	# def myoRun(self,sleepTime = 0.001):
	# 	print("myo is runing.....")
	# 	while True:
	# 		print("thread 2")
	# 		self.run()
	# 		time.sleep(sleepTime)

if __name__ == '__main__':
	pass
