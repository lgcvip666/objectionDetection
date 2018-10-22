import numpy as np
import online
import time
# This class provides the functionality we want. You only need to look at
# this if you want to know how this works. It only needs to be defined
# once, no need to muck around with its internals.
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


# The following example is pretty much the exact use-case of a dictionary,
# but is included for its simplicity. Note that you can include statements
# in each suite.

# v = 'ten'
# for case in switch(v):
    # if case('one'):
        # print 1
        # break
    # if case('two'):
        # print 2
        # break
    # if case('ten'):
        # print 10
        # break
    # if case('eleven'):
        # print 11
        # break
    # if case(): # default, could also just omit condition or 'if True'
        # print "something else!"
        # # No need to break here, it'll stop anyway
        
###################################################################################            
            # print(CLASSES[idx])# 输出标签
            # a = input("input:")
            # if a == 1: # 模拟张手标签
                # for case in switch(CLASSES[idx]):
                    # if case("person"):
                        # print("框选物体 A")
                        # break
                    # if case("bottle"):
                        # print("框选物体 B")
                        # break
                    # if case("chair"):
                        # print("框选物体 C")
                        # break
                    # if case():
                        # print("nothing")
                        
###################################################################################        
###################################################################################            
      
###################################################################################        
        
def objectChoose(list,flag = 0):
    while True:
        with open("txtFiles/openHand.txt") as f1:
            openHand = f1.readline()
            print("openHand:",openHand)
        with open("txtFiles/closeHand.txt") as f2:
            closeHand = f2.readline()
            print("closeHand:",closeHand)
        if openHand == "y":
            print(list[flag]) 
            
            if closeHand == "y":
                print("已通过串口发送指令给假肢手，并对 %s做预备动作" % list[flag])
                break
            if closeHand == "n":
                flag += 1
            if flag == len(list):
                flag = 0

# 2.0：张手 1.0：握拳
def objectChoose_3(list,flag = 0):
    while True:
        print("SVM_prediction:",online.SVM_prediction.tolist()[0])
        if online.SVM_prediction.tolist()[0] == 2.0 : #张手
            print(list[flag]) #框选物体
            if online.SVM_prediction.tolist()[0] == 3.0 :  #握手
                print("已通过串口发送指令给假肢手，并对 %s做预备动作" % list[flag])
                break
            if online.SVM_prediction.tolist()[0] != 3.0:
                flag += 1
            if flag == len(list):
                flag = 0


# 2.0：张手 1.0：握拳
def objectChoose_4(list,flag = 0):
    print("进入物体选择程序")
    while True:
        a = online.SVM_prediction.tolist()[0]
        b = 0
        print("未进入选择循环，SVM_prediction:",a)
        if a == 2.0 : #张手
            print(list[flag]) #框选物体
            b = online.SVM_prediction.tolist()[0]
            print("进入选择 ,SVM_prediction:",b)
            time.sleep(2)
            if b == 2.0 :  #握手3
                print("已通过串口发送指令给假肢手，并对 %s做预备动作" % list[flag])
                break
            if b == 2.0 : #张手
                flag += 1
            if flag == len(list):
                flag = 0

def objectChoose_2(list,flag = 0):
    while True:
        if str(input("模拟张手信号(y/n?)："))=="y":
            print(list[flag]) 
            
        condition = str(input("模拟握拳信号(y/n?)："))
        if condition == "y":
            print("已通过串口发送指令给假肢手，并对 %s做预备动作" % list[flag])
            break 
        if condition == "n":
            flag += 1
        if flag == len(list):
            flag = 0     

if __name__ == '__main__':
        objectChoose(list=["A 物体","B 物体","C 物体"])  
