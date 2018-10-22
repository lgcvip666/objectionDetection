#coding:UTF-8


from __future__ import print_function

'''
Pseudo - hand position and command class
'''
class myHandPosition(object):

	def __init__(self):

		'''----------------------------指令帧----------------------------------------------------------'''
		self.commandFramehHeader1 = "0xEB" 	#帧头
		self.commandFramehHeader2 = "0x90"	#帧头
		self.commandHandId = "0x01"			#灵巧手的ID号（1-254）默认为1 ， 广播ID为255
		self.commandDataLength = "0x02" 	#数据体的长度：数据体长度 + 校验和的长度
		self.commandData1 = ""				#数据体（指令号）1	
		self.commandData2 = ""				#数据体（指令号）2
		self.commandCheckSum = ""			#校验和
		'''----------------------------应答帧----------------------------------------------------------'''
		self.replyFramehHeader1 = "0xEE" 	#帧头
		self.replyFramehHeader2 = "0x16"	#帧头
		self.replyHandId = "0x01"			#灵巧手的ID号（1-254）默认为1 ， 广播ID为255
		self.replyDataLength = "0x02" 		#数据体的长度：数据体长度 + 校验和的长度
		self.replyCmdData = ""				#返回发送的命令号	
		self.replyData = ""					#数据体
		self.replyCheckSum = ""				#校验和

		'''---------------------------指令类型-----------------------------------------------------------'''
		self.CMD_MC_SET_DRVALL_SEEKANGLE_GYH 		= "0x54" 				#设置目标归一化角度
		self.CMD_MC_SET_DRVALL_SEEKPOS 				= "0x50"				#设置目标位置
		self.CMD_MC_SET_DRVALL_SPEED 				= "0x51"				#设置速度
		self.CMD_MC_SET_DRVALL_YBP_THRESHOLD 		= "0x52"				#设置抓力阈值
		self.CMD_MC_READ_DRVALL_SEEKGYHANGLE		= "0xD7"				#读取目标归一化角度
		self.CMD_MC_READ_DRVALL_SEEKPOS 			= "0xD0"				#读取目标位置
		self.CMD_MC_READ_DRVALL_CURANGLE_GYH 		= "0xD9"				#读取当前归一化角度
		self.CMD_MC_READ_DRVALL_CURPOS				= "0xD1"				#读取当前位置
		self.CMD_MC_READ_DRVALL_SPEED 				= "0xD2"				#读取当前速度
		self.CMD_MC_READ_DRVALL_YBP_THRESHOLD 		= "0xD3"				#读取抓力阈值
		self.CMD_MC_READ_DRVALL_YBP_RAWDATA			= "0xD4"				#读取传感器原始值
		self.CMD_MC_PARA_SAVE						= "0x01"				#参数固化，掉电不丢失
		self.CMD_MC_PARA_ID_SET 					= "0x04"				#设置灵巧手ID号
		self.CMD_MC_MOVE_K_SET_CURPOS_IN_CMAP		= "0x05"				#保存当前手势到手势序列K中
		self.CMD_MC_MOVE_K_SHOW 					= "0x06"				#将手势序列K中的手势展示
		self.CMD_MC_MOVE_K_SHOW_ASDEFAULT			= "0x07"				#将当前手势保存为上电默认状态


	def intToHexStr(self , intNum):

		hexStr = hex(intNum)

		if intNum < 256:
			highStr = "0x00"
			lowStr  = "0x" + hexStr[2:]
		else:
			highStr = "0x0" + hexStr[2]
			lowStr  = "0x" + hexStr[3:5]
		return lowStr , highStr

	def hexStrToInt(self , hexStr):

		return int(hexStr , 16)

	'''
	功能：主控单元设置灵巧手中 6 个自由度的关节角度，已经进行了归一化处理，数据
	范围从 0 到 1000,0 为握拳状态下各自由度能达到的极限角度，1000 为五指伸开状态下各自
	由度能达到的极限角度。通过设置各个自由度的角度值可使灵巧手完成相应的手势动作。
	灵巧手中的 6 个直线伺服驱动器的 ID 号为 1-6，每个驱动器都负责一个关节角度的控制，
	其中小拇指的 ID 为 1、无名指的 ID 为 2、中指的 ID 为 3、食指的 ID 为 4、大拇指弯曲指
	关节 ID 为 5、大拇指旋转指关节 ID 为 6。
	数据内容：6 个自由度的角度数据，每个角度数据为 2Bytes（小端模式低字节先发送），
	共 12Bytes，角度的数据范围是从 0 到 1000，若为 0xFFFF，则表示不需要设置该驱动器的
	目标角度，因此可单独设置某个驱动器的目标角度。
	'''
	def setHandNormalizationAngle(self , handAngleList = [1000,1000,1000,1000,1000,1000]):

		tempCmdList = []
		self.commandDataLength = "0x0d"
		self.commandData1 = self.CMD_MC_SET_DRVALL_SEEKANGLE_GYH
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader1)))
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader2)))
		tempCmdList.append((self.hexStrToInt(self.commandHandId)))
		tempCmdList.append((self.hexStrToInt(self.commandDataLength)))
		tempCmdList.append((self.hexStrToInt(self.commandData1)))
		for item in handAngleList:
			lowStr , highStr = self.intToHexStr(item)
			tempCmdList.append((self.hexStrToInt(lowStr)))
			tempCmdList.append((self.hexStrToInt(highStr)))
		#求校验和
		tempSum = sum(tempCmdList) - self.hexStrToInt(self.commandFramehHeader1) - self.hexStrToInt(self.commandFramehHeader2)
		self.commandCheckSum , _ = self.intToHexStr(tempSum)
		tempCmdList.append((self.hexStrToInt(self.commandCheckSum)))
		return tempCmdList


	'''
	功能：主控单元设置灵巧手中 6 个直线驱动器的目标位置，使灵巧手完成相应的手势
	动作。灵巧手中的 6 个直线伺服驱动器的 ID 号为 1-6，其中小拇指的 ID 为 1、无名指的 ID
	为 2、中指的 ID 为 3、食指的 ID 为 4、大拇指弯曲指关节 ID 为 5、大拇指旋转指关节 ID
	为 6。
	数据内容：6 个驱动器的目标位置，每个位置为 2Bytes（小端模式低字节先发送），共12Bytes，
	目标位置的有效值为 0~2000，若为 0xFFFF，则表示不需要设置该驱动器的目标
	位置，因此可单独设置某个驱动器的目标位置。
	'''
	def setHandTargetPosition(self , handPositionList = [1000,1000,1000,1000,1000,1000]):

		tempCmdList = []
		self.commandDataLength = "0x0d"
		self.commandData1 = self.CMD_MC_SET_DRVALL_SEEKPOS
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader1)))
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader2)))
		tempCmdList.append((self.hexStrToInt(self.commandHandId)))
		tempCmdList.append((self.hexStrToInt(self.commandDataLength)))
		tempCmdList.append((self.hexStrToInt(self.commandData1)))
		for item in handPositionList:
			lowStr , highStr = self.intToHexStr(item)
			tempCmdList.append((self.hexStrToInt(lowStr)))
			tempCmdList.append((self.hexStrToInt(highStr)))
		#求校验和
		tempSum = sum(tempCmdList) - self.hexStrToInt(self.commandFramehHeader1) - self.hexStrToInt(self.commandFramehHeader2)
		self.commandCheckSum , _ = self.intToHexStr(tempSum)
		tempCmdList.append((self.hexStrToInt(self.commandCheckSum)))
		return tempCmdList

	'''
	功能：主控单元设置灵巧手中 6 个直线驱动器的运动速度。
	数据内容：6 个驱动器的速度，每个速度为 2Bytes（小端模式低字节先发送），共
	12Bytes，速度的有效值为 0~2000，若为 0xFFFF，则表示不需要设置该驱动器的速度，因
	此可单独设置某个驱动器的速度值。
	'''
	def setHandTargetSpeed(self , handSpeedList = [1000,1000,1000,1000,1000,1000]):

		tempCmdList = []
		self.commandDataLength = "0x0d"
		self.commandData1 = self.CMD_MC_SET_DRVALL_SPEED 
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader1)))
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader2)))
		tempCmdList.append((self.hexStrToInt(self.commandHandId)))
		tempCmdList.append((self.hexStrToInt(self.commandDataLength)))
		tempCmdList.append((self.hexStrToInt(self.commandData1)))
		for item in handSpeedList:
			lowStr , highStr = self.intToHexStr(item)
			tempCmdList.append((self.hexStrToInt(lowStr)))
			tempCmdList.append((self.hexStrToInt(highStr)))
		#求校验和
		tempSum = sum(tempCmdList) - self.hexStrToInt(self.commandFramehHeader1) - self.hexStrToInt(self.commandFramehHeader2)
		self.commandCheckSum , _ = self.intToHexStr(tempSum)
		tempCmdList.append((self.hexStrToInt(self.commandCheckSum)))
		return tempCmdList

	'''
	功能：主控单元设置灵巧手 5 根手指的指尖抓力阈值。
	数据内容：5 根手指的指尖抓力阈值（从小指依次到大拇指的顺序，以克为单位），每
	个阈值为 2Bytes（小端模式低字节先发送），共 10Bytes，阈值的有效值为 100~1200，若为
	0xFFFF，则表示不需要设置该手指的阈值，因此可单独设置某根手指的指尖阈值。
	'''
	def setHandForceThreshold(self , handForceThresholdList = [600,600,600,600,600]):

		tempCmdList = []
		self.commandDataLength = "0x0b"
		self.commandData1 = self.CMD_MC_SET_DRVALL_YBP_THRESHOLD 

		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader1)))
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader2)))
		tempCmdList.append((self.hexStrToInt(self.commandHandId)))
		tempCmdList.append((self.hexStrToInt(self.commandDataLength)))
		tempCmdList.append((self.hexStrToInt(self.commandData1)))
		for item in handSpeedList:
			lowStr , highStr = self.intToHexStr(item)
			tempCmdList.append((self.hexStrToInt(lowStr)))
			tempCmdList.append((self.hexStrToInt(highStr)))
		#求校验和
		tempSum = sum(tempCmdList) - self.hexStrToInt(self.commandFramehHeader1) - self.hexStrToInt(self.commandFramehHeader2)
		self.commandCheckSum , _ = self.intToHexStr(tempSum)
		tempCmdList.append((self.hexStrToInt(self.commandCheckSum)))
		return tempCmdList

	'''
	功能：主控单元读取灵巧手当前 6 个驱动器的目标角度
	数据内容：无。
	'''
	def readTargetNormalizationAngle(self):

		tempCmdList = []
		self.commandDataLength = "0x01"
		self.commandData1 = self.CMD_MC_READ_DRVALL_SEEKGYHANGLE 
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader1)))
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader2)))
		tempCmdList.append((self.hexStrToInt(self.commandHandId)))
		tempCmdList.append((self.hexStrToInt(self.commandDataLength)))
		tempCmdList.append((self.hexStrToInt(self.commandData1)))
		#求校验和
		tempSum = sum(tempCmdList) - self.hexStrToInt(self.commandFramehHeader1) - self.hexStrToInt(self.commandFramehHeader2)
		self.commandCheckSum , _ = self.intToHexStr(tempSum)
		tempCmdList.append((self.hexStrToInt(self.commandCheckSum)))
		return tempCmdList
	'''
	功能：主控单元读取灵巧手当前 6 个驱动器的目标位置
	数据内容：无。
	'''
	def readTargetPosition(self):

		tempCmdList = []
		self.commandDataLength = "0x01"
		self.commandData1 = self.CMD_MC_READ_DRVALL_SEEKPOS 
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader1)))
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader2)))
		tempCmdList.append((self.hexStrToInt(self.commandHandId)))
		tempCmdList.append((self.hexStrToInt(self.commandDataLength)))
		tempCmdList.append((self.hexStrToInt(self.commandData1)))
		#求校验和
		tempSum = sum(tempCmdList) - self.hexStrToInt(self.commandFramehHeader1) - self.hexStrToInt(self.commandFramehHeader2)
		self.commandCheckSum , _ = self.intToHexStr(tempSum)
		tempCmdList.append((self.hexStrToInt(self.commandCheckSum)))
		return tempCmdList
	'''
	功能：主控单元读取灵巧手当前 6 个驱动器的当前角度
	数据内容：无。
	'''
	def ReadCurrentNormalizationAngle(self):

		tempCmdList = []
		self.commandDataLength = "0x01"
		self.commandData1 = self.CMD_MC_READ_DRVALL_CURANGLE_GYH 
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader1)))
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader2)))
		tempCmdList.append((self.hexStrToInt(self.commandHandId)))
		tempCmdList.append((self.hexStrToInt(self.commandDataLength)))
		tempCmdList.append((self.hexStrToInt(self.commandData1)))
		#求校验和
		tempSum = sum(tempCmdList) - self.hexStrToInt(self.commandFramehHeader1) - self.hexStrToInt(self.commandFramehHeader2)
		self.commandCheckSum , _ = self.intToHexStr(tempSum)
		tempCmdList.append((self.hexStrToInt(self.commandCheckSum)))
		return tempCmdList

	'''
	功能：主控单元读取灵巧手当前 6 个驱动器的当前位置
	数据内容：无。
	'''
	def ReadCurrentPosition(self):

		tempCmdList = []
		self.commandDataLength = "0x01"
		self.commandData1 = self.CMD_MC_READ_DRVALL_CURPOS 
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader1)))
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader2)))
		tempCmdList.append((self.hexStrToInt(self.commandHandId)))
		tempCmdList.append((self.hexStrToInt(self.commandDataLength)))
		tempCmdList.append((self.hexStrToInt(self.commandData1)))
		#求校验和
		tempSum = sum(tempCmdList) - self.hexStrToInt(self.commandFramehHeader1) - self.hexStrToInt(self.commandFramehHeader2)
		self.commandCheckSum , _ = self.intToHexStr(tempSum)
		tempCmdList.append((self.hexStrToInt(self.commandCheckSum)))
		return tempCmdList

	'''
	功能：主控单元读取灵巧手当前 6 个驱动器的当前位置
	数据内容：无。
	'''
	def ReadCurrentSpeed(self):

		tempCmdList = []
		self.commandDataLength = "0x01"
		self.commandData1 = self.CMD_MC_READ_DRVALL_SPEED
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader1)))
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader2)))
		tempCmdList.append((self.hexStrToInt(self.commandHandId)))
		tempCmdList.append((self.hexStrToInt(self.commandDataLength)))
		tempCmdList.append((self.hexStrToInt(self.commandData1)))
		#求校验和
		tempSum = sum(tempCmdList) - self.hexStrToInt(self.commandFramehHeader1) - self.hexStrToInt(self.commandFramehHeader2)
		self.commandCheckSum , _ = self.intToHexStr(tempSum)
		tempCmdList.append((self.hexStrToInt(self.commandCheckSum)))
		return tempCmdList

	'''
	功能：主控单元读取灵巧手当前 6 个驱动器的当前位置
	数据内容：无。
	'''
	def ReadGraspThreshold(self):

		tempCmdList = []
		self.commandDataLength = "0x01"
		self.commandData1 = self.CMD_MC_READ_DRVALL_YBP_THRESHOLD
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader1)))
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader2)))
		tempCmdList.append((self.hexStrToInt(self.commandHandId)))
		tempCmdList.append((self.hexStrToInt(self.commandDataLength)))
		tempCmdList.append((self.hexStrToInt(self.commandData1)))
		#求校验和
		tempSum = sum(tempCmdList) - self.hexStrToInt(self.commandFramehHeader1) - self.hexStrToInt(self.commandFramehHeader2)
		self.commandCheckSum , _ = self.intToHexStr(tempSum)
		tempCmdList.append((self.hexStrToInt(self.commandCheckSum)))
		return tempCmdList

	'''
	功能：主控单元读取灵巧手当前 6 个驱动器的当前位置
	数据内容：无。
	'''
	def ReadRawSensorData(self):

		tempCmdList = []
		self.commandDataLength = "0x01"
		self.commandData1 = self.CMD_MC_READ_DRVALL_YBP_RAWDATA
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader1)))
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader2)))
		tempCmdList.append((self.hexStrToInt(self.commandHandId)))
		tempCmdList.append((self.hexStrToInt(self.commandDataLength)))
		tempCmdList.append((self.hexStrToInt(self.commandData1)))
		#求校验和
		tempSum = sum(tempCmdList) - self.hexStrToInt(self.commandFramehHeader1) - self.hexStrToInt(self.commandFramehHeader2)
		self.commandCheckSum , _ = self.intToHexStr(tempSum)
		tempCmdList.append((self.hexStrToInt(self.commandCheckSum)))
		return tempCmdList

	'''
	功能：主控单元将灵巧手当前的速度和抓力阈值以及手势动作等参数固化到内部闪
	存，掉电不丢失
	数据内容：无。
	'''
	def setParameterCuring(self):

		tempCmdList = []
		self.commandDataLength = "0x01"
		self.commandData1 = self.CMD_MC_PARA_SAVE
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader1)))
		tempCmdList.append((self.hexStrToInt(self.commandFramehHeader2)))
		tempCmdList.append((self.hexStrToInt(self.commandHandId)))
		tempCmdList.append((self.hexStrToInt(self.commandDataLength)))
		tempCmdList.append((self.hexStrToInt(self.commandData1)))
		#求校验和
		tempSum = sum(tempCmdList) - self.hexStrToInt(self.commandFramehHeader1) - self.hexStrToInt(self.commandFramehHeader2)
		self.commandCheckSum , _ = self.intToHexStr(tempSum)
		tempCmdList.append((self.hexStrToInt(self.commandCheckSum)))
		return tempCmdList


if __name__ == '__main__':

	mHandPosition = myHandPosition()
	print(mHandPosition.setHandNormalizationAngle(handAngleList = [100 , 200 , 300 , 400 , 500 , 600])) 

