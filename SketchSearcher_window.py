import tkinter as tk
import cv2
import numpy as np
from tkinter.simpledialog import *
from tkinter.colorchooser import *
from keras.models import load_model
from keras.preprocessing import image
from PIL import Image

## 함수 선언부
def newImage():
    global newHeight, newWidth
    global window, canvas1, paper1, inW, inH, outW, outH, inImage
    global inImageR, inImageG, inImageB, outImageR, outImageG
    global outImageB, filename, cvPhoto

    inW, inH = newWidth, newHeight

    inImageR = np.zeros((inH, inW), dtype=np.uint8) + 255
    inImageG = np.zeros((inH, inW), dtype=np.uint8) + 255
    inImageB = np.zeros((inH, inW), dtype=np.uint8) + 255

    inImage = np.zeros((inH, inW, 3), dtype=np.uint8)
    for i in range(inH):
        for k in range(inW):
            inImage[i][k] = inImageB[i][k], inImageG[i][k], inImageR[i][k]
    defaultImage()

def defaultImage() :
    global window, canvas1, paper1, inW, inH, outW, outH
    global inImageR, inImageG, inImageB, outImageR, outImageG
    global outImageB, filename, cvPhoto
    outImageR, outImageG, outImageB = [], [], []  # 초기화

    # outImage의 크기를 결정
    outH = inH;  outW = inW

    # 빈 메모리 확보
    outImageR = np.zeros((outH, outW), dtype=np.uint8) + 255
    outImageG = np.zeros((outH, outW), dtype=np.uint8) + 255
    outImageB = np.zeros((outH, outW), dtype=np.uint8) + 255

    for i in range(inH) :
        for k in range(inW) :
            outImageR[i][k] = inImageR[i][k]
            outImageG[i][k] = inImageG[i][k]
            outImageB[i][k] = inImageB[i][k]
    displayImage()

def displayImage() :
    global window, canvas1, paper1, inW, inH, outW, outH
    global inImageR, inImageG, inImageB, outImageR, outImageG
    global outImageB, filename, cvPhoto, rate, VIEW_X, VIEW_Y, result
    if canvas1 is not None:
        canvas1.destroy()

    ### 고정된 화면을 준비
    if outW == outH:
        if VIEW_X >= outW or VIEW_Y >= outH:
            VIEW_X = outW
            VIEW_Y = outH
            step = 1
        else:
            rate=2
            if VIEW_X < 512:
                while True:
                    if (VIEW_X*rate) >= 512:
                        VIEW_X *= rate
                        VIEW_Y *= rate
                        break
                    else:
                        rate += 1
            step = outW // VIEW_X
            rate = step
    else:
        if outW > outH:
            rate = 2
            while True:
                if (outW / rate) <= 512:
                    break
                else:
                    rate += 1
            VIEW_X = int(outW / rate)
            VIEW_Y = int(outH / rate)
            step = int(rate)
        else:
            rate = 2
            while True:
                if (outH / rate) <= 512:
                    break
                else:
                    rate += 1
            VIEW_X = int(outW / rate)
            VIEW_Y = int(outH / rate)
            step = int(rate)

    canvas1 = Canvas(window, height=VIEW_Y, width=VIEW_X)
    paper1 = PhotoImage(height=VIEW_Y, width=VIEW_X)
    canvas1.create_image((VIEW_X / 2, VIEW_Y / 2), image=paper1, state='normal')

    rgbString = ''
    switch = True
    for i in range(0, outH, step):
        tmpString = ''
        for k in range(0, outW, step):
            r, g, b = outImageR[i][k], outImageG[i][k], outImageB[i][k]
            tmpString += ' #%02x%02x%02x' % (r, g, b)
            if switch == True and r != 0 and g != 0 and b != 0:
                switch =False

        rgbString += '{'+ tmpString +'} '
    paper1.put(rgbString)
    canvas1.place(x=40, y=60)

    status.configure(text='예측 결과: '+ prediction)
    outImage = np.zeros((outH, outW, 3), dtype=np.uint8)
    for i in range(outH):
        for k in range(outW):
            outImage[i][k] = outImageB[i][k], outImageG[i][k], outImageR[i][k]

def brush(event): #브러쉬 이벤트가 동작하면
    global rate

    try :
        if event.x > 0 or event.x < 512 or event.y > 0 or event.y < 512:
            canvas1.create_line(int(event.x-brushSize/2), int(event.y-brushSize/2),
                                int(event.x+brushSize/2), int(event.y+brushSize/2),
                                width=brushSize, fill=brushColor, smooth=TRUE)

            adjust = int(brushSize/2*rate) # 스케일링 비율
            rc = int(brushColor[1:3], 16) # outImageR에 들어갈 수치
            gc = int(brushColor[3:5], 16) #  outImageG에 들어갈 수치
            bc = int(brushColor[5:], 16) # outImageB에 들어갈 수치

            for i in range((event.y*rate)-adjust, (event.y*rate)+adjust):
                for k in range((event.x*rate)-adjust, (event.x*rate)+adjust):
                    outImageR[i][k] = rc
                    outImageG[i][k] = gc
                    outImageB[i][k] = bc
    except:
        pass

def selectColor():
    global brushColor
    color = askcolor()
    brushColor = color[1]
    brushColorBtn.configure(bg=brushColor)

def brushSizeConfig():
    global brushSize, newWindow, brushSizeENT
    newWindow = Toplevel(window)
    brushSizeENT = Entry(newWindow, width = 4)
    brushSizeENT.insert("end", brushSize)
    brushSizeENT.pack(side =TOP, padx = 5, pady = 5)
    brushCon = Button(newWindow, width = 4, height =1, text= "확인", command = confirmBrush)
    brushCon.pack(side = BOTTOM, padx = 5, pady = 5)

def confirmBrush():
    global brushSize, brushSizeENT, newWindow
    brushSize = int(brushSizeENT.get())
    newWindow.destroy()

def erase():
    global newHeight, newWidth
    global window, canvas1, paper1, canvas2, inW, inH, outW, outH, inImage
    global inImageR, inImageG, inImageB, outImageR, outImageG
    global outImageB, filename, cvPhoto

    canvas2 = Canvas(window, height=512, width=512)
    canvas2.create_rectangle(0, 0, 512, 512, fill='lightgray')
    canvas2.place(x=642, y=60)

    status.configure(text='예측 결과: ')

    inImageR = np.zeros((inH, inW), dtype=np.uint8) + 255
    inImageG = np.zeros((inH, inW), dtype=np.uint8) + 255
    inImageB = np.zeros((inH, inW), dtype=np.uint8) + 255

    inImage = np.zeros((inH, inW, 3), dtype=np.uint8)
    for i in range(inH):
        for k in range(inW):
            inImage[i][k] = inImageB[i][k], inImageG[i][k], inImageR[i][k]
    defaultImage()

def gen_TempImage():
    global inW, inH, outW, outH
    global inImageR, inImageG, inImageB, outImageR, outImageG, outImageB

    outImage = np.zeros((outH, outW, 3), dtype=np.uint8)
    for i in range(outH):
        for k in range(outW):
            outImage[i][k] = outImageB[i][k], outImageG[i][k], outImageR[i][k]
    outImage = np.array(outImage)
    outImage = cv2.resize(outImage, (150, 150))
    cv2.imwrite("tmp.jpg", outImage)

    prediction_image()

def prediction_image():
    global prediction, result, canvas2
    model = load_model('C:/Users/B-13/Anaconda3/project2/project3_skm/skm_classifier10.h5')

    test_image = image.load_img('tmp.jpg', target_size = (150, 150))
    test_image = image.img_to_array(test_image)
    test_image = np.expand_dims(test_image, axis = 0)
    result = model.predict(test_image)
    # training_set.class_indices
    if result[0][0] >= 0.5:
        prediction = '사과'
    elif result[0][1] >= 0.5:
        prediction = '버스'
    elif result[0][2] >= 0.5:
        prediction = '구름'
    elif result[0][3] >= 0.5:
        prediction = '안경'
    elif result[0][4] >= 0.5:
        prediction = '모니터'
    elif result[0][5] >= 0.5:
        prediction = '바지'
    elif result[0][6] >= 0.5:
        prediction = '연필'
    elif result[0][7] >= 0.5:
        prediction = '토끼'
    elif result[0][8] >= 0.5:
        prediction = '해'
    elif result[0][9] >= 0.5:
        prediction = '태극기'
    else:
        prediction = '인식못함'
    print(result, prediction)
    if prediction == '사과':
        pass
    openOpenCV()
    status.configure(text='예측 결과: ' + prediction)

def openOpenCV():
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto, prediction, imageData

    if prediction=="태극기":
        filename = 'm_image/tae.jpg'
    elif prediction=="사과":
        filename = 'm_image/apple.jpg'
    elif prediction=="안경":
        filename = 'm_image/glasses.jpg'
    elif prediction=="토끼":
        filename = 'm_image/rabbit.jpg'
    if filename == "" or filename == None:
        return
    # 파일 --> 메모리
    imageData = cv2.imread(filename)
    loadImageColorCV2(imageData)

    # Input --> outPut으로 동일하게 만들기.
    equalImageColor()

def loadImageColorCV2(imageData):
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto
    inImageR, inImageG, inImageB = [], [], []  # 초기화

    ##########################################
    ## OpenCV용으로 읽어서 보관 + Pillow용으로 변환
    cvData = imageData
    cvPhoto = cv2.cvtColor(cvData, cv2.COLOR_BGR2RGB)
    photo = Image.fromarray(cvPhoto)
    #############################################

    # 파일 크기 계산
    inW = photo.width
    inH = photo.height
    # 빈 메모리 확보 (2차원 리스트)
    for _ in range(inH):
        tmp = []
        for _ in range(inW):
            tmp.append(0)
        inImageR.append(tmp)
    for _ in range(inH):
        tmp = []
        for _ in range(inW):
            tmp.append(0)
        inImageG.append(tmp)
    for _ in range(inH):
        tmp = []
        for _ in range(inW):
            tmp.append(0)
        inImageB.append(tmp)
    # 파일 --> 메모리로 한개씩 옮기기
    photoRGB = photo.convert('RGB')
    for i in range(inH):
        for k in range(inW):
            r, g, b = photoRGB.getpixel((k, i))  #
            inImageR[i][k] = r
            inImageG[i][k] = g
            inImageB[i][k] = b

def equalImageColor():
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, filename
    outImageR, outImageG, outImageB = [], [], []  # 초기화
    # outImage의 크기를 결정
    outH = inH;
    outW = inW
    # 빈 메모리 확보 (2차원 리스트)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageR.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageG.append(tmp)
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImageB.append(tmp)
    #### 영상 처리 알고리즘을 구현 ####
    for i in range(inH):
        for k in range(inW):
            outImageR[i][k] = inImageR[i][k]
            outImageG[i][k] = inImageG[i][k]
            outImageB[i][k] = inImageB[i][k]
    ################################
    displayImageColor()

def displayImageColor():
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, filename, canvas2, prediction
    if canvas2 != None:
        canvas2.destroy()

    ### 고정된 화면을 준비 ###
    VIEW_X, VIEW_Y = 512, 512
    if VIEW_X >= outW or VIEW_Y >= outH:  # 원영상이 256이하면
        VIEW_X = outW
        VIEW_Y = outH
        step = 1
    else:
        step = outW // VIEW_X

    canvas2 = Canvas(window, height=VIEW_Y, width=VIEW_X)
    paper = PhotoImage(height=VIEW_Y, width=VIEW_X)
    canvas2.create_image((VIEW_X / 2, VIEW_Y / 2), image=paper, state='normal')

    rgbString = ''  # 여기에 전체 픽셀 문자열을 저장할 계획
    for i in range(0, outH, step):
        tmpString = ''
        for k in range(0, outW, step):
            r, g, b = outImageR[i][k], outImageG[i][k], outImageB[i][k],
            tmpString += ' #%02x%02x%02x' % (r, g, b)
        rgbString += '{' + tmpString + '} '
    paper.put(rgbString)
    canvas2.place(x=642, y=60)




from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
import os
import urllib
import argparse

def search():
    global prediction
    #prediction='사과'###코드 복붙후에 이 줄 삭제~~
    searchterm = prediction  # will also be the name of the folder
    url = "https://www.google.co.in/search?q=" + searchterm + "&source=lnms&tbm=isch"
    # NEED TO DOWNLOAD CHROMEDRIVER, insert path to chromedriver inside parentheses in following line
    browser = webdriver.Chrome('C:/Users/B-13/Downloads/chromedriver_win32/chromedriver')
    browser.get(url)
    header = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
    counter = 0
    succounter = 0

    if not os.path.exists(searchterm):
        os.mkdir(searchterm)

    for _ in range(3):
        browser.execute_script("window.scrollBy(0,100)")

    for x in browser.find_elements_by_xpath('//div[contains(@class,"rg_meta")]'):
        counter = counter + 1
        print
        "Total Count:", counter
        print
        "Succsessful Count:", succounter
        print
        "URL:", json.loads(x.get_attribute('innerHTML'))["ou"]

        img = json.loads(x.get_attribute('innerHTML'))["ou"]
        imgtype = json.loads(x.get_attribute('innerHTML'))["ity"]
        try:
            req = urllib.Request(img, headers={'User-Agent': header})
            raw_img = urllib.urlopen(req).read()
            File = open(os.path.join(searchterm, searchterm + "_" + str(counter) + "." + imgtype), "wb")
            File.write(raw_img)
            File.close()
            succounter = succounter + 1
        except:
            print
            "can't get img"

    print
    succounter, "pictures succesfully downloaded"

    #browser.close()




## 전역변수 선언부
window, canvas1, paper1, canvas2, paper2 = [None] * 5
inW, inH, outW, outH = [200] * 4
filename = None
cvPhoto = None
inImageR, inImageG, inImageB = [], [], []
outImageR, outImageG, outImageB = [], [], []
brushColor = "#000000" ; brushSize=8
rate=1
VIEW_X, VIEW_Y = 512, 512
newHeight, newWidth = 512, 512
prediction, result = "", [[]]

## 메인 코드부
if __name__ == "__main__":
    window = tk.Tk()
    window.title('Sketch Searcher used CNN')
    window.geometry("1200x600")

    mainMenu = tk.Menu(window)  # 메뉴 전체 껍질
    window.config(menu=mainMenu)

    canvas2 = Canvas(window, height=512, width=512)
    canvas2.create_rectangle(0, 0, 512, 512, fill='lightgray')
    canvas2.place(x=642, y=60)

    # 버튼
    btn1 = Button(window, text="인식", command = gen_TempImage
                        , relief="groove", width=9, height=2, repeatdelay=1000, repeatinterval=100)
    btn1.place(x=562, y=254)

    btn2 = Button(window, text="지우기", command = erase
                        , relief="groove", width=9, height=2, repeatdelay=1000, repeatinterval=100)
    btn2.place(x=562, y=314)

    btn3 = Button(window, text="검색", command=search
                  , relief="groove", width=9, height=2, repeatdelay=1000, repeatinterval=100)
    btn3.place(x=562, y=374)

    ## Status Bar
    status = Label(window, text='예측 결과', relief=SUNKEN, anchor=W)
    status.pack(side=BOTTOM, fill=X)

    ## Tool Bar
    toolFrame = Frame(window, relief=RAISED, bg="GRAY")
    toolFrame.pack(side=TOP, fill=X)

    brushColorBtn = Button(toolFrame, width=3, height=1, background= brushColor, command = selectColor)
    brushColorBtn.pack(side=LEFT, padx=5, pady=5)

    brushSizeBTN = Button(toolFrame, text = "선 굵기", width =6, height = 1, command = brushSizeConfig)
    brushSizeBTN.pack(side=LEFT, padx=5, pady=5)

    newImage()
    window.bind("<B1-Motion>", brush)

    window.mainloop()
