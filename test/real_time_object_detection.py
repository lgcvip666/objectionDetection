#############################################################
#
#                   物体检测+肌电抓取
#
#############################################################

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2
#############################################################
from online import myMyo, waitForStop, EMGHandler
import threading
from threading import Thread
import online
import sys
import traceback
from handCtrl import myHandCtrl
#############################################################


# 2.0：张手 1.0：握拳
def objectChoose(list,flag = 0):
    print("进入物体选择程序")
    while True:
        a = online.SVM_prediction.tolist()[0]
        b = 0
        print("未进入选择，SVM_prediction:",a)
        if a == 2.0 : #张手
            print(list[flag]) #框选物体
            b = online.SVM_prediction.tolist()[0]
            print("进入选择 ,SVM_prediction:",b)
            time.sleep(2)
            if b == 2.0 :  #握手预备动作；
                mHandCtrl.handMovementCtrol(movementType = "setHandNormalizationAngle"  , parameterList = [400,400,400,400,400,400]) 
                print("已通过串口发送指令给假肢手，并对 %s做预备动作" % list[flag])
                break
            if b == 2.0 : #张手
                flag += 1
            if flag == len(list):
                flag = 0



"""
肌电线程
"""
def runMyo():
    while True:
        print("运行线程MYO")
        mMyo.run()


"""
视频线程
"""
def video():
    # global c
    c = True
    status = 10  # 等待拍照的时间
    """loop over the frames from the video stream"""
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
            print("status-if", status)
            objectChoose(list)
        print("status", status)
        ########################################################################
        # 肌电信号控制抓取物体和松开物体
        if online.SVM_prediction.tolist()[0] == 2.0:#握拳，抓取物体。
            mHandCtrl.handMovementCtrol(movementType = "setHandNormalizationAngle"  , parameterList = [200,200,200,200,200,200]) 
            # mHandCtrl.handMovementCtrol(movementType = "setHandNormalizationAngle"  , parameterList = [1000,1000,1000,1000,1000,1000]) 
            print("正在给串口发送指令，并抓取物体")
        if online.SVM_prediction.tolist()[0] == 3.0:#张手，松开物体。
            mHandCtrl.handMovementCtrol(movementType = "setHandNormalizationAngle"  , parameterList = [1000,1000,1000,1000,1000,1000])  
            print("正在给串口发送指令，并松开物体")
        ########################################################################
        key = cv2.waitKey(1) & 0xFF
        """if the `q` key was pressed, break from the loop"""
        if key == ord("q"):
            break
        """update the FPS counter"""
        fps.update()





""" construct the argument parse and parse the arguments"""
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

"""status 是 objectChoose()程序在while循环里只执行一次的状态变量"""
# status = True
"""idx_list = [] #创建空列表 ,也不能放在大循环外面里，不然列表值会不断累积。"""

#不能写在循环里，不然多次实例化，会再未关闭串口的情况下尝试打开串口，造成错误；
mHandCtrl = None #全局变量；
mHandCtrl = myHandCtrl()

# 线程 threadVideo
tsk = []
threadVideo = threading.Thread(target=video)  # 创建线程。
threadVideo.start()  # 方法threading.Thread.start():启动线程。
tsk.append(threadVideo)
print("tsk:", tsk)

# 线程 threadMyo
mMyo = myMyo(storedPath='online\\')  # 实例化 myMyo 类
mMyo.start()
threadMyo = threading.Thread(target=runMyo)  # 创建线程。
threadMyo.start()  # 方法threading.Thread.start():启动线程。
tsk.append(threadMyo)

print('start join: ' + time.strftime('%H:%M:%S') + "\n")
for tt in tsk:
    tt.join()
print('end join: ' + time.strftime('%H:%M:%S') + "\n")

"""stop the timer and display FPS information"""
fps.stop()
print("")
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

"""do a bit of cleanup"""
vs.stream.release()
cv2.destroyAllWindows()
