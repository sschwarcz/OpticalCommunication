import cv2
import numpy as np
import multiprocessing.queues
from multiprocessing import Process
from datetime import datetime
import EncoderDecoder
import time

locArr = []
processing = []
queuesOUT = []
queuesIN = []
goodSignal = []

def getAllValues():
    authorizedThreads = 1
    lifetime_of_thread = 10

    # onExpected_first_signal = 0.1292
    # offExpected_first_signal = 0.0697
    onExpected_first_signal = 0.1277
    offExpected_first_signal =  0.072
    expectedError_first_signal = 0.03

    time_for_frame_message = 0.3
    package_size=1

    return authorizedThreads,lifetime_of_thread ,onExpected_first_signal,offExpected_first_signal ,expectedError_first_signal,time_for_frame_message,package_size



class POI(Process):  ####################################new point of interest

    def __init__(self , loc , queueI , queueO):
        super(POI , self).__init__()

        self.loc = loc
        self.maxl = None
        self.qIN = queueI
        self.qOUT = queueO
        self.signalOn = [0] * 10
        self.signalOff = [0] * 10
        self.EOF=False
        self.time_of_message=None
        # self.result_available = threading.Event()

    def kill_process(self):
        print("pid-" , self.pid ,"time of message transmition",round(time.time()-self.time_of_message,3))
        self.qOUT.put(("kill" , self.loc))
        print("pid-" , self.pid ,"send kill request")

    def tracking(self):
        newLoc=(self.loc[0] + self.maxl[0] - 50 , self.loc[1] + self.maxl[1] - 50)
        if isCropable(newLoc):
            temploc = self.loc
            self.loc =newLoc

            self.qOUT.put(("loc",(temploc,newLoc)))
            # self.qOUT.put("loc",(newLoc))
        else:
            print("edge __kill process")
            self.kill_process()
        pass

    def get_message(self):

        _,_,_,_,_,time_sleep , packagesize=getAllValues()

        final_message=""
        message = ""
        started = False
        firstdigit=False
        EOF=False
        countofchar=0
        lastDigits=[1]*10
        digitscount=0
        print("pid-" , self.pid , "waiting for message")
        # print("1010000100110111101100001011110100010000001101001011100110010000001110100011010000110010100100000011010110110100101101110011001110010000110000000000")
        start = datetime.now()
        error = 0
        timeEOF =time.time()
        while True:

            if started==False:
                # print("entered get message")
                # print("start == false")
                try:
                    tupleQueue = self.qIN.get()
                except:
                    print("pid-" , self.pid , "error")

                frame = tupleQueue[0]

                timee = tupleQueue[1]
                if (time.time()-timeEOF>6):
                    self.EOF = True
                    break

            else:

                while (time_sleep+error >= (timee - start).total_seconds()) :
                    if started != False:
                        try:
                            tupleQueue = self.qIN.get()
                        except:
                            print("pid-" , self.pid , "error")
                        frame = tupleQueue[0]

                        timee = tupleQueue[1]

                    pass

                pass


            croped_frame = frame[self.loc[1] - 50:self.loc[1] + 50 , self.loc[0] - 50:self.loc[0] + 50]
            # cv2.imshow("cropped" , croped_frame)

            if cv2.waitKey(1) == 27:
                break  # esc to quit
            # cv2.waitKey(0)

            maxLoc , maxVal = getFlashValue(croped_frame)

            if maxVal != 0:
                if firstdigit==False:
                    firstdigit=True
                    started = True
                    # error=0.1
                    self.maxl = maxLoc

                    start = timee
                else:
                    self.maxl = maxLoc
                    message = message + "1"
                    print("1" , end='')
                    # started = True
                    # lastDigits[digitscount] = 1
                    # digitscount = (digitscount + 1) % 10
                    start = timee
            else:
                self.maxl = (50 , 50)
                if started == True:
                    message = message + "0"
                    print("0" , end='')
                    # lastDigits[digitscount] = 0
                    # digitscount = (digitscount + 1) % 10
                    start = timee
            self.tracking()
            if len(message)==8:
                if(message=='01111111'):

                    self.EOF=True
                    print()
                    break
                else:
                    char = EncoderDecoder.binary_toText(message)
                    print(char)
                    final_message=final_message+char
                    message=''
                    countofchar=countofchar+1
                pass
            if countofchar==packagesize:

                break


            # cv2.circle(frame , maxLoc , 50 , (0 , 0 , 255) , 2 , cv2.LINE_AA)
            # cv2.imshow('flash' , frame)
            if cv2.waitKey(1) == 27:
                break  # esc to quit

        return final_message


    def get_some_shit_out(self):
        maxVal=1

        while (maxVal!=0):
            try:
                tupleQueue = self.qIN.get()
            except:
                print("pid-" , self.pid , "error")

            frame = tupleQueue[0]
            timee = tupleQueue[1]
            # print(timee)
            croped_frame = frame[self.loc[1] - 50:self.loc[1] + 50 , self.loc[0] - 50:self.loc[0] + 50]
            # cv2.imshow("cropped" , croped_frame) #little window
            if cv2.waitKey(1) == 27:
                break  # esc to quit
            # cv2.waitKey(0)

            maxLoc , maxVal = getFlashValue(croped_frame)


            pass


    def get_first_signal(self):

        _,_,onExpected,offExpected,expectedError,_,_=getAllValues()

        lowBoundON = onExpected - expectedError
        lowBoundOFF = offExpected - expectedError
        highBoundON = onExpected + expectedError
        highBoundOFF = offExpected + expectedError

        start_on = datetime.now()
        start_off = datetime.now()
        onBool = False
        offBool = False
        onArr = []
        offArr = []
        onMinmax = [10 , 0]
        offMinmax = [10 , 0]

        onIndex = 0
        offIndex = 0

        signal_etablished = False
        flag=50
        # flag_check=False
        final_mess = ""
        while True:
            avgON = sum(self.signalOn) / len(self.signalOn)
            avgOFF = sum(self.signalOff) / len(self.signalOff)

            if avgON < highBoundON and avgON > lowBoundON and avgOFF < highBoundOFF and avgOFF > lowBoundOFF:
                flag=flag-1
                # print(flag)
                if (signal_etablished == False) and (flag<=0):
                    print("enter flag",flag)
                    print("pid-" , self.pid , "good signal")
                    print("pid-" , self.pid , "onAVG-" , avgON , "offAVG-" , avgOFF)
                    # print(onArr)
                    # print(offArr)
                    self.qOUT.put(("true" , self.loc))
                    # self.get_message()
                    signal_etablished = True
                    print("pid-" , self.pid , "start tracking")
                self.tracking()


            else:
                if signal_etablished == True:
                    print("pid-" , self.pid , "first signal lost")
                    print("pid-" , self.pid , "onAVG-" , avgON , "offAVG-" , avgOFF)
                    self.time_of_message = time.time()
                    while(self.EOF==False):
                        final_mess= final_mess+ self.get_message()
                        self.get_some_shit_out()

                    if self.EOF==True:
                        print()
                        print("pid-" , self.pid , "message : ",final_mess)

                    signal_etablished = False
                    self.kill_process()
                pass

            if self.loc[0] < 50 or self.loc[1] < 50 or self.loc[0] > 610 or self.loc[1] > 475:
                print("pid-" , self.pid , "size")
                # self.qIN.close()
                # self.qOUT.close()
                # self.qIN.join_thread()
                # self.qOUT.join_thread()
                self.kill_process()

                break

            try:
                tupleQueue = self.qIN.get()
            except:
                print("pid-" , self.pid , "error")
            frame = tupleQueue[0]
            timee = tupleQueue[1]
            # print(timee)
            croped_frame = frame[self.loc[1] - 50:self.loc[1] + 50 , self.loc[0] - 50:self.loc[0] + 50]
            # cv2.imshow("cropped" , croped_frame) #little window
            if cv2.waitKey(1) == 27:
                break  # esc to quit
            # cv2.waitKey(0)

            maxLoc , maxVal = getFlashValue(croped_frame)

            if maxVal != 0:

                self.maxl = maxLoc

                onBool = True
                if offBool == True:

                    start_on = timee
                    end_off = timee
                    timeoff = round((end_off - start_off).total_seconds() , 3)
                    self.signalOff[offIndex] = timeoff
                    offIndex = (offIndex + 1) % 10
                    # print("end-off" , timeoff)
                    offArr.append(timeoff)

                    if offMinmax[0] > timeoff:
                        offMinmax[0] = timeoff
                    if offMinmax[1] < timeoff and timeoff < 100:
                        offMinmax[1] = timeoff
                    offBool = False

            else:

                self.maxl = (50 , 50)

                offBool = True
                if onBool == True:
                    start_off = timee
                    end_on = timee
                    timeon = round((end_on - start_on).total_seconds() , 3)
                    self.signalOn[onIndex] = timeon
                    onIndex = (onIndex + 1) % 10
                    # print("end-on" , timeon)
                    onArr.append(timeon)
                    if onMinmax[0] > timeon:
                        onMinmax[0] = timeon
                    if onMinmax[1] < timeon and timeon < 100:
                        onMinmax[1] = timeon
                    onBool = False

                if (timee - start_off).total_seconds() > 3 or (timee - start_on).total_seconds() > 4:
                    self.signalOff[offIndex] = 0
                    offIndex = (offIndex + 1) % 10
                    self.signalOn[onIndex] = 0
                    onIndex = (onIndex + 1) % 10

                    pass
            if cv2.waitKey(1) == 27:
                break  # esc to quit
            # self.tracking()
        cv2.destroyAllWindows()

        print("pid-" , self.pid , "off" , self.signalOff)
        print("pid-" , self.pid , "on" , self.signalOn)

    def run(self):
        print("pid-" , self.pid , "start new thread-" , self.loc)
        self.get_first_signal()
        # self.get_message()

def locContain(tuple):
    global locArr
    for i in range(len(locArr)):
        if locArr[i][0] + 50 >= tuple[0] and locArr[i][0] - 50 <= tuple[0] and locArr[i][1] + 50 >= tuple[1] and \
                locArr[i][1] - 50 <= tuple[1]:
            return True
        pass

    return False


def isCropable(loc):
    if loc[0] < 50 or loc[1] < 50 or loc[0] > 610 or loc[1] > 475:
        print("main-" , "not cropable")
        return False
    else:
        return True


def kill_child_process(i):
    process = processing.pop(i)
    print("main- kill process",process[0].pid)
    quOUT = queuesOUT.pop(i)
    quIN = queuesIN.pop(i)
    try:
        quOUT.close()
        quIN.close()
        quOUT.join_thread()
        quIN.join_thread()
        process[0].terminate()
        process[0].join()
    except:
        print("main-" , "queue already stoped")


def getFlashValue(frame):
    hsv = cv2.cvtColor(frame , cv2.COLOR_BGR2HSV)

    lower_flashlight = np.array([0 , 0 , 255])
    upper_flashlight = np.array([0 , 0 , 255])

    mask = cv2.inRange(hsv , lower_flashlight , upper_flashlight)

    (minVal , maxVal , minLoc , maxLoc) = cv2.minMaxLoc(mask)

    return maxLoc , maxVal


def show_webcam(mirror=False):
    cam = cv2.VideoCapture(0)

    # queue.

    authorizedThreads, lifetime_of_thread,_,_,_,_,_= getAllValues()

    processCount = 1

    while True:
        ret_val , img = cam.read()
        if mirror:
            img = cv2.flip(img , 1)
        frame = img

        maxLoc , maxVal = getFlashValue(frame)

        nbrOfProcess = len(queuesOUT)
        for i in range(nbrOfProcess):
            if i < nbrOfProcess:
                queuesOUT[i].put((frame , datetime.now()))

                if queuesIN[i].empty() == False:
                    # print("queueIN not empty")
                    request=queuesIN[i].get()
                    if request[0] == "true":
                        goodSignal[i] = True
                        print("main-" , "communication")
                        #     pass
                    elif request[0]=="loc":
                        oldLoc=request[1][0]
                        newLoc=request[1][1]

                        locArr.remove(oldLoc)
                        locArr.append(newLoc)
                        pass
                    elif request[0] == "kill":
                        # print("main-" , "kill process")
                        kill_child_process(i)
                        locArr.remove(request[1])
                        goodSignal.pop(i)
                        processCount = processCount - 1
                        nbrOfProcess = nbrOfProcess - 1
                        break

                if (datetime.now() - processing[i][1]).total_seconds() > lifetime_of_thread and goodSignal[i] == False:
                    print("main-" , "---" , nbrOfProcess , "-----" , i)
                    kill_child_process(i)
                    processCount = processCount - 1
                    nbrOfProcess = nbrOfProcess - 1
                    print("main-" , "end of time")

        if (maxVal != 0):
            if locContain(maxLoc) == False and isCropable(maxLoc) == True and processCount <= authorizedThreads:
                print("main-" , "enter-" , processCount)
                processCount = processCount + 1
                queueOUT = multiprocessing.Queue()
                queueIN = multiprocessing.Queue()
                # queue.empty()
                queuesOUT.append(queueOUT)
                queuesIN.append(queueIN)
                goodSignal.append(False)
                thread1 = POI(maxLoc , queueOUT , queueIN)

                thread1.start()

                processing.append((thread1 , datetime.now()))
                locArr.append(maxLoc)

            # cv2.circle(frame , maxLoc , 50 , (0 , 0 , 255) , 2 , cv2.LINE_AA)
        # print(locArr)

        # frames=[]
        # frames.append(frame)
        # im_h = cv2.hconcat(frames)
        cv2.imshow('flash' , frame)

        if cv2.waitKey(1) == 27:
            break  # esc to quit

        if cv2.waitKey(1) == ord('c'):
            print("main- unused locations cleared")
            locArr.clear()


    cv2.destroyAllWindows()

def main():
    show_webcam(mirror=False)

if __name__ == '__main__':
    main()
