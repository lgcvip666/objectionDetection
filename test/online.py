from __future__ import print_function
from myo.myo_raw import MyoRaw
import sys
import time
import uuid
import h5py
import numpy as np
import csv 
import os
import math
import threading

from sklearn.externals import joblib
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.model_selection import cross_val_score  
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier

#----------------------------------------------------------------------------------------------
#下载特征值极值，用于在线特征值归一化；
#下载训练好的模型
featureFolder = os.getcwd() + "\\DataSets\\" + \
				os.listdir(os.getcwd() + "\\DataSets")[len(os.listdir(os.getcwd() + "\\DataSets"))-1]#[]中表示找到DataSets下的最后一个文件夹
print('featureFolder-->'+str(featureFolder))
featureMax = np.loadtxt(featureFolder+'//featureMax.txt')
featureMin = np.loadtxt(featureFolder+'//featureMin.txt')
model_RF  = joblib.load("model//model_RF.m")
model_SVM = joblib.load("model//model_SVM.m")
model_KNN = joblib.load("model//model_KNN.m")
#----------------------------------------------------------------------------------------------
#全局变量以及特征函数
windowDataLength = 20 #时间窗，与训练模型时保持一致
slideDataLength  = 4  #滑动窗
emg_data  = []		  #存储 windowDataLength+slideDataLength 行肌电数据
stop_flag = 0
# 3个特征函数
def featureRMS(data):
    return np.sqrt(np.mean(data**2, axis=0))
def featureMAV(data):
    return np.mean(np.abs(data), axis=0) 
def featureWL(data):
    return np.sum(np.abs(np.diff(data, axis=0)),axis=0)/data.shape[0]

#----------------------------------------------------------------------------------------------
#肌电数据格式处理
def proc_emg(emg, moving):
	global emg_data
	timeStrick = time.time()	#time.time() 返回当前时间的时间戳
	emg = np.append(emg ,timeStrick)
	emg_data = np.append(emg_data, emg)

    
global SVM_prediction

SVM_prediction=np.array([4.])


#----------------------------------------------------------------------------------------------
#处理肌电信号
###  mMyo.hnd = EMGHandler(mMyo.m, mMyo.storedPath) #实例化对象mMyo.hnd
# self == mMyo.hnd
class EMGHandler(object):
	def __init__(self, m, storedPath):
		self.recording = -1
		self.dtype = np.int16
		self.m = m
		self.storedPath = storedPath
		self.rawLength = 0
	# def return_label(self):
		# return 
		# self.__call__.RF_prediction,\
		# self.__call__.SVM_prediction,\
		# self.__call__.KNN_prediction
		
	def __call__(self, emg, moving):
		self.emg = emg
		global RF_prediction,SVM_prediction,KNN_prediction
		global emg_data, featureMax, featureMin, windowDataLength, slideDataLength
		if self.recording >= 0:
			if len(emg_data) != 0:
				emg_data = emg_data.reshape((int(len(emg_data)/9),9))#int(len(emg_data)/9)行，9列
				self.rawLength = emg_data.shape[0]
			if self.rawLength >= windowDataLength+slideDataLength:
				#达到24行数据，提取后20行，提取特征值分类
				emg_data = emg_data[slideDataLength:windowDataLength+slideDataLength,:]
				feature = []
				for i in range(8):
					data = emg_data[:,i]
					############测试###################
					# print("emg_data[:,%i] " % i)
					# print("data is :",data)
					############测试###################
					RMS  = featureRMS(data)
					MAV  = featureMAV(data)
					WL   = featureWL(data)
					feature = np.append(feature, (RMS, MAV, WL))
					############测试###################
					# print("feature is :\t\n",feature)
					############测试###################
				feature = feature.reshape((1,24))
				# 归一化后进行预测
				feature = ((feature-featureMin)/(featureMax-featureMin))[0]
				############测试###################
				# print("feature is :\t\n",feature)
				#########测试###################
				for i in range(24):
					if(feature[i]>1):
						feature[i] = 1
					elif(feature[i]<0):
						feature[i] = 0
				feature = feature.reshape((1,24))
				#########测试###################
				# print("feature is :\t\n",feature)
				#########测试###################
				RF_prediction = model_RF.predict(feature)
				SVM_prediction = model_SVM.predict(feature)
				KNN_prediction = model_KNN.predict(feature)
				print('RF_prediction-->'+str(RF_prediction)+' , '+'SVM_prediction-->'+str(SVM_prediction)+' , '+'KNN_prediction-->'+str(KNN_prediction))
				feature = []#单次判断结束，置空，便于下次处理
				# return RF_prediction,SVM_prediction,KNN_prediction
		else:
			feature  = []
			emg_data = []

##mMyo = myMyo(storedPath='online\\')	#实例化 myMyo 类
class myMyo(object):
	# def __init__(self):
	def __init__(self, storedPath):
		# self.m =  MyoRaw(sys.argv[1] if len(sys.argv) >= 2 else None)
		self.m =  MyoRaw()
		print("1")
		#from myo.myo_raw import MyoRaw #实例化对象self.m 
		self.storedPath = storedPath
		self.hnd = EMGHandler(self.m, self.storedPath)#实例化对象self.hnd
###########################################################################
		# self.hnd.return_label()
###########################################################################
		print("2")
		self.m.add_emg_handler(self.hnd)#add_emg_handler 是MyoRaw类下的一个方法
		print("3")
		self.m.add_emg_handler(proc_emg)
	def start(self):
		self.hnd.recording = 1 #recording类属性，开始标志符为 1 
		print('recording flag --> ' + str(self.hnd.recording))
		self.m.connect()#connect 是MyoRaw类下的一个方法
	def run(self):
		self.m.run()
	def stop(self):
		self.hnd.recording = -1
		print('recording flag --> ' + str(self.hnd.recording))
		self.m.disconnect()

def waitForStop():
	time.sleep(10)
	stop_flag = 1 

if __name__ == '__main__':
    mMyo = myMyo(storedPath='online\\')	#实例化 myMyo 类
    threadWaitForStop = threading.Thread(target = waitForStop) #创建线程。
    threadWaitForStop.start()#方法threading.Thread.start():启动线程。

    mMyo.start()
    print("myo is runing.....")
    while (stop_flag == 0):
        mMyo.run()
    threadWaitForStop.join()#等待线程终止
    
    mMyo.stop()
    print('end')