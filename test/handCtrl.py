#coding:UTF-8


from __future__ import print_function
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2
# from whiteHand.mySerial import mySerial
from mySerial import mySerial

import time

'''
Pseudo - hand position and command class
'''
class myHandCtrl(object):

    def __init__(self):

        self.mSerial = mySerial()  #初始化串口

        '''----------------------------指令帧----------------------------------------------------------'''
        self.commandFramehHeader1 = "0xEB"     #帧头
        self.commandFramehHeader2 = "0x90"    #帧头
        self.commandHandId = "0x01"            #灵巧手的ID号（1-254）默认为1 ， 广播ID为255
        self.commandDataLength = "0x02"     #数据体的长度：数据体长度 + 校验和的长度
        self.commandData1 = ""                #数据体（指令号）1    
        self.commandData2 = ""                #数据体（指令号）2
        self.commandCheckSum = ""            #校验和
        '''----------------------------应答帧----------------------------------------------------------'''
        self.replyFramehHeader1 = "0xEE"     #帧头
        self.replyFramehHeader2 = "0x16"    #帧头
        self.replyHandId = "0x01"            #灵巧手的ID号（1-254）默认为1 ， 广播ID为255
        self.replyDataLength = "0x02"         #数据体的长度：数据体长度 + 校验和的长度
        self.replyCmdData = ""                #返回发送的命令号    
        self.replyData = ""                    #数据体
        self.replyCheckSum = ""                #校验和

        '''---------------------------指令类型-----------------------------------------------------------'''
        self.CMD_MC_SET_DRVALL_SEEKANGLE_GYH         = "0x54"                 #设置目标归一化角度
        self.CMD_MC_SET_DRVALL_SEEKPOS                 = "0x50"                #设置目标位置
        self.CMD_MC_SET_DRVALL_SPEED                 = "0x51"                #设置速度
        self.CMD_MC_SET_DRVALL_YBP_THRESHOLD         = "0x52"                #设置抓力阈值
        self.CMD_MC_READ_DRVALL_SEEKGYHANGLE        = "0xD7"                #读取目标归一化角度
        self.CMD_MC_READ_DRVALL_SEEKPOS             = "0xD0"                #读取目标位置
        self.CMD_MC_READ_DRVALL_CURANGLE_GYH         = "0xD9"                #读取当前归一化角度
        self.CMD_MC_READ_DRVALL_CURPOS                = "0xD1"                #读取当前位置
        self.CMD_MC_READ_DRVALL_SPEED                 = "0xD2"                #读取当前速度
        self.CMD_MC_READ_DRVALL_YBP_THRESHOLD         = "0xD3"                #读取抓力阈值
        self.CMD_MC_READ_DRVALL_YBP_RAWDATA            = "0xD4"                #读取传感器原始值
        self.CMD_MC_PARA_SAVE                        = "0x01"                #参数固化，掉电不丢失
        self.CMD_MC_PARA_ID_SET                     = "0x04"                #设置灵巧手ID号
        self.CMD_MC_MOVE_K_SET_CURPOS_IN_CMAP        = "0x05"                #保存当前手势到手势序列K中
        self.CMD_MC_MOVE_K_SHOW                     = "0x06"                #将手势序列K中的手势展示
        self.CMD_MC_MOVE_K_SHOW_ASDEFAULT            = "0x07"                #将当前手势保存为上电默认状态
    '''--------------------------------------------------------------------------------------------------------------'''
    '''
    功能：讲十进制数字转为十六进制，并拆为高位和低位
    参数：intNum：整型数据
    返回：高位和低位
    '''
    def intToHexStr(self , intNum):

        hexStr = hex(intNum)

        if intNum < 256:
            highStr = "0x00"
            lowStr  = "0x" + hexStr[2:]
        else:
            highStr = "0x0" + hexStr[2]
            lowStr  = "0x" + hexStr[3:5]
        return lowStr , highStr
    '''
    功能：将十六进制字符串形式转为整形
    参数：hexStr：十六进制字符串
    返回：整形
    '''
    def hexStrToInt(self , hexStr):

        return int(hexStr , 16)

    '''
    功能：控制灵巧手运动

    参数：movementType:运动类型 , 可以选用的参数为：{"setHandNormalizationAngle" , "setHandTargetPosition" ,"setHandTargetSpeed", 
                                                  "setHandForceThreshold"}
         parameterList:参数列表
    
    返回：命令

    注意：参数范围：{"setHandNormalizationAngle:0(握拳)-1000(伸掌)" , 
                    "setHandTargetPosition     ：0(握拳)-2000(伸掌)"          0xFFFF：不设置动作 ,
                    "setHandTargetSpeed"     ：0(慢速)-2000(快速)"          0xFFFF：不设置动作, 
                    "setHandForceThreshold"  ：100(小力)-1200(大力)"      0xFFFF：不设置动作    参数列表为5}
    '''
    def handMovementCtrol(self , movementType = "setHandNormalizationAngle"  , parameterList = [1000,1000,1000,1000,1000,1000]):
        tempCmdList = []
        self.commandDataLength = "0x0d"
        if movementType == "setHandNormalizationAngle":
            self.commandData1 = self.CMD_MC_SET_DRVALL_SEEKANGLE_GYH
        elif movementType == "setHandTargetPosition":
            self.commandData1 = self.CMD_MC_SET_DRVALL_SEEKPOS
        elif movementType == "setHandTargetSpeed":
            self.commandData1 = self.CMD_MC_SET_DRVALL_SPEED
        elif movementType == "setHandForceThreshold":
            self.commandData1 = self.CMD_MC_SET_DRVALL_YBP_THRESHOLD
            self.commandDataLength = "0x0b"
            handForceThresholdList = [600,600,600,600,600]

        tempCmdList.append((self.hexStrToInt(self.commandFramehHeader1)))
        tempCmdList.append((self.hexStrToInt(self.commandFramehHeader2)))
        tempCmdList.append((self.hexStrToInt(self.commandHandId)))
        tempCmdList.append((self.hexStrToInt(self.commandDataLength)))
        tempCmdList.append((self.hexStrToInt(self.commandData1)))
        for item in parameterList:
            lowStr , highStr = self.intToHexStr(item)
            tempCmdList.append((self.hexStrToInt(lowStr)))
            tempCmdList.append((self.hexStrToInt(highStr)))
        #求校验和
        tempSum = sum(tempCmdList) - self.hexStrToInt(self.commandFramehHeader1) - self.hexStrToInt(self.commandFramehHeader2)
        self.commandCheckSum , _ = self.intToHexStr(tempSum)
        tempCmdList.append((self.hexStrToInt(self.commandCheckSum)))
        self.mSerial.sendCmd(tempCmdList)
        
        if self.readCommandReturnValue() == True:
            print("Send command " + movementType + " succeed!!!!")
        else:
            print("Send command " + movementType + "  fail!!!!")
            self.mSerial.sendCmd(tempCmdList)

    '''
    功能：读取发送命令后的返回值
    参数：movementType:运动类型 , 可以选用的参数为：{"setHandNormalizationAngle" , "setHandTargetPosition" ,"setHandTargetSpeed", 
                                                    "setHandForceThreshold"}
    返回：无
    '''
    def readCommandReturnValue(self):

        recvCommandList = self.mSerial.recvCmd(cmdCount = 7)
        if recvCommandList[5] == 1:
            return True
        elif recvCommandList[5] == 85:
            return False

    '''
    功能：读取手的信息
    参数：handInfoType信息的类型，可以取：{"targetAngle", "targetPosition" , "currentSpeed" , "graspThreshold"
                                        "currentAngle" , "currentPosition" ,"sensorData" }
    返回：命令
    '''
    def readHandInfo(self , handInfoType = "targetAngle"):
        tempCmdList = []
        self.commandDataLength = "0x01"
        if handInfoType == "targetAngle":
            self.commandData1 = self.CMD_MC_READ_DRVALL_SEEKGYHANGLE
        elif handInfoType == "targetPosition":
            self.commandData1 = self.CMD_MC_READ_DRVALL_SEEKPOS
        elif handInfoType == "currentAngle":
            self.commandData1 = self.CMD_MC_READ_DRVALL_CURANGLE_GYH
        elif handInfoType == "currentPosition":
            self.commandData1 = self.CMD_MC_READ_DRVALL_CURPOS
        elif handInfoType == "currentSpeed":
            self.commandData1 = self.CMD_MC_READ_DRVALL_SPEED
        elif handInfoType == "graspThreshold":
            self.commandData1 = self.CMD_MC_READ_DRVALL_YBP_THRESHOLD
        elif handInfoType == "sensorData":
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
        self.mSerial.sendCmd(tempCmdList)
        print(handInfoType +  ":" + str(self.readHandInfoReturnValue(handInfoType = handInfoType)))
    '''
    功能：读取手指的信息
    handInfoType信息的类型，可以取：{"targetAngle", "targetPosition" , "currentSpeed" , "graspThreshold"
                                            "currentAngle" , "currentPosition" ,"sensorData" }
    返回：各个手指的信息
    '''
    def readHandInfoReturnValue(self , handInfoType = "targetAngle"):
        if handInfoType in ["graspThreshold" , "sensorData"]:
            recvCommandList = self.mSerial.recvCmd(cmdCount = 16)
            recvDataList = recvCommandList[5:15]
            finger1 = int(("0x" + hex(recvDataList[1])[2:4] + hex(recvDataList[0])[2:4]) , 16)
            finger2 = int(("0x" + hex(recvDataList[3])[2:4] + hex(recvDataList[2])[2:4]) , 16)
            finger3 = int(("0x" + hex(recvDataList[5])[2:4] + hex(recvDataList[4])[2:4]) , 16)
            finger4 = int(("0x" + hex(recvDataList[7])[2:4] + hex(recvDataList[6])[2:4]) , 16)
            finger5 = int(("0x" + hex(recvDataList[9])[2:4] + hex(recvDataList[8])[2:4]) , 16)

            return finger1 , finger2 , finger3 , finger4 , finger5
        else:
            recvCommandList = self.handCtrol.recvCmd(cmdCount = 18)
            recvDataList = recvCommandList[5:17]
            finger1 = int(("0x" + hex(recvDataList[1])[2:4] + hex(recvDataList[0])[2:4]) , 16)
            finger2 = int(("0x" + hex(recvDataList[3])[2:4] + hex(recvDataList[2])[2:4]) , 16)
            finger3 = int(("0x" + hex(recvDataList[5])[2:4] + hex(recvDataList[4])[2:4]) , 16)
            finger4 = int(("0x" + hex(recvDataList[7])[2:4] + hex(recvDataList[6])[2:4]) , 16)
            finger5 = int(("0x" + hex(recvDataList[9])[2:4] + hex(recvDataList[8])[2:4]) , 16)
            finger55 = int(("0x" + hex(recvDataList[11])[2:4] + hex(recvDataList[10])[2:4]) , 16)
            return finger1 , finger2 , finger3 , finger4 , finger5 , finger55

    """
    功能：配置灵巧手
    参数：configureParameterType:配置参数类型 ， 可以选择：{"setHandId" , "saveSequenceOfGestures" , "displaySequenceOfGestures"}
    说明：{"setHandId"---->handId(1-254)
         "saveSequenceOfGestures"---->actionSequenceNumber(14-44，共 31 个序列号)
         "displaySequenceOfGestures"----->displayActionSequenceNumber(0-44，共 45 个序列号，其中 0-13 为固定动作，14-44 位用户编程动作)}
    返回：命令
    """
    def configureHand(self , configureParameterType = "setHandId" , handId = "0x04" , actionSequenceNumber = "0x0f" , displayActionSequenceNumber = "0x0a" ):

        tempCmdList = []
        self.commandDataLength = "0x02"
        if configureParameterType == "setHandId":
            self.commandData1 = self.CMD_MC_PARA_ID_SET
            self.commandData2 = handId
        elif configureParameterType == "saveSequenceOfGestures":
            self.commandData1 = self.CMD_MC_MOVE_K_SET_CURPOS_IN_CMAP
            self.commandData2 = actionSequenceNumber
        elif configureParameterType == "displaySequenceOfGestures":
            self.commandData1 = self.CMD_MC_MOVE_K_SHOW
            self.commandData2 = displayActionSequenceNumber

        tempCmdList.append((self.hexStrToInt(self.commandFramehHeader1)))
        tempCmdList.append((self.hexStrToInt(self.commandFramehHeader2)))
        tempCmdList.append((self.hexStrToInt(self.commandHandId)))
        tempCmdList.append((self.hexStrToInt(self.commandDataLength)))
        tempCmdList.append((self.hexStrToInt(self.commandData1)))
        tempCmdList.append((self.hexStrToInt(self.commandData2)))
        #求校验和
        tempSum = sum(tempCmdList) - self.hexStrToInt(self.commandFramehHeader1) - self.hexStrToInt(self.commandFramehHeader2)
        self.commandCheckSum , _ = self.intToHexStr(tempSum)
        tempCmdList.append((self.hexStrToInt(self.commandCheckSum)))
        self.mSerial.sendCmd(tempCmdList)
        if self.readCommandReturnValue() == True:
            print("Send command " + configureParameterType + " succeed!!!!")
        else:
            print("Send command " + configureParameterType + "  fail!!!!")
            self.mSerial.sendCmd(tempCmdList)
    '''
    功能：关于手部一些设置
    参数：setParameterType可以设置的参数类型,可以取：{"parameterCuring" , "setDefaultAction"}
    返回：命令
    '''
    def setHandInfo(self , setParameterType = "parameterCuring"):
        tempCmdList = []
        self.commandDataLength = "0x01"
        if setParameterType == "parameterCuring":
            self.commandData1 = self.CMD_MC_PARA_SAVE
        elif setParameterType == "setDefaultAction":
            self.commandData1 = self.CMD_MC_MOVE_K_SHOW_ASDEFAULT
        tempCmdList.append((self.hexStrToInt(self.commandFramehHeader1)))
        tempCmdList.append((self.hexStrToInt(self.commandFramehHeader2)))
        tempCmdList.append((self.hexStrToInt(self.commandHandId)))
        tempCmdList.append((self.hexStrToInt(self.commandDataLength)))
        tempCmdList.append((self.hexStrToInt(self.commandData1)))
        #求校验和
        tempSum = sum(tempCmdList) - self.hexStrToInt(self.commandFramehHeader1) - self.hexStrToInt(self.commandFramehHeader2)
        self.commandCheckSum , _ = self.intToHexStr(tempSum)
        tempCmdList.append((self.hexStrToInt(self.commandCheckSum)))
        self.mSerial.sendCmd(tempCmdList)
        if self.readCommandReturnValue() == True:
            print("Send command " + setParameterType + " succeed!!!!")
        else:
            print("Send command " + setParameterType + "  fail!!!!")
            self.mSerial.sendCmd(tempCmdList)



    """
    视频线程
    """
    def video(self):
        # global c
        c = True
        status = 10  # 等待拍照的时间
        """loop over the frames from the video stream"""
        ap = argparse.ArgumentParser()
        ap.add_argument("-p", "--prototxt", required=True,
                        help="path to Caffe 'deploy' prototxt file")
        ap.add_argument("-m", "--model", required=True,
                        help="path to Caffe pre-trained model")
        ap.add_argument("-c", "--confidence", type=float, default=0.2,
                        help="minimum probability to filter weak detections")
        args = vars(ap.parse_args())


        CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
                   "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                   "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                   "sofa", "train", "tvmonitor"]
        COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))


        """load our serialized model from disk"""
        print("[INFO] loading model...")
        net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
        """
        # initialize the video stream, allow the cammera sensor to warmup,
        # and initialize the FPS counter
        """
        print("[INFO] starting video stream...")
        vs = VideoStream(src=0).start()
        time.sleep(2.0)
        fps = FPS().start()
        while True:
            print("运行线程VIDEO")
            print("start video")
            """grab the frame from the threaded video stream and resize it"""
            """to have a maximum width of 800 pixels"""
            frame = vs.read()
            # # 下 1 行
            # # ret, frame = cap.read()
            print(type(frame))
            """
            图像无法加载，imread 返回None。
            传递None到imshow，导致其试图创建大小为0x0，这一失败的窗口。
            """
            while frame is None:
                print("waiting...")
                if frame is not None:
                    break
            # if frame is None:
                # print("waiting...")
                # time.sleep(0.1)
            # elif frame is not None:
            # print(type(frame))
            frame = imutils.resize(frame, width=800)
            # print("1")
            cv2.imshow("Frame", frame)
            """grab the frame dimensions and convert it to a blob"""
            (h, w) = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(cv2.resize(
                frame, (300, 300)), 0.007843, (300, 300), 127.5)

            # pass the blob through the network and obtain the detections and
            # predictions
            net.setInput(blob)
            detections = net.forward()

            # np.arange(0,3)
            # array([0, 1, 2])
            # loop over the detections
            idx_list = []  # 创建空列表 ,不能放在循环里，不然每次循环都会把列表清空。
            # print("2")
            for i in np.arange(0, detections.shape[2]):
                # print("np.arange(0, detections.shape[2]):",np.arange(0, detections.shape[2]))
                # print("检测到的物体种类总共有：",detections.shape[2])
                # extract the confidence (i.e., probability) associated with the prediction
                confidence = detections[0, 0, i, 2]  # 计算检测到的物体的置信率
                # print("confidence：",confidence)

                # filter out weak detections by ensuring the `confidence` is
                # greater than the minimum confidence
                if confidence > args["confidence"]:  # 置信率太低的不输出
                    # extract the index of the class label from the
                    # `detections`, then compute the (x, y)-coordinates of
                    # the bounding box for the object
                    idx = int(detections[0, 0, i, 1])  # 标签所在 CLASSES 中的索引位置
                    # print("idx:",idx)
                    # print("CLASSES[idx]:",CLASSES[idx])

                    idx_list.append(idx)
                    # print("idx_list",idx_list)

                    idx_list_new = []  # 创建空列表 ,不能放在循环里，不然每次循环都会把列表清空。
                    for num in idx_list[-(detections.shape[2]):]:  # 取后N个append的标签
                        # print("num:",num)
                        idx_list_new.append(num)
                        # print("idx_list_new:",idx_list_new)

                    global list
                    list = []  # 创建空列表 ,不能放在循环里，不然每次循环都会把列表清空。
                    for idx in idx_list_new:
                        list.append([CLASSES[idx]])
                    # print("检测到的物体分别是：",list)

                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    # print("box:",box)
                    (startX, startY, endX, endY) = box.astype("int")
                    # draw the prediction on the frame
                    label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
                    cv2.rectangle(frame, (startX, startY),
                                  (endX, endY), COLORS[idx], 2)
                    y = startY - 15 if startY - 15 > 15 else startY + 15
                    cv2.putText(frame, label, (startX, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

            print("检测到的物体种类总共有：", detections.shape[2])
            print("检测到的物体分别是：", sum(list, []))  # sum(list,[]) 把嵌套的list转成一个一维的list
            # show the output frame
            cv2.imshow("Frame", frame)
            # time.sleep(5)
            """下面的objectChoose()程序在while循环里只执行一次"""
            ########################################################################
            if status != 0:
                print("status-else", status)
                status -= 1
            elif status == 0 and c == True:
                c = False
                # print("status-if", status)
                self.objectChoose(list)
                #objectChoose(list, flag = 0, tmp=tmp)
            # print("status", status)
            ########################################################################

            # 肌电信号控制抓取物体和松开物体
            if online.SVM_prediction.tolist()[0] == 2.0:#握拳，抓取物体。
                self.handMovementCtrol(movementType = "setHandNormalizationAngle"  , parameterList = [0,0,0,0,0,0]) 
                print("正在给串口发送指令，并抓取物体")
            if online.SVM_prediction.tolist()[0] == 3.0:#张手，松开物体。
                self.handMovementCtrol(movementType = "setHandNormalizationAngle"  , parameterList = [1000,1000,1000,1000,1000,1000])  
                print("正在给串口发送指令，并松开物体")
            ########################################################################
            key = cv2.waitKey(1) & 0xFF
            """if the `q` key was pressed, break from the loop"""
            if key == ord("q"):
                break
            """update the FPS counter"""
            fps.update()


if __name__ == '__main__':

    mHandCtrl = myHandCtrl()
    # mHandCtrl.handMovementCtrol(movementType = "setHandNormalizationAngle"  , parameterList = [400,200,300,400,500,600]) 
    mHandCtrl.handMovementCtrol(movementType = "setHandNormalizationAngle"  , parameterList = [400,400,400,400,400,400]) 
    time.sleep(2)
    mHandCtrl.handMovementCtrol(movementType = "setHandNormalizationAngle"  , parameterList = [1000,1000,1000,1000,1000,1000]) 
    # mHandCtrl.readHandInfo(handInfoType = "sensorData")
    mHandCtrl.configureHand(configureParameterType = "displaySequenceOfGestures")