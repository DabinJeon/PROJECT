######################### Bigtata Integration Tool (Ver 0.06) ######################

from tkinter import *
from tkinter.filedialog import *
from tkinter import messagebox
import pymysql
from tkinter import ttk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.pyplot as plt
import math
from PIL import Image
from PIL import ImageFilter, ImageEnhance
#########################
IP_ADDR = '192.168.111.141' ; USER_NAME = 'director' ; USER_PASS = 'PassWord@1234' ;  DB_NAME="companyDB"

################################ GrayScale Image ###################################

def  openImage() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, filename
    filename = askopenfilename(parent=window, filetypes=(("RAW 파일", "*.raw"), ("모든 파일", "*.*")))
    if filename == "" or filename == None :
        return
    #########################
    loadImage(filename) # 파일 --> 메모리
    #########################
    equalImage() # Input --> outPut으로 동일하게 만들기

# 정방형 이미지
def loadImage(fname) :
    global window, canvas, paper, inW, inH, outW, outH, inImage, outImage
    inImage = [] # 초기화
    #########################
    fsize = os.path.getsize(fname)
    inW = inH = int(math.sqrt(fsize)) # 정방형 이미지 사이즈 지정
    #########################
    for _ in range(inH) : # 빈 메모리 확보 (2차원 리스트)
        tmp = []
        for _ in range(inW) :
            tmp.append(0)
        inImage.append(tmp)
    #########################
    fp = open(fname, 'rb')  # 파일 --> 메모리로 한개씩 옮기기
    for  i  in  range(inH) :
        for k in range(inW) :
            data = int(ord(fp.read(1))) # 1개 픽셀값을 읽음 (0~255)
            inImage[i][k] = data
    fp.close()

def equalImage() :
    global window, canvas, paper, inW, inH, outW, outH, inImage, outImage
    outImage = []
    #########################
    outH = inH;  outW = inW  # outImage의 크기를 결정
    #########################
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImage.append(tmp)
    #########################
    for i in range(inH) : # 영상 처리 알고리즘 구현
        for k in range(inW) :
            outImage[i][k] = inImage[i][k]
    #########################
    displayImage()

def displayImage() :
    global window, canvas, paper, inW, inH, outW, outH, inImage, outImage
    if canvas != None :
        canvas.destroy()
    window.geometry(str(outH) + 'x' + str(outW))
    canvas = Canvas(window, height=outH, width=outW)
    paper = PhotoImage(height=outH, width=outW)
    canvas.create_image((outW / 2, outH / 2), image=paper, state='normal')
    #########################
    rgbString = '' # 여기에 전체 픽셀 문자열을 저장할 계획
    step = 1
    for i in range(0, outH, step) :
        tmpString = ''
        for k in range(0, outW, step) :
            data = outImage[i][k]
            tmpString += ' #%02x%02x%02x' % (data, data, data)
        rgbString += '{' + tmpString + '} '
    paper.put(rgbString)
    #########################
    canvas.pack()

##################################################

import struct # RAW 파일로 저장
def saveFile() :
    global window, canvas, paper, inImage, outImage,inW, inH, outW, outH, filename
    saveFp = asksaveasfile(parent=window, mode='wb', defaultextension="*.raw", filetypes=(("RAW파일", "*.raw"), ("모든파일", "*.*")))
    #########################
    for i in range(outW):
        for k in range(outH):
            saveFp.write( struct.pack('B',outImage[i][k]))
    #########################
    saveFp.close()

import xlsxwriter
def saveExcelImage() :
    global window, canvas, paper, inImage, outImage, inW, inH, outW, outH, filename
    saveFp = asksaveasfile(parent=window, mode='wb', defaultextension="*.xlsx", filetypes=(("엑셀 파일", "*.xlsx"), ("모든파일", "*.*")))
    xlsxName = saveFp.name
    #########################
    sheetName = os.path.basename(xlsxName).split(".")[0]
    wb = xlsxwriter.Workbook(xlsxName)
    ws = wb.add_worksheet(sheetName)
    #########################
    ws.set_column(0, outW, 1.0) #워크시트의 폭 조절  # 실제로 약 0.34쯤.
    #########################
    for  r  in range(outH) : #워크시트의 높이 조절
        ws.set_row(r, 9.5)  # 실제로 약 0.35쯤
    #########################
    for rowNum in range(outH) : # 각 셀마다 색상 지정
        for colNum in range(outW) :
            data = outImage[rowNum][colNum]
            #########################
            if data > 15 : # data 값으로 셀의 배경색을 조절... #000000 ~ #FFFFFF
                hexStr = '#' + hex(data)[2:] * 3
            else :
                hexStr = '#' + ('0' + hex(data)[2:] ) * 3
            #########################
            cell_format = wb.add_format() ## 셀의 포맷 형식을 준비
            cell_format.set_bg_color(hexStr)
            ws.write(rowNum,colNum,'', cell_format)
    #########################
    wb.close()
    messagebox.showinfo('완료', xlsxName + ' 저장됨')

##################################################

# 테이블로 DB의 grayImage 불러오기
def loadDB() :
    global window, canvas, paper, inW, inH, outW, outH, inImage, outImage, filename
    global window2, sheet, rows
    con = pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, database=DB_NAME, charset='utf8')
    cur = con.cursor()
    #########################
    sql = "SELECT id, imageName, imageType FROM grayImageTBL"
    cur.execute(sql)
    rows = cur.fetchall()
    #########################
    window2 = Toplevel(window) # 새로운 윈도창 띄우기
    sheet = ttk.Treeview(window2, height=10);    sheet.pack()
    descs = cur.description
    colNames = [d[0] for d in descs]
    sheet.column("#0", width=80);
    sheet.heading("#0", text=colNames[0])
    sheet["columns"] = colNames[1:]
    for colName in colNames[1:]:
        sheet.column(colName, width=80);
        sheet.heading(colName, text=colName)
    for row in rows :
        sheet.insert('', 'end', text=row[0], values=row[1:])
    sheet.bind('<Double-1>', sheetDblClick)
    #########################
    cur.close()
    con.close()

def sheetDblClick(event) :
    global window, canvas, paper, inW, inH, outW, outH, inImage, outImage, filename
    global window2, sheet, rows
    #########################
    item = sheet.identify('item', event.x, event.y) # 'I001' ....
    entNum = int(item[1:]) - 1  # 쿼리한 결과 리스트의 순번
    id = rows[entNum][0] # 선택한 id
    window2.destroy()
    #########################
    con = pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, database=DB_NAME, charset='utf8')
    cur = con.cursor()
    sql = "SELECT imageName, grayImage FROM grayImageTBL WHERE id=" + str(id) # ID로 이미지 추출하기
    cur.execute(sql)
    row = cur.fetchone()
    cur.close()
    con.close()
    #########################
    import tempfile
    # 임시 폴더
    fname, binData = row
    fullPath = tempfile.gettempdir()+ '/' + fname # 임시경로 + 파일명
    fp = open(fullPath , 'wb') # 폴더를 지정.
    fp.write(binData)
    fp.close()
    #########################
    if fname.split('.')[1].upper() != 'RAW' :
        messagebox.showinfo('None Type', fname + 'Not RAW File')
        return
    #########################
    filename = fname
    #########################
    loadImage(fullPath) # 파일 --> 메모리
    equalImage()

##################################################

#raw 이미지를 DB에 저장
def rawToPixelDB() :
    global window, canvas, paper, inW, inH, outW, outH, inImage, outImage, filename
    global window2, sheet, rows
    if outImage == [] or outImage == None :
        return
    #########################
    con = pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, database=DB_NAME, charset='utf8')
    cur = con.cursor()
    #########################
    fname = os.path.basename(filename); ftype = fname.split(".")[1]; xSize = outW;ySize = outH
    import random
    if filename == '' or filename == None :
        filename = "image" + random.randint(100000) +str(ftype)
    #########################
    for i in range(outH) :
        for k in range(outW) :
            sql = "INSERT INTO colorImageTBL( id, imageName, imageType, xSize, ySize, x, y, r, g, b) VALUES (NULL, '" + fname + "', '" + str(ftype) + "', " + str(xSize) + ", " + str(ySize) + ", "
            r = g = b = outImage[i][k]
            sql += str(i) + ", " + str(k) + ", " + str(r)  + ", " + str(g) + ", " + str(b) + ")"
            cur.execute(sql)
    #########################
    cur.close()
    con.commit()
    con.close()
    messagebox.showinfo('complete', fname + 'image saved to grayImageTBL')

# 테이블의 행단위로 정보를 RAW 이미지(inImage) 로딩
def PixelDBToRaw() :
    global window, canvas, paper, inW, inH, outW, outH, inImage, outImage, filename
    global window2, sheet, rows
    con = pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, database=DB_NAME, charset='utf8')
    cur = con.cursor()
    #########################
    sql = "SELECT DISTINCT imageName, imageType, xSize, ySize FROM colorImageTBL"
    cur.execute(sql)
    rows = cur.fetchall()
    #########################
    ## 새로운 윈도창 띄우기
    window2 = Toplevel(window)
    sheet = ttk.Treeview(window2, height=10);    sheet.pack()
    descs = cur.description
    colNames = [d[0] for d in descs]
    sheet.column("#0", width=80)
    sheet.heading("#0", text=colNames[0])
    sheet["columns"] = colNames[1:]
    for colName in colNames[1:]:
        sheet.column(colName, width=80)
        sheet.heading(colName, text=colName)
    for row in rows :
        sheet.insert('', 'end', text=row[0], values=row[1:])
    sheet.bind('<Double-1>', sheetDblClick2)
    #########################
    cur.close()
    con.close()

# 흑백이미지로 출력
def sheetDblClick2(event) :
    global window, canvas, paper, inW, inH, outW, outH, inImage, outImage, filename
    global window2, sheet, rows
    #########################
    item = sheet.identify('item', event.x, event.y) # 'I001' ....
    entNum = int(item[1:]) - 1  ## 쿼리한 결과 리스트의 순번
    fileID = rows[entNum][0] ## 선택한 id
    window2.destroy()
    #########################
    con = pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, database=DB_NAME, charset='utf8')
    cur = con.cursor()
    sql = "SELECT x, y, r, g, b FROM colorTBL WHERE fName='" + fileID + "'" # ID로 이미지 추출하기
    cur.execute(sql)
    #########################
    colorRows = cur.fetchall()
    cur.close()
    con.close()
    #########################
    inW = rows[entNum][2]; inH=rows[entNum][3]
    inImage = []
    #########################
    for _ in range(inH) :  # 빈 메모리 확보 (2차원 리스트)
        tmp = []
        for _ in range(inW) :
            tmp.append(0)
        inImage.append(tmp)
    for row in colorRows :
        x, y, r, g, b = row
        inImage[x][y] = r
    #########################
    equalImage()

##################################################

from tkinter.simpledialog import  *
def addImage() :
    global window, canvas, paper, inW, inH, outW, outH, inImage, outImage
    value = askinteger("Brighter Image", "value : ")
    #########################
    for i in range(outH) :
        for k in range(outW) :
            if outImage[i][k] + value > 255 :
                outImage[i][k] = 255
            else :
                outImage[i][k] = outImage[i][k] + value
    #########################
    displayImage()

def zoomOutImage() :
    global window, canvas, paper, inW, inH, outW, outH, inImage, outImage
    outImage = []  # 초기화
    scale = askinteger("Zoom Out Image", "value : ")
    outH = inH//scale;  outW = inW//scale
    #########################
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImage.append(tmp)
    #########################
    for i in range(outH) :
        for k in range(outW) :
            outImage[i][k] = inImage[i*scale][k*scale]
    #########################
    displayImage()

def zoomInImage() :
    global window, canvas, paper, inW, inH, outW, outH, inImage, outImage
    outImage = []  # 초기화
    scale = askinteger("Zoom In Image", "value : ")
    outH = inH*scale;  outW = inW*scale
    #########################
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImage.append(tmp)
    #########################
    for i in range(outH) :
        for k in range(outW) :
            outImage[i][k] = inImage[i//scale][k//scale]
    #########################
    displayImage()

##################################################

def embossingMaskGray() :
    global window, canvas, paper, inW, inH, outW, outH, inImage, outImage
    outImage = []  # 초기화
    outH = inH;  outW = inW
    #########################
    for _ in range(outH):
        tmp = []
        for _ in range(outW):
            tmp.append(0)
        outImage.append(tmp)
    #########################
    MSIZE=3
    mask = [ [-1, 0, 0],
             [ 0, 0, 0],
             [ 0, 0, 1],  ]
    #########################
    tmpInImage = [] # 임시 입력 영상
    for _ in range(inH + 2) :
        tmp = []
        for _ in range(inW + 2) :
            tmp.append(127)
        tmpInImage.append(tmp)
    #########################
    tmpOutImage = [] # 임시 출력 영상
    for _ in range(outH ) :
        tmp = []
        for _ in range(outW) :
            tmp.append(0)
        tmpOutImage.append(tmp)
    #########################
    for i in range(inH) : # 입력 --> 임시입력
        for k in range(inW) :
            tmpInImage[i+1][k+1] = inImage[i][k]
    #########################
    for i in range(1, inH) : # 회선 연산 : 마스크로 긁어서 계산
        for k in range(1, inW) :
            # 1점을 처리하기. 3x3 반복 처리.  각 위치끼리 곱한후 합계...
            S = 0.0
            for  m  in range(0, MSIZE) :
                for n in range(0, MSIZE) :
                    S += mask[m][n] * tmpInImage[i+(m-1)][k+(n-1)]
            tmpOutImage[i-1][k-1] = S
        #########################
        for i in range(outH): # 마스크의 합계가 0일 경우엔 127 정도를 더함 (영상이 너무 어두워지는것 방지)
            for k in range(outW):
                tmpOutImage[i][k] += 127
        #########################
        for i in range(outH):  # 임시 출력 --> 출력
            for k in range(outW):
                value = int(tmpOutImage[i][k])
                if value > 255:
                    value = 255
                elif value < 0:
                    value = 0
                outImage[i][k] = value
    #########################
    displayImage()

##################################################

def averageRAW() :
    global window, canvas, paper, inW, inH, outW, outH, inImage, outImage
    rawSum =0
    for i in range(inH) :
        for k in range(inW) :
            rawSum += inImage[i][k]
    inRawAvg = rawSum // (inH * inW) # 입력영상 평균값
    rawSum = 0
    for i in range(outH):
        for k in range(outW):
            rawSum += outImage[i][k]
    outRawAvg = rawSum // (inH * inW)  # 출력영상 평균값
    #########################
    subWindow = Toplevel(window);    subWindow.geometry('100x50')
    label1 = Label(subWindow, text='Input Image Average  : ' + str(inRawAvg)); label1.pack()
    label2 = Label(subWindow, text='Output Image Average : ' + str(outRawAvg)); label2.pack()
    subWindow.mainloop()

def histoRAW() :
    global window, canvas, paper, inW, inH, outW, outH, inImage, outImage
    countList = [0] * 256 ; normalList = [0] * 256
    # 빈도수 세기
    for i in range(outH):
        for k in range(outW):
            value = outImage[i][k]
            countList[value] += 1
    # 정규화 시키기 : 정규화된값 = (카운트값 - 최소값) * 최대높이 / (최대값 - 최소값)
    maxValue = max(countList);  minValue = min(countList)
    for i in range(len(countList)) :
        normalList[i] = (countList[i] - minValue) * 256 / (maxValue - minValue)
    # 히스토그램 그리기
    subWindow = Toplevel(window);    subWindow.geometry('256x256')
    subCanvas = Canvas(subWindow, width=256, height=256)
    subPaper = PhotoImage(width=256, height=256)
    subCanvas.create_image( (256/2, 256/2), image=subPaper, state='normal')
    #########################
    for i in range(0, 256) :
        for k in range(0, int(normalList[i])) :
            if k > 255 :
                break
            data = 0
            subPaper.put('#%02x%02x%02x' % (data, data, data), (i, 255-k))
    #########################
    subCanvas.pack(expand=1, anchor=CENTER)
    subWindow.mainloop()

import matplotlib.pyplot as plt
def matHistoRAW() :
    global window, canvas, paper, inW, inH, outW, outH, inImage, outImage
    countList = [0] * 256
    # 빈도수 세기
    for i in range(outH):
        for k in range(outW):
            value = outImage[i][k]
            countList[value] += 1
    plt.plot(countList)
    plt.show()

################################## Color Image #####################################

def  openImageColor() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, filename
    filename = askopenfilename(parent=window, filetypes=(("Image File", "*.gif;*.jpg;*.png;*.bmp;*.tif"), ("All File", "*.*")))
    if filename == "" or filename == None :
        return
    #########################
    loadImageColor(filename)
    #########################
    equalImageColor()

from PIL import Image
def loadImageColor(fname) :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, filename, photo
    inImageR, inImageG, inImageB = [], [], [] # 초기화
    #########################
    photo = Image.open(fname)
    inW = photo.width;  inH = photo.height
    #########################
    inImageR = np.zeros((inH, inW), dtype=np.uint8) # 빈 메모리 확보 (2차원 리스트)
    inImageG = np.zeros((inH, inW), dtype=np.uint8)
    inImageB = np.zeros((inH, inW), dtype=np.uint8)
    #########################
    photoRGB = photo.convert('RGB') # 파일 --> 메모리로 한개씩 옮기기
    for  i  in  range(inH) :
        for k in range(inW) :
            r, g, b = photoRGB.getpixel((k, i)) #
            inImageR[i][k] = r; inImageG[i][k] = g; inImageB[i][k] = b

def equalImageColor() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, filename
    outImageR, outImageG, outImageB = [], [], []  # 초기화
    #########################
    outH = inH;  outW = inW
    #########################
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
    #########################
    for i in range(inH) :
        for k in range(inW) :
            outImageR[i][k] = inImageR[i][k]
            outImageG[i][k] = inImageG[i][k]
            outImageB[i][k] = inImageB[i][k]
    ################################
    displayImageColor()

# 큰 이미지는 step을 주어 출력하기 (상태창 표시)
def displayImageColor() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, filename
    if canvas != None:
        canvas.destroy()
    #########################
    VIEW_X, VIEW_Y = 512, 512 # 고정된 화면을 준비
    if VIEW_X >= outW and VIEW_Y >= outH:  # 원영상이 256이하면
        VIEW_X = outW;
        VIEW_Y = outH
        step = 1
    else:
        if outW > outH:
            step = outW / VIEW_X
        else:
            step = outH / VIEW_X
    #########################
    window.geometry(str(int(VIEW_X * 1.2)) + 'x' + str(int(VIEW_Y * 1.2)))
    canvas = Canvas(window, height=VIEW_Y, width=VIEW_X)
    paper = PhotoImage(height=VIEW_Y, width=VIEW_X)
    canvas.create_image((VIEW_X / 2, VIEW_Y / 2), image=paper, state='normal')
    #########################
    import numpy
    rgbString = ''  # 여기에 전체 픽셀 문자열을 저장할 계획
    for i in numpy.arange(0, outH, step):
        tmpString = ''
        for k in numpy.arange(0, outW, step):
            i = int(i);
            k = int(k)
            try:
                r, g, b = outImageR[i][k], outImageG[i][k], outImageB[i][k]
            except:
                pass
            tmpString += ' #%02x%02x%02x' % (r, g, b)
        rgbString += '{' + tmpString + '} '
    paper.put(rgbString)
    canvas.pack(expand=1, anchor=CENTER)
    status.configure(text='이미지 정보:' + str(outW) + 'x' + str(outH))

##################################################

def saveImageColor() :
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    outArray = []
    for i in range(outH) :
        tmpList = []
        for k in range(outW) :
            tup = tuple([outImageR[i][k], outImageG[i][k], outImageB[i][k]])
            tmpList.append(tup)
        outArray.append(tmpList)
    #########################
    outArray = np.array(outArray)
    savePhoto = Image.fromarray(outArray.astype('uint8'), 'RGB')
    #########################
    saveFp = asksaveasfile(parent=window, mode='w', defaultextension=".", filetypes=(("Image File", "*.gif;*.jpg;*.png;*.bmp;*.tif"), ("All File", "*.*")))
    savePhoto.save(saveFp.name)
    #########################
    print('OK! save')

##################################################

def colorToPixelDB() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, filename
    global window2, sheet, rows
    # if outImageR == [] or outImageR == None :
    #     return
    #########################
    con = pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, database=DB_NAME, charset='utf8')
    cur = con.cursor()
    #########################
    fname = os.path.basename(filename); ftype = fname.split(".")[1]; xSize = outW;ySize = outH
    #########################
    for i in range(outH) :
        for k in range(outW) :
            sql = "INSERT INTO colorImageTBL( id, imageName, imageType, xSize, ySize, x, y, r, g, b) VALUES (NULL, '" + fname + "', '" + str(ftype) + "', " + str(xSize) + ", " + str(ySize) + ", "
            r = outImageR[i][k]
            g = outImageG[i][k]
            b = outImageB[i][k]
            sql += str(i) + ", " + str(k) + ", " + str(r)  + ", " + str(g) + ", " + str(b) + ")"
            cur.execute(sql)
    #########################
    cur.close()
    con.commit()
    con.close()
    messagebox.showinfo('complete', fname + 'image saved to grayImageTBL')

# 테이블의 행단위로 정보를 RAW 이미지(inImage) 로딩
def PixelDBToColor() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, filename
    global window2, sheet, rows
    con = pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, database=DB_NAME, charset='utf8')
    cur = con.cursor()
    #########################
    sql = "SELECT DISTINCT imageName, imageType, xSize, ySize FROM colorImageTBL"
    cur.execute(sql)
    rows = cur.fetchall()
    #########################
    ## 새로운 윈도창 띄우기
    window2 = Toplevel(window)
    sheet = ttk.Treeview(window2, height=10);    sheet.pack()
    descs = cur.description
    colNames = [d[0] for d in descs]
    sheet.column("#0", width=80)
    sheet.heading("#0", text=colNames[0])
    sheet["columns"] = colNames[1:]
    for colName in colNames[1:]:
        sheet.column(colName, width=80)
        sheet.heading(colName, text=colName)
    for row in rows :
        sheet.insert('', 'end', text=row[0], values=row[1:])
    sheet.bind('<Double-1>', sheetDblClick3)
    #########################
    cur.close()
    con.close()

# 흑백이미지로 출력
def sheetDblClick3(event) :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, filename
    global window2, sheet, rows
    #########################
    item = sheet.identify('item', event.x, event.y) # 'I001' ....
    entNum = int(item[1:]) - 1  ## 쿼리한 결과 리스트의 순번
    fileID = rows[entNum][0] ## 선택한 id
    window2.destroy()
    #########################
    con = pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, database=DB_NAME, charset='utf8')
    cur = con.cursor()
    sql = "SELECT x, y, r, g, b FROM colorImageTBL WHERE imageName='" + fileID + "'" # ID로 이미지 추출하기
    cur.execute(sql)
    #########################
    colorRows = cur.fetchall()
    cur.close()
    con.close()
    #########################
    inW = rows[entNum][2]; inH=rows[entNum][3]
    inImage = []
    #########################
    for _ in range(inH) :
        tmp = []
        for _ in range(inW) :
            tmp.append(0)
        inImageR.append(tmp)
    for _ in range(inH) :
        tmp = []
        for _ in range(inW) :
            tmp.append(0)
        inImageG.append(tmp)
    for _ in range(inH) :
        tmp = []
        for _ in range(inW) :
            tmp.append(0)
        inImageB.append(tmp)
    #########################
    for row in colorRows :
        x, y, r, g, b = row
        inImageR[x][y] = r
        inImageG[x][y] = g
        inImageB[x][y] = b
    #########################
    equalImageColor()

##################################################

def mirrorImageColor() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, filename
    outImageR, outImageG, outImageB = [], [], []  # 초기화
    #########################
    outH = inH;  outW = inW
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
    #########################
    for i in range(inH) :
        for k in range(inW) :
            outImageR[inH-1-i][k] = inImageR[i][k]
            outImageG[inH-1-i][k] = inImageG[i][k]
            outImageB[inH-1-i][k] = inImageB[i][k]
    #########################
    displayImageColor()

def reverseImageColorNumPy() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, filename
    outImageR, outImageG, outImageB = [], [], []  # 초기화
    #########################
    outH = inH; outW = inW
    #########################
    outImageR = np.zeros((outH, outW), dtype=np.uint8)  # 빈 메모리 확보
    outImageG = np.zeros((outH, outW), dtype=np.uint8)
    outImageB = np.zeros((outH, outW), dtype=np.uint8)
    #########################
    outImageR = 255 - inImageR
    outImageG = 255 - inImageG
    outImageB = 255 - inImageB
    #########################
    displayImageColor()

def zoomOutImageColor() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, filename
    outImageR, outImageG, outImageB = [], [], []  # 초기화
    scale = askinteger("Zoom Out Image", "value : ")
    #########################
    outH = inH//scale;  outW = inW//scale
    #########################
    for _ in range(outH): # 빈 메모리 확보
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
    #########################
    for i in range(outH) :
        for k in range(outW) :
            outImageR[i][k] = inImageR[i*scale][k*scale]
            outImageG[i][k] = inImageG[i * scale][k * scale]
            outImageB[i][k] = inImageB[i * scale][k * scale]
    #########################
    displayImageColor()

def zoomInImageColor() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, filename
    outImageR, outImageG, outImageB = [], [], []  # 초기화
    scale = askinteger("확대 값", "값 입력")
    #########################
    outH = inH*scale;  outW = inW*scale
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
    #########################
    for i in range(outH) :
        for k in range(outW) :
            outImageR[i][k] = inImageR[i//scale][k//scale]
            outImageG[i][k] = inImageG[i // scale][k // scale]
            outImageB[i][k] = inImageB[i // scale][k // scale]
    #########################
    displayImageColor()

def bwImageColor() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, filename
    outImageR, outImageG, outImageB = [], [], []  # 초기화
    #########################
    outH = inH;  outW = inW
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
    #########################
    hap = 0
    for i in range(inH) :
        for k in range(inW) :
            tData = (inImageR[i][k] + inImageG[i][k] + inImageB[i][k]) // 3
            hap += tData
    avg = hap // (inW*inH)
    #########################
    for i in range(inH) :
        for k in range(inW) :
            if (inImageR[i][k] + inImageG[i][k] + inImageB[i][k]) // 3 >= avg :
                outImageR[i][k] = outImageG[i][k] = outImageB[i][k] = 255
            else :
                outImageR[i][k] = outImageG[i][k] = outImageB[i][k] = 0
    #########################
    displayImageColor()

##################################################

def embossingColorPillow() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, filename, photo
    #########################
    photo2 = photo.copy() ## Pillow 라이브러리가 제공해주는 메소드(함수)를 사용해서 처리
    photo2 = photo2.filter(ImageFilter.EMBOSS)
    #########################
    outImageR, outImageG, outImageB = [], [], []  # 초기화
    outH = inH;  outW = inW
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
    #########################
    photoRGB = photo2.convert('RGB')
    for i in range(outH):
        for k in range(outW):
            r, g, b = photoRGB.getpixel((k, i))  #
            outImageR[i][k] = r
            outImageG[i][k] = g
            outImageB[i][k] = b
    #########################
    displayImageColor()

##################################################

def matHistoColor() :
    global window, canvas, paper, inW, inH, outW, outH, inImage, outImage
    countListR = [0] * 256 ;
    #########################
    for i in range(outH):
        for k in range(outW):
            value = outImageR[i][k]
            countListR[value] += 1
    plt.plot(countListR)
    #########################
    countListG = [0] * 256;
    for i in range(outH):
        for k in range(outW):
            value = outImageG[i][k]
            countListG[value] += 1
    plt.plot(countListG)
    #########################
    countListB = [0] * 256;
    for i in range(outH):
        for k in range(outW):
            value = outImageB[i][k]
            countListB[value] += 1
    plt.plot(countListB)
    plt.show()

###################################### OpenCV ######################################

import cv2
def  openOpenCV() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto
    #########################
    filename = askopenfilename(parent=window, filetypes=(("Image file", "*.jpg;*.png;*.bmp;*.tif"), ("All file", "*.*")))
    if filename == "" or filename == None :
        return
    #########################
    imageData = cv2.imread(filename)  # 파일 --> 메모리
    loadImageColorCV2(imageData)
    #########################
    equalImageColor()

def loadImageColorCV2(imageData) :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto
    inImageR, inImageG, inImageB = [], [], [] # 초기화
    #########################
    cvData = imageData  # OpenCV용으로 읽어서 보관 + Pillow용으로 변환
    cvPhoto = cv2.cvtColor(cvData, cv2.COLOR_BGR2RGB)
    photo = Image.fromarray(cvPhoto)
    #########################
    inW = photo.width;  inH = photo.height
    for _ in range(inH) : # 빈 메모리 확보 (2차원 리스트)
        tmp = []
        for _ in range(inW) :
            tmp.append(0)
        inImageR.append(tmp)
    for _ in range(inH) :
        tmp = []
        for _ in range(inW) :
            tmp.append(0)
        inImageG.append(tmp)
    for _ in range(inH) :
        tmp = []
        for _ in range(inW) :
            tmp.append(0)
        inImageB.append(tmp)
    #########################
    photoRGB = photo.convert('RGB') # 파일 --> 메모리로 한개씩 옮기기
    for  i  in  range(inH) :
        for k in range(inW) :
            r, g, b = photoRGB.getpixel((k, i)) #
            inImageR[i][k] = r; inImageG[i][k] = g; inImageB[i][k] = b

import numpy as np
def toColorImage(photo2) :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto
    outImageR, outImageG, outImageB = [], [], []  # 초기화
    #########################
    outH = inH;  outW = inW
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
    #########################
    photoRGB = photo2.convert('RGB')
    for i in range(outH):
        for k in range(outW):
            r, g, b = photoRGB.getpixel((k, i))  #
            outImageR[i][k] = r;
            outImageG[i][k] = g;
            outImageB[i][k] = b
    #########################
    displayImageColor()

##################################################

def embossingCV2() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto
    #########################
    cvPhoto2 = cvPhoto[:] # 엠보싱을 CV2 메소드로 구현하기 --> photo2로 넘기기
    mask = np.zeros((3,3), np.float32);   mask[0][0] = -1 ; mask[2][2] = 1
    cvPhoto2 = cv2.filter2D(cvPhoto2, -1, mask)
    cvPhoto2 += 127
    photo2 = Image.fromarray(cvPhoto2)
    #########################
    toColorImage(photo2)

##################################################

def faceCV2() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto
    #########################
    # CV2 메소드로 구현하기 --> photo2로 넘기기
    cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
    cvPhoto2 = cvPhoto[:]  # 복사
    cvGray = cv2.cvtColor(cvPhoto2, cv2.COLOR_RGB2GRAY)
    #########################
    face_rects = cascade.detectMultiScale(cvGray, 1.1, 5) # 얼굴 인식하는 사각형을 추출
    #########################
    for (x,y,w,h) in face_rects :
        cv2.rectangle(cvPhoto2, (x,y), (x+w, y+h), (0,255,0), 3)
    #########################
    photo2 = Image.fromarray(cvPhoto2)
    #########################
    toColorImage(photo2)

def maskCV2() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto
    # CV2 메소드로 구현하기 --> photo2로 넘기기
    cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
    faceMask = cv2.imread('C:/Images/images(ML)/moustache.png')
    h_mask, w_mask = faceMask.shape[:2]
    #########################
    cvPhoto2 = cvPhoto[:]  # 복사
    cvGray = cv2.cvtColor(cvPhoto2, cv2.COLOR_BGR2GRAY)
    #########################
    face_rects = cascade.detectMultiScale(cvGray, 1.1, 5)

    #########################
    for (x,y,w,h) in face_rects :
        if h > 0 and w > 0 :
            x = int(x + 0.1*w)
            y = int(y + 0.6*h)
            w = int(0.8 * w)
            h = int(0.2 * h)
            cvPhoto2_2 = cvPhoto2[y:y+h, x:x+w]
            faceMask_small = cv2.resize(faceMask, (w, h), interpolation=cv2.INTER_AREA)
            gray_mask = cv2.cvtColor(faceMask_small,cv2.COLOR_RGB2GRAY)
            ret, mask = cv2.threshold(gray_mask, 50, 255, cv2.THRESH_BINARY)
            mask_inv = cv2.bitwise_not(mask)
            maskedFace = cv2.bitwise_and(faceMask_small, faceMask_small, mask = mask)
            maskedFrame = cv2.bitwise_and(cvPhoto2_2, cvPhoto2_2, mask=mask_inv)
            cvPhoto2[y:y+h, x:x+w] = cv2.add(maskedFace, maskedFrame)
    #########################
    photo2 = Image.fromarray(cvPhoto2)
    #########################
    toColorImage(photo2)

def objectCV2() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto
    #########################
    # 블러링을 CV2 메소드로 구현하기 --> photo2로 넘기기
    cvPhoto2 = cvPhoto[:]  # 복사
    image = cvPhoto2
    #########################
    args = {'image': filename, 'prototxt': 'MobileNetSSD_deploy.prototxt.txt',
     'model': 'MobileNetSSD_deploy.caffemodel', 'confidence': 0.2}
    #########################
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
               "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
               "sofa", "train", "tvmonitor"]
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
    net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
    #########################
    #image = cv2.imread(args["image"])
    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()
    #########################
    for i in np.arange(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > args["confidence"]:
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            #########################
            label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
            print("[INFO] {}".format(label))
            cv2.rectangle(image, (startX, startY), (endX, endY),  COLORS[idx], 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(image, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
    #########################
    cvPhoto2 = image
    #########################
    photo2 = Image.fromarray(cvPhoto2)
    ###########################################################
    toColorImage(photo2)

def videoCV2() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto
    global frame # 동영상의 한장면
    #########################
    vFname = askopenfilename(parent=window, filetypes=(("Video file", "*.mp4"), ("All file", "*.*")))
    if vFname == "" or vFname == None :
        return
    cap = cv2.VideoCapture(vFname)  # 0이면 카메라
    s_factor = 0.5 # 화면 크기 배율
    #########################
    import time
    while True :
        ret, frame = cap.read()  # 한개 장면
        frame = cv2.resize(frame, None, fx=s_factor, fy=s_factor, interpolation=cv2.INTER_AREA)
        #time.sleep(0.1) # 동영상 속도 조절
        #########DeepLearning 알고리즘############
        image = frame
        #########################
        args = {'image': filename, 'prototxt': 'MobileNetSSD_deploy.prototxt.txt',
                'model': 'MobileNetSSD_deploy.caffemodel', 'confidence': 0.2}
        #########################
        CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
                   "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                   "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                   "sofa", "train", "tvmonitor"]
        COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
        net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
        #########################
        # image = cv2.imread(args["image"])
        (h, w) = image.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)
        net.setInput(blob)
        detections = net.forward()
        #########################
        for i in np.arange(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > args["confidence"]:
                idx = int(detections[0, 0, i, 1])
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                #########################
                label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
                print("[INFO] {}".format(label))
                cv2.rectangle(image, (startX, startY), (endX, endY), COLORS[idx], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(image, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
        #########################
        frame = image
        cv2.imshow('DeepLearning', frame)
        #########################
        c = cv2.waitKey(1)
        if  c == 27 : # 27:ESC키
            break
        elif c == ord('c') or c == ord('C') :
            captureVideo()
            window.update()
    #########################
    cap.release()
    cv2.destroyAllWindows()

def captureVideo() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto
    global frame  # 동영상의 한장면
    #########################
    loadImageColorCV2(frame)
    equalImageColor()

def insertCustomerTBL():
    global customerInsertEnt1, customerInsertEnt2, customerInsertEnt3, customerInsertEnt4, customerInsertEnt5
    window2=Tk(); window2.title('CustomerTBL : Insert Data'); window.geometry('800x500')
    #########################
    insertFrame = Frame(window2); insertFrame.pack(side=TOP)
    #########################
    label1 = Label(insertFrame, width=5, text="  id :"); label2 = Label(insertFrame, width=5, text="name :");
    label3 = Label(insertFrame, width=4, text="age :"); label4 = Label(insertFrame, width=6, text="gender :");
    label5 = Label(insertFrame, width=6, text="nation :")
    #########################
    customerInsertEnt1 = Entry(insertFrame, width=10); customerInsertEnt2 = Entry(insertFrame, width=10)
    customerInsertEnt3 = Entry(insertFrame, width=10); customerInsertEnt4 = Entry(insertFrame, width=10)
    customerInsertEnt5 = Entry(insertFrame, width=10)
    CustomerInsertBtn = Button(insertFrame, text='INSERT', command=customerInsert)
    #########################
    label1.pack(side=LEFT, pady=10); customerInsertEnt1.pack(side=LEFT, padx=9, pady=10)
    label2.pack(side=LEFT, pady=10); customerInsertEnt2.pack(side=LEFT, padx=10, pady=10)
    label3.pack(side=LEFT, pady=10); customerInsertEnt3.pack(side=LEFT, padx=10, pady=10)
    label4.pack(side=LEFT, pady=10); customerInsertEnt4.pack(side=LEFT, padx=10, pady=10)
    label5.pack(side=LEFT, pady=10); customerInsertEnt5.pack(side=LEFT, padx=10, pady=10)
    CustomerInsertBtn.pack(side=LEFT, padx=10, pady=10)
    #########################
    window2.mainloop()

#################################### Database ######################################

def selectCustomerTBL():
    global window
    global customerList1, customerList2, customerList3, customerList4, customerList5
    global CustomerSelectEnt1, CustomerSelectEnt2, CustomerSelectEnt3
    topframe = Frame(window); topframe.pack(side=TOP)
    bottomFrame = Frame(window); bottomFrame.pack(side=BOTTOM, fill=BOTH, expand=1)
    #########################
    CustomerSelectEnt1 = Entry(topframe, width=10); CustomerSelectBtn1 = Button(topframe, text='SEARCH', command=customerIdSelect)
    CustomerSelectEnt2 = Entry(topframe, width=10); CustomerSelectBtn2 = Button(topframe, text='SEARCH', command=customerGenderSelect)
    CustomerSelectEnt3 = Entry(topframe, width=10); CustomerSelectBtn3 = Button(topframe, text='SEARCH', command=customerNationSelect)
    label1 = Label(topframe, width=2,text="id :"); label2 = Label(topframe, width=7,text="gender :")
    label3 = Label(topframe, width=6,text="nation :")
    #########################
    label1.pack(side=LEFT, pady=5); CustomerSelectEnt1.pack(side=LEFT, padx=10, pady=5); CustomerSelectBtn1.pack(side=LEFT, padx=10, pady=5)
    label2.pack(side=LEFT, pady=5); CustomerSelectEnt2.pack(side=LEFT, padx=10, pady=5); CustomerSelectBtn2.pack(side=LEFT, padx=10, pady=5)
    label3.pack(side=LEFT, pady=5); CustomerSelectEnt3.pack(side=LEFT, padx=10, pady=5); CustomerSelectBtn3.pack(side=LEFT, padx=10, pady=5)
    #########################
    CustomerShowBtn = Button(topframe, text='SHOW ALL', command=customerShow); CustomerShowBtn.pack(side=RIGHT, padx=10, pady=5)
    #########################
    customerList1 = Listbox(bottomFrame, bg='white'); customerList1.pack(side=LEFT, fill=BOTH, expand=1)
    customerList2 = Listbox(bottomFrame, bg='white'); customerList2.pack(side=LEFT, fill=BOTH, expand=1)
    customerList3 = Listbox(bottomFrame, bg='white'); customerList3.pack(side=LEFT, fill=BOTH, expand=1)
    customerList4 = Listbox(bottomFrame, bg='white'); customerList4.pack(side=LEFT, fill=BOTH, expand=1)
    customerList5 = Listbox(bottomFrame, bg='white'); customerList5.pack(side=LEFT, fill=BOTH, expand=1)


def deleteCustomerTBL():
    global customerDeleteEnt
    window2=Tk(); window2.title('CustomerTBL : Delete Data'); window.geometry('800x500')
    #########################
    cautionFrame = Frame(window2); cautionFrame.pack(side=TOP)
    deleteFrame = Frame(window2); deleteFrame.pack(side=TOP)
    #########################
    label0 = Label(cautionFrame, width=10, height=1, text= "* CAUTION *")
    #########################
    label1 = Label(deleteFrame, width=4, text="    id :");  customerDeleteEnt = Entry(deleteFrame, width=10)
    CustomerDeleteBtn = Button(deleteFrame, text='DELETE', command=customerDelete)
    #########################
    label0.pack(side=LEFT, padx=9, pady=10)
    label1.pack(side=LEFT,padx=3, pady=10); customerDeleteEnt.pack(side=LEFT, padx=9, pady=10)
    CustomerDeleteBtn.pack(side=LEFT, padx=10, pady=10)
    #########################
    window2.mainloop()

def customerShow():
    global customerList1, customerList2, customerList3, customerList4, customerList5
    con= pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, db="companyDB")
    cur=con.cursor()
    #########################
    sql = "SELECT id,name,age,gender,nation FROM customerTBL"
    cur.execute(sql)
    idList=[]; nameList=[]; ageList=[]; genderList=[]; nationList=[]
    #########################
    while True:
        row = cur.fetchone()
        if row == "" or row == None:
            break
        idList.append(row[0])
        nameList.append(row[1])
        ageList.append(row[2])
        genderList.append(row[3])
        nationList.append(row[4])
    #########################
    customerList1.delete(0, customerList1.size() - 1); customerList2.delete(0, customerList2.size() - 1)
    customerList3.delete(0, customerList3.size() - 1); customerList4.delete(0, customerList4.size() - 1)
    customerList5.delete(0, customerList5.size() - 1)
    #########################
    for id,name,age,gender,nation in zip(idList,nameList,ageList,genderList,nationList):
        customerList1.insert(END, id)
        customerList2.insert(END,name)
        customerList3.insert(END, age)
        customerList4.insert(END, gender)
        customerList5.insert(END, nation)
    #########################
    cur.close() ; con.commit(); con.close()

def customerIdSelect():
    global customerList1, customerList2, customerList3, customerList4, customerList5
    global CustomerSelectEnt1, CustomerSelectEnt2, CustomerSelectEnt3
    con= pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, db="companyDB")
    cur = con.cursor()
    #########################
    sql = "SELECT id,name,age,gender,nation FROM customerTBL WHERE id='"+CustomerSelectEnt1.get()+"'"
    cur.execute(sql)
    idList=[]; nameList=[]; ageList=[]; genderList=[]; nationList=[]
    #########################
    while True:
        row = cur.fetchone()
        if row == "" or row == None:
            break
        idList.append(row[0])
        nameList.append(row[1])
        ageList.append(row[2])
        genderList.append(row[3])
        nationList.append(row[4])
    #########################
    customerList1.delete(0, customerList1.size() - 1); customerList2.delete(0, customerList2.size() - 1)
    customerList3.delete(0, customerList3.size() - 1); customerList4.delete(0, customerList4.size() - 1)
    customerList5.delete(0, customerList5.size() - 1)
    #########################
    for id,name,age,gender,nation in zip(idList,nameList,ageList,genderList,nationList):
        customerList1.insert(END, id)
        customerList2.insert(END,name)
        customerList3.insert(END, age)
        customerList4.insert(END, gender)
        customerList5.insert(END, nation)
    #########################
    cur.close() ; con.commit(); con.close()

def customerGenderSelect():
    global customerList1, customerList2, customerList3, customerList4, customerList5
    global CustomerSelectEnt1, CustomerSelectEnt2, CustomerSelectEnt3
    con= pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, db="companyDB")
    cur = con.cursor()
    #########################
    sql = "SELECT id,name,age,gender,nation FROM customerTBL WHERE gender='"+CustomerSelectEnt2.get()+"'"
    cur.execute(sql)
    idList=[]; nameList=[]; ageList=[]; genderList=[]; nationList=[]
    #########################
    while True:
        row = cur.fetchone()
        if row == "" or row == None:
            break
        idList.append(row[0])
        nameList.append(row[1])
        ageList.append(row[2])
        genderList.append(row[3])
        nationList.append(row[4])
    #########################
    customerList1.delete(0, customerList1.size() - 1); customerList2.delete(0, customerList2.size() - 1)
    customerList3.delete(0, customerList3.size() - 1); customerList4.delete(0, customerList4.size() - 1)
    customerList5.delete(0, customerList5.size() - 1)
    #########################
    for id,name,age,gender,nation in zip(idList,nameList,ageList,genderList,nationList):
        customerList1.insert(END, id)
        customerList2.insert(END,name)
        customerList3.insert(END, age)
        customerList4.insert(END, gender)
        customerList5.insert(END, nation)
    #########################
    cur.close() ; con.commit(); con.close()

def customerNationSelect():
    global customerList1, customerList2, customerList3, customerList4, customerList5
    global CustomerSelectEnt1, CustomerSelectEnt2, CustomerSelectEnt3
    con= pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, db="companyDB")
    cur = con.cursor()
    #########################
    sql = "SELECT id,name,age,gender,nation FROM customerTBL WHERE nation='"+CustomerSelectEnt3.get()+"'"
    cur.execute(sql)
    idList=[]; nameList=[]; ageList=[]; genderList=[]; nationList=[]
    #########################
    while True:
        row = cur.fetchone()
        if row == "" or row == None:
            break
        idList.append(row[0])
        nameList.append(row[1])
        ageList.append(row[2])
        genderList.append(row[3])
        nationList.append(row[4])
    #########################
    customerList1.delete(0, customerList1.size() - 1); customerList2.delete(0, customerList2.size() - 1)
    customerList3.delete(0, customerList3.size() - 1); customerList4.delete(0, customerList4.size() - 1)
    customerList5.delete(0, customerList5.size() - 1)
    #########################
    for id,name,age,gender,nation in zip(idList,nameList,ageList,genderList,nationList):
        customerList1.insert(END, id)
        customerList2.insert(END,name)
        customerList3.insert(END, age)
        customerList4.insert(END, gender)
        customerList5.insert(END, nation)
    #########################
    cur.close() ; con.commit(); con.close()

def customerInsert():
    global customerInsertEnt1, customerInsertEnt2, customerInsertEnt3, customerInsertEnt4, customerInsertEnt5
    con= pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, db="companyDB")
    cur = con.cursor()
    #########################
    id = customerInsertEnt1.get(); name = customerInsertEnt2.get(); age = customerInsertEnt3.get()
    gender =  customerInsertEnt4.get(); nation = customerInsertEnt5.get()
    sql = "INSERT INTO customerTBL VALUES('" +id+ "', '" +name+ "'," +age+ ",'" +gender+ "','" +nation+ "')"
    cur.execute(sql)
    #########################
    messagebox.showinfo("complete","INSERT complete")
    #########################
    cur.close(); con.commit(); con.close()

def customerDelete():
    global customerDeleteEnt
    con= pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, db="companyDB")
    cur = con.cursor()
    #########################
    id = customerDeleteEnt.get()
    sql = "DELETE FROM customerTBL WHERE id='" +id+ "'"
    cur.execute(sql)
    #########################
    messagebox.showinfo("complete","DELETE complete")
    #########################
    cur.close(); con.commit(); con.close()

##################################################

def selectSales02TBL():
    global window, canvas, paper, sheet
    global sales02List1, sales02List2, sales02List3, sales02List4, sales02List5
    global Sales02SelectEnt1, Sales02SelectEnt2, Sales02SelectEnt3
    #########################
    topframe = Frame(window); topframe.pack(side=TOP)
    bottomFrame = Frame(window); bottomFrame.pack(side=BOTTOM, fill=BOTH, expand=1)
    #########################
    Sales02SelectEnt1 = Entry(topframe, width=10); Sales02SelectBtn1 = Button(topframe, text='SEARCH', command=sales02IdSelect)
    Sales02SelectEnt2 = Entry(topframe, width=10); Sales02SelectBtn2 = Button(topframe, text='SEARCH', command=sales02InvoiceSelect)
    Sales02SelectEnt3 = Entry(topframe, width=10); Sales02SelectBtn3 = Button(topframe, text='SEARCH', command=sales02ProductSelect)
    label1 = Label(topframe, width=2,text="id :"); label2 = Label(topframe, width=11,text="invoice_num :")
    label3 = Label(topframe, width=11,text="product_num :")
    #########################
    label1.pack(side=LEFT, pady=10); Sales02SelectEnt1.pack(side=LEFT, padx=10, pady=10); Sales02SelectBtn1.pack(side=LEFT, padx=10, pady=10)
    label2.pack(side=LEFT, pady=10); Sales02SelectEnt2.pack(side=LEFT, padx=10, pady=10); Sales02SelectBtn2.pack(side=LEFT, padx=10, pady=10)
    label3.pack(side=LEFT, pady=10); Sales02SelectEnt3.pack(side=LEFT, padx=10, pady=10); Sales02SelectBtn3.pack(side=LEFT, padx=10, pady=10)
    #########################
    Sales02ShowBtn = Button(topframe, text='SHOW ALL', command=Sales02Show); Sales02ShowBtn.pack(side=RIGHT, padx=10, pady=10)
    #########################
    sales02List1 = Listbox(bottomFrame, bg='white'); sales02List1.pack(side=LEFT, fill=BOTH, expand=1)
    sales02List2 = Listbox(bottomFrame, bg='white'); sales02List2.pack(side=LEFT, fill=BOTH, expand=1)
    sales02List3 = Listbox(bottomFrame, bg='white'); sales02List3.pack(side=LEFT, fill=BOTH, expand=1)
    sales02List4 = Listbox(bottomFrame, bg='white'); sales02List4.pack(side=LEFT, fill=BOTH, expand=1)
    sales02List5 = Listbox(bottomFrame, bg='white'); sales02List5.pack(side=LEFT, fill=BOTH, expand=1)

def Sales02Show():
    global window, canvas, paper, sheet
    global sales02List1, sales02List2, sales02List3, sales02List4, sales02List5
    con= pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, db="companyDB")
    cur=con.cursor()
    #########################
    sql = "SELECT * FROM sales_2019_02TBL"
    cur.execute(sql)
    idList=[]; invoiceList=[]; productList=[]; costList=[]; dateList=[]
    #########################
    while True:
        row = cur.fetchone()
        if row == "" or row == None:
            break
        idList.append(row[0])
        invoiceList.append(row[1])
        productList.append(row[2])
        costList.append(row[3])
        dateList.append(row[4])
    #########################
    sales02List1.delete(0, sales02List1.size() - 1); sales02List2.delete(0, sales02List2.size() - 1)
    sales02List3.delete(0, sales02List3.size() - 1); sales02List4.delete(0, sales02List4.size() - 1)
    sales02List5.delete(0, sales02List5.size() - 1)
    #########################
    for id,name,age,gender,nation in zip(idList,invoiceList,productList,costList,dateList):
        sales02List1.insert(END, id)
        sales02List2.insert(END,name)
        sales02List3.insert(END, age)
        sales02List4.insert(END, gender)
        sales02List5.insert(END, nation)
    #########################
    cur.close() ; con.commit(); con.close()

def sales02IdSelect():
    global sales02List1, sales02List2, sales02List3, sales02List4, sales02List5
    global Sales02SelectEnt1, Sales02SelectEnt2, Sales02SelectEnt3
    con= pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, db="companyDB")
    cur = con.cursor()
    #########################
    sql = "SELECT * FROM sales_2019_02TBL WHERE id='"+Sales02SelectEnt1.get()+"'"
    cur.execute(sql)
    idList=[]; invoice_numList=[]; product_numList=[]; costList=[]; purchase_dateList=[]
    #########################
    while True:
        row = cur.fetchone()
        if row == "" or row == None:
            break
        idList.append(row[0])
        invoice_numList.append(row[1])
        product_numList.append(row[2])
        costList.append(row[3])
        purchase_dateList.append(row[4])
    #########################
    sales02List1.delete(0, sales02List1.size() - 1); sales02List2.delete(0, sales02List2.size() - 1)
    sales02List3.delete(0, sales02List3.size() - 1); sales02List4.delete(0, sales02List4.size() - 1)
    sales02List5.delete(0, sales02List5.size() - 1)
    #########################
    for id,invoice,product,cost,date in zip(idList,invoice_numList,product_numList,costList,purchase_dateList):
        sales02List1.insert(END, id)
        sales02List2.insert(END, invoice)
        sales02List3.insert(END, product)
        sales02List4.insert(END, cost)
        sales02List5.insert(END, date)
    #########################
    cur.close() ; con.commit(); con.close()

def sales02InvoiceSelect():
    global sales02List1, sales02List2, sales02List3, sales02List4, sales02List5
    global Sales02SelectEnt1, Sales02SelectEnt2, Sales02SelectEnt3
    con= pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, db="companyDB")
    cur = con.cursor()
    #########################
    sql = "SELECT * FROM sales_2019_02TBL WHERE invoice_num='"+Sales02SelectEnt2.get()+"'"
    cur.execute(sql)
    idList=[]; invoice_numList=[]; product_numList=[]; costList=[]; purchase_dateList=[]
    #########################
    while True:
        row = cur.fetchone()
        if row == "" or row == None:
            break
        idList.append(row[0])
        invoice_numList.append(row[1])
        product_numList.append(row[2])
        costList.append(row[3])
        purchase_dateList.append(row[4])
    #########################
    sales02List1.delete(0, sales02List1.size() - 1); sales02List2.delete(0, sales02List2.size() - 1)
    sales02List3.delete(0, sales02List3.size() - 1); sales02List4.delete(0, sales02List4.size() - 1)
    sales02List5.delete(0, sales02List5.size() - 1)
    #########################
    for id,invoice,product,cost,date in zip(idList,invoice_numList,product_numList,costList,purchase_dateList):
        sales02List1.insert(END, id)
        sales02List2.insert(END, invoice)
        sales02List3.insert(END, product)
        sales02List4.insert(END, cost)
        sales02List5.insert(END, date)
    #########################
    cur.close() ; con.commit(); con.close()

def sales02ProductSelect():
    global sales02List1, sales02List2, sales02List3, sales02List4, sales02List5
    global Sales02SelectEnt1, Sales02SelectEnt2, Sales02SelectEnt3
    con= pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, db="companyDB")
    cur = con.cursor()
    #########################
    sql = "SELECT * FROM sales_2019_02TBL WHERE product_num="+Sales02SelectEnt3.get()
    cur.execute(sql)
    idList=[]; invoice_numList=[]; product_numList=[]; costList=[]; purchase_dateList=[]
    #########################
    while True:
        row = cur.fetchone()
        if row == "" or row == None:
            break
        idList.append(row[0])
        invoice_numList.append(row[1])
        product_numList.append(row[2])
        costList.append(row[3])
        purchase_dateList.append(row[4])
    #########################
    sales02List1.delete(0, sales02List1.size() - 1); sales02List2.delete(0, sales02List2.size() - 1)
    sales02List3.delete(0, sales02List3.size() - 1); sales02List4.delete(0, sales02List4.size() - 1)
    sales02List5.delete(0, sales02List5.size() - 1)
    #########################
    for id,invoice,product,cost,date in zip(idList,invoice_numList,product_numList,costList,purchase_dateList):
        sales02List1.insert(END, id)
        sales02List2.insert(END, invoice)
        sales02List3.insert(END, product)
        sales02List4.insert(END, cost)
        sales02List5.insert(END, date)
    #########################
    cur.close() ; con.commit(); con.close()

##################################################

def selectSales03TBL():
    global window, canvas, paper, sheet
    global sales03List1, sales03List2, sales03List3, sales03List4, sales03List5
    global Sales03SelectEnt1, Sales03SelectEnt2, Sales03SelectEnt3
    #########################
    topframe = Frame(window); topframe.pack(side=TOP)
    bottomFrame = Frame(window); bottomFrame.pack(side=BOTTOM, fill=BOTH, expand=1)
    #########################
    Sales03SelectEnt1 = Entry(topframe, width=10); Sales03SelectBtn1 = Button(topframe, text='SEARCH', command=sales03IdSelect)
    Sales03SelectEnt2 = Entry(topframe, width=10); Sales03SelectBtn2 = Button(topframe, text='SEARCH', command=sales03InvoiceSelect)
    Sales03SelectEnt3 = Entry(topframe, width=10); Sales03SelectBtn3 = Button(topframe, text='SEARCH', command=sales03ProductSelect)
    label1 = Label(topframe, width=2,text="id :"); label2 = Label(topframe, width=11,text="invoice_num :")
    label3 = Label(topframe, width=11,text="product_num :")
    #########################
    label1.pack(side=LEFT, pady=10); Sales03SelectEnt1.pack(side=LEFT, padx=10, pady=10); Sales03SelectBtn1.pack(side=LEFT, padx=10, pady=10)
    label2.pack(side=LEFT, pady=10); Sales03SelectEnt2.pack(side=LEFT, padx=10, pady=10); Sales03SelectBtn2.pack(side=LEFT, padx=10, pady=10)
    label3.pack(side=LEFT, pady=10); Sales03SelectEnt3.pack(side=LEFT, padx=10, pady=10); Sales03SelectBtn3.pack(side=LEFT, padx=10, pady=10)
    #########################
    Sales03ShowBtn = Button(topframe, text='SHOW ALL', command=Sales03Show); Sales03ShowBtn.pack(side=RIGHT, padx=10, pady=10)
    #########################
    sales03List1 = Listbox(bottomFrame, bg='white'); sales03List1.pack(side=LEFT, fill=BOTH, expand=1)
    sales03List2 = Listbox(bottomFrame, bg='white'); sales03List2.pack(side=LEFT, fill=BOTH, expand=1)
    sales03List3 = Listbox(bottomFrame, bg='white'); sales03List3.pack(side=LEFT, fill=BOTH, expand=1)
    sales03List4 = Listbox(bottomFrame, bg='white'); sales03List4.pack(side=LEFT, fill=BOTH, expand=1)
    sales03List5 = Listbox(bottomFrame, bg='white'); sales03List5.pack(side=LEFT, fill=BOTH, expand=1)

def Sales03Show():
    global window, canvas, paper, sheet
    global sales03List1, sales03List2, sales03List3, sales03List4, sales03List5
    con= pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, db="companyDB")
    cur=con.cursor()
    #########################
    sql = "SELECT * FROM sales_2019_03TBL"
    cur.execute(sql)
    idList=[]; invoiceList=[]; productList=[]; costList=[]; dateList=[]
    #########################
    while True:
        row = cur.fetchone()
        if row == "" or row == None:
            break
        idList.append(row[0])
        invoiceList.append(row[1])
        productList.append(row[2])
        costList.append(row[3])
        dateList.append(row[4])
    #########################
    sales03List1.delete(0, sales03List1.size() - 1); sales03List2.delete(0, sales03List2.size() - 1)
    sales03List3.delete(0, sales03List3.size() - 1); sales03List4.delete(0, sales03List4.size() - 1)
    sales03List5.delete(0, sales03List5.size() - 1)
    #########################
    for id,name,age,gender,nation in zip(idList,invoiceList,productList,costList,dateList):
        sales03List1.insert(END, id)
        sales03List2.insert(END,name)
        sales03List3.insert(END, age)
        sales03List4.insert(END, gender)
        sales03List5.insert(END, nation)
    #########################
    cur.close() ; con.commit(); con.close()

def sales03IdSelect():
    global sales03List1, sales03List2, sales03List3, sales03List4, sales03List5
    global Sales03SelectEnt1, Sales03SelectEnt2, Sales03SelectEnt3
    con= pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, db="companyDB")
    cur = con.cursor()
    #########################
    sql = "SELECT * FROM sales_2019_03TBL WHERE id='"+Sales03SelectEnt1.get()+"'"
    cur.execute(sql)
    idList=[]; invoice_numList=[]; product_numList=[]; costList=[]; purchase_dateList=[]
    #########################
    while True:
        row = cur.fetchone()
        if row == "" or row == None:
            break
        idList.append(row[0])
        invoice_numList.append(row[1])
        product_numList.append(row[2])
        costList.append(row[3])
        purchase_dateList.append(row[4])
    #########################
    sales03List1.delete(0, sales03List1.size() - 1); sales03List2.delete(0, sales03List2.size() - 1)
    sales03List3.delete(0, sales03List3.size() - 1); sales03List4.delete(0, sales03List4.size() - 1)
    sales03List5.delete(0, sales03List5.size() - 1)
    #########################
    for id,invoice,product,cost,date in zip(idList,invoice_numList,product_numList,costList,purchase_dateList):
        sales03List1.insert(END, id)
        sales03List2.insert(END, invoice)
        sales03List3.insert(END, product)
        sales03List4.insert(END, cost)
        sales03List5.insert(END, date)
    #########################
    cur.close() ; con.commit(); con.close()

def sales03InvoiceSelect():
    global sales03List1, sales03List2, sales03List3, sales03List4, sales03List5
    global Sales03SelectEnt1, Sales03SelectEnt2, Sales03SelectEnt3
    con= pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, db="companyDB")
    cur = con.cursor()
    #########################
    sql = "SELECT * FROM sales_2019_03TBL WHERE invoice_num='"+Sales03SelectEnt2.get()+"'"
    cur.execute(sql)
    idList=[]; invoice_numList=[]; product_numList=[]; costList=[]; purchase_dateList=[]
    #########################
    while True:
        row = cur.fetchone()
        if row == "" or row == None:
            break
        idList.append(row[0])
        invoice_numList.append(row[1])
        product_numList.append(row[2])
        costList.append(row[3])
        purchase_dateList.append(row[4])
    #########################
    sales03List1.delete(0, sales03List1.size() - 1); sales03List2.delete(0, sales03List2.size() - 1)
    sales03List3.delete(0, sales03List3.size() - 1); sales03List4.delete(0, sales03List4.size() - 1)
    sales03List5.delete(0, sales03List5.size() - 1)
    #########################
    for id,invoice,product,cost,date in zip(idList,invoice_numList,product_numList,costList,purchase_dateList):
        sales03List1.insert(END, id)
        sales03List2.insert(END, invoice)
        sales03List3.insert(END, product)
        sales03List4.insert(END, cost)
        sales03List5.insert(END, date)
    #########################
    cur.close() ; con.commit(); con.close()

def sales03ProductSelect():
    global sales03List1, sales03List2, sales03List3, sales03List4, sales03List5
    global Sales03SelectEnt1, Sales03SelectEnt2, Sales03SelectEnt3
    con= pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, db="companyDB")
    cur = con.cursor()
    #########################
    sql = "SELECT * FROM sales_2019_03TBL WHERE product_num="+Sales03SelectEnt3.get()
    cur.execute(sql)
    idList=[]; invoice_numList=[]; product_numList=[]; costList=[]; purchase_dateList=[]
    #########################
    while True:
        row = cur.fetchone()
        if row == "" or row == None:
            break
        idList.append(row[0])
        invoice_numList.append(row[1])
        product_numList.append(row[2])
        costList.append(row[3])
        purchase_dateList.append(row[4])
    #########################
    sales03List1.delete(0, sales03List1.size() - 1); sales03List2.delete(0, sales03List2.size() - 1)
    sales03List3.delete(0, sales03List3.size() - 1); sales03List4.delete(0, sales03List4.size() - 1)
    sales03List5.delete(0, sales03List5.size() - 1)
    #########################
    for id,invoice,product,cost,date in zip(idList,invoice_numList,product_numList,costList,purchase_dateList):
        sales03List1.insert(END, id)
        sales03List2.insert(END, invoice)
        sales03List3.insert(END, product)
        sales03List4.insert(END, cost)
        sales03List5.insert(END, date)
    #########################
    cur.close() ; con.commit(); con.close()

##################################################

def selectSupplies03TBL():
    global window, canvas, paper, sheet
    global Supplies03List1, Supplies03List2, Supplies03List3, Supplies03List4, Supplies03List5
    global Supplies03SelectEnt1, Supplies03SelectEnt2, Supplies03SelectEnt3
    #########################
    topframe = Frame(window); topframe.pack(side=TOP)
    bottomFrame = Frame(window); bottomFrame.pack(side=BOTTOM, fill=BOTH, expand=1)
    #########################
    Supplies03SelectEnt1 = Entry(topframe, width=10); Supplies03SelectBtn1 = Button(topframe, text='SEARCH', command=None)
    Supplies03SelectEnt2 = Entry(topframe, width=10); Supplies03SelectBtn2 = Button(topframe, text='SEARCH', command=None)
    Supplies03SelectEnt3 = Entry(topframe, width=10); Supplies03SelectBtn3 = Button(topframe, text='SEARCH', command=None)
    label1 = Label(topframe, width=8,text="supplies :"); label2 = Label(topframe, width=11,text="invoice_num :")
    label3 = Label(topframe, width=11,text="product_num :")
    #########################
    label1.pack(side=LEFT, pady=10); Supplies03SelectEnt1.pack(side=LEFT, padx=10, pady=10); Supplies03SelectBtn1.pack(side=LEFT, padx=10, pady=10)
    label2.pack(side=LEFT, pady=10); Supplies03SelectEnt2.pack(side=LEFT, padx=10, pady=10); Supplies03SelectBtn2.pack(side=LEFT, padx=10, pady=10)
    label3.pack(side=LEFT, pady=10); Supplies03SelectEnt3.pack(side=LEFT, padx=10, pady=10); Supplies03SelectBtn3.pack(side=LEFT, padx=10, pady=10)
    #########################
    Sales03ShowBtn = Button(topframe, text='ALL', command=supplies03Show); Sales03ShowBtn.pack(side=RIGHT, padx=10, pady=10)
    #########################
    Supplies03List1 = Listbox(bottomFrame, bg='white'); Supplies03List1.pack(side=LEFT, fill=BOTH, expand=1)
    Supplies03List2 = Listbox(bottomFrame, bg='white'); Supplies03List2.pack(side=LEFT, fill=BOTH, expand=1)
    Supplies03List3 = Listbox(bottomFrame, bg='white'); Supplies03List3.pack(side=LEFT, fill=BOTH, expand=1)
    Supplies03List4 = Listbox(bottomFrame, bg='white'); Supplies03List4.pack(side=LEFT, fill=BOTH, expand=1)
    Supplies03List5 = Listbox(bottomFrame, bg='white'); Supplies03List5.pack(side=LEFT, fill=BOTH, expand=1)

def supplies03Show():
    global window, canvas, paper, sheet
    global Supplies03List1, Supplies03List2, Supplies03List3, Supplies03List4, Supplies03List5
    con= pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, db="companyDB")
    cur=con.cursor()
    #########################
    sql = "SELECT * FROM supplies_2019_03TBL"
    cur.execute(sql)
    idList=[]; invoiceList=[]; productList=[]; costList=[]; dateList=[]
    #########################
    while True:
        row = cur.fetchone()
        if row == "" or row == None:
            break
        idList.append(row[0])
        invoiceList.append(row[1])
        productList.append(row[2])
        costList.append(row[3])
        dateList.append(row[4])
    #########################
    Supplies03List1.delete(0, Supplies03List1.size() - 1); Supplies03List2.delete(0, Supplies03List2.size() - 1)
    Supplies03List3.delete(0, Supplies03List3.size() - 1); Supplies03List4.delete(0, Supplies03List4.size() - 1)
    Supplies03List5.delete(0, Supplies03List5.size() - 1)
    #########################
    for id,name,age,gender,nation in zip(idList,invoiceList,productList,costList,dateList):
        Supplies03List1.insert(END, id)
        Supplies03List2.insert(END,name)
        Supplies03List3.insert(END, age)
        Supplies03List4.insert(END, gender)
        Supplies03List5.insert(END, nation)
    #########################
    cur.close() ; con.commit(); con.close()

##################################################

def readySQL():
    global customerSQLEnt
    window2=Tk(); window2.title('CompanyDB : use SQL'); window.geometry('800x500')
    #########################
    cautionFrame = Frame(window2); cautionFrame.pack(side=TOP)
    deleteFrame = Frame(window2); deleteFrame.pack(side=TOP)
    #########################
    label0 = Label(cautionFrame, width=60, height=1, text= "Connected with Fedora22( MySQL Server)  -  companyDB ")
    #########################
    label1 = Label(deleteFrame, width=6, text="   SQL :");  customerSQLEnt = Entry(deleteFrame, width=70)
    CustomerSQLBtn = Button(deleteFrame, text='INPUT', command=insertSQL)
    #########################
    label0.pack(side=LEFT, padx=9, pady=10)
    label1.pack(side=LEFT,padx=3, pady=10); customerSQLEnt.pack(side=LEFT, padx=9, pady=10)
    CustomerSQLBtn.pack(side=LEFT, padx=10, pady=10)
    #########################
    window2.mainloop()

def insertSQL():
    global customerSQLEnt
    con= pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, db="companyDB")
    cur = con.cursor()
    #########################
    SQLsentence = customerSQLEnt.get()
    try:
        sql = SQLsentence
        cur.execute(sql)
    except:
        messagebox.showinfo("incorrect SQL syntax", "You have an error in your SQL syntax")
        return
    #########################
    messagebox.showinfo("complete","complete")
    #########################
    cur.close(); con.commit(); con.close()

################################## Excel File ######################################

import xlrd
def openExcelFile() :
    global excelList
    #########################
    filename = askopenfilename(parent=window, filetypes=(("xls 파일", "*.xls;*.xlsx"), ("모든 파일", "*.*")))
    if filename == "" or filename == None:
        return
    workbook = xlrd.open_workbook(filename)
    sheetCount = workbook.nsheets
    #########################
    firstYN = True
    for worksheet in workbook.sheets() :
        sRow = worksheet.nrows
        sCol = worksheet.ncols
        for i in range(sRow) :
            if firstYN == True and i == 0 :
                firstYN = False
                pass
            elif firstYN == False and i != 0 :
                pass
            elif firstYN == False and i == 0 :
                print(i, end='   ')
                continue
            #########################
            tmpList = []
            for k in range(sCol) :
                value = worksheet.cell_value(i,k)
                tmpList.append(value)
            excelList.append(tmpList)
    #########################
    drawSheet(excelList)

import xlwt
def saveExcelFile() :
    global excelList
    if excelList==[] or excelList==None:
        return
    #########################
    saveFp = asksaveasfile(parent=window, mode='w',
                               defaultextension=".csv", filetypes=(("액샐 파일", "*.xls"), ("모든파일", "*.*")))
    #########################
    filename=saveFp.name
    workbook=xlwt.Workbook()
    outSheet=workbook.add_sheet('sheet1')
    #########################
    for i in range(len(excelList)):
        for k in range(len(excelList[1])):
            outSheet.write(i,k, excelList[i][k])
    #########################
    workbook.save(filename)
    messagebox.showinfo('complete',filename+'save complete')

def saveExcelToDB_sales_2019_03():
    global window, canvas, paper, sheet
    global excelList
    con= pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, db="companyDB")
    cur = con.cursor()
    #########################
    for row in excelList[1:]:
        print(row[0],row[2],type(row[0]),type(row[2]))
        sql = "INSERT INTO supplies_2019_03TBL VALUES('" +str(row[0])+ "','" +str(row[1])+ "'," +str(row[2])+ "," +str(row[3])+ ",'" +str(row[4])+ "')"
        print(sql)
        cur.execute(sql)
    #########################
    messagebox.showinfo("complete","INSERT complete")
    #########################
    cur.close(); con.commit(); con.close()

#################################### CSV File ######################################

import csv
def openCSVFile() :
    global window, canvas, paper, sheet
    global csvList
    #########################
    filename = askopenfilename(parent=window, filetypes=(("CSV 파일", "*.csv"), ("모든 파일", "*.*")))
    if filename == "" or filename == None:
        return
    #########################
    loadCSV(filename)

def loadCSV(fname) :
    global window, canvas, paper, sheet
    global csvList
    #########################
    with open(fname, 'r', newline='') as filereader:
        csvReader = csv.reader(filereader) # CSV 전용으로 다시 열기
        header_list = next(csvReader)
        csvList.append(header_list)
        for  row_list in csvReader :
            csvList.append(row_list)
    #########################
    drawSheet(csvList)

def drawSheet(cList) :
    global window, canvas, paper, sheet
    if sheet != None :
        sheet.destroy()
    #########################
    sheet = ttk.Treeview(window)
    sheet.pack(side=LEFT, fill=Y)
    #########################
    sheet.column("#0", width=80); sheet.heading("#0", text=cList[0][0])
    sheet["columns"] = cList[0][1:]
    for colName in cList[0][1:]:
        sheet.column(colName, width=80); sheet.heading(colName, text=colName)
    #########################
    for row in cList[1:] :
        colList = []
        for col in row[1:]:
            colList.append(col)
        sheet.insert('', 'end', text=row[0], values=tuple(colList))

def saveCSVFile() :
    global window, canvas, paper, sheet
    global csvList
    saveFp = asksaveasfile(parent=window, mode='w',
                           defaultextension=".csv", filetypes=(("CSV파일", "*.csv"), ("모든파일", "*.*")))
    with open(saveFp.name, 'w', newline='') as filewriter :
        for row_list in csvList :
            row_str = ','.join(map(str, row_list))
            filewriter.writelines(row_str + '\n')

def saveCsvToDB_sales_2018_12():
    global window, canvas, paper, sheet
    global csvList
    con= pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, db="companyDB")
    cur = con.cursor()
    #########################
    for row in csvList[1:]:
        print(row[0],row[2],type(row[0]),type(row[2]))
        sql = "INSERT INTO sales_2018_12TBL VALUES('" +row[0]+ "','" +row[1]+ "'," +row[2]+ ",'" +row[3]+ "','" +row[4]+ "')"
        print(sql)
        cur.execute(sql)
    #########################
    messagebox.showinfo("complete","INSERT complete")
    #########################
    cur.close(); con.commit(); con.close()

def saveCsvToDB_sales_2019_01():
    global window, canvas, paper, sheet
    global csvList
    con= pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, db="companyDB")
    cur = con.cursor()
    #########################
    for row in csvList[1:]:
        print(row[0],row[2],type(row[0]),type(row[2]))
        sql = "INSERT INTO sales_2019_01TBL VALUES('" +row[0]+ "','" +row[1]+ "'," +row[2]+ ",'" +row[3]+ "','" +row[4]+ "')"
        print(sql)
        cur.execute(sql)
    #########################
    messagebox.showinfo("complete","INSERT complete")
    #########################
    cur.close(); con.commit(); con.close()

def saveCsvToDB_sales_2019_02():
    global window, canvas, paper, sheet
    global csvList
    con= pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, db="companyDB")
    cur = con.cursor()
    #########################
    for row in csvList[1:]:
        print(row[0],row[2],type(row[0]),type(row[2]))
        sql = "INSERT INTO sales_2019_02TBL VALUES('" +row[0]+ "','" +row[1]+ "'," +row[2]+ ",'" +row[3]+ "','" +row[4]+ "')"
        print(sql)
        cur.execute(sql)
    #########################
    messagebox.showinfo("complete","INSERT complete")
    #########################
    cur.close(); con.commit(); con.close()

def saveCsvToDB_sales_2019_03():
    global window, canvas, paper, sheet
    global csvList
    con= pymysql.connect(host=IP_ADDR, user=USER_NAME, password=USER_PASS, db="companyDB")
    cur = con.cursor()
    #########################
    for row in csvList[1:]:
        print(row[0],row[2],type(row[0]),type(row[2]))
        sql = "INSERT INTO sales_2019_03TBL VALUES('" +row[0]+ "','" +row[1]+ "'," +row[2]+ ",'" +row[3]+ "','" +row[4]+ "')"
        print(sql)
        cur.execute(sql)
    #########################
    messagebox.showinfo("complete","INSERT complete")
    #########################
    cur.close(); con.commit(); con.close()


def csvUp10() :
    global csvList
    #########################
    header_list = csvList[0] # cost 열의 위치를 찾기
    for i in range(len(header_list)) :
        header_list[i] = header_list[i].strip()
    try :
        pos = header_list.index('cost')
    except :
        messagebox.showinfo('message', 'cost column is not exist')
        return
    #########################
    for i in range(1, len(csvList)) :
        row = csvList[i]
        cost = row[pos]
        print(cost)
        cost = float(cost)
        print(cost)
        cost *= 1.1
        cost_str = "{0:.2f}".format(cost)
        csvList[i][pos] = cost_str
    #########################
    drawSheet(csvList)

def csvUp20() :
    global csvList
    #########################
    header_list = csvList[0] # cost 열의 위치를 찾기
    for i in range(len(header_list)) :
        header_list[i] = header_list[i].upper().strip()
    try :
        pos = header_list.index('COST')
    except :
        messagebox.showinfo('message', 'COST column is not exist')
        return
    #########################
    for i in range(1, len(csvList)) :
        row = csvList[i]
        cost = row[pos]
        cost = float(cost[1:])
        cost *= 1.2
        cost_str = "{0:.2f}".format(cost)
        csvList[i][pos] = cost_str
    #########################
    drawSheet(csvList)

################################## Data Analysis ###################################

def selectSalesTBL():
    global window
    global SalesSelectYear, SalesSelectMonth
    #########################
    topframe = Frame(window); topframe.pack(side=TOP)
    bottomFrame = Frame(window); bottomFrame.pack(side=BOTTOM, fill=BOTH, expand=1)
    #########################
    label1 = Label(topframe, width=7, text="year :"); label2 = Label(topframe, width=7, text="month :")
    label3 = Label(topframe, width=5, text=" | "); label4 = Label(topframe, width=15, text="Additional Option :")
    SalesSelectYear = Entry(topframe, width=5); SalesSelectMonth = Entry(topframe, width=5)
    SalesSelectBtn1 = Button(topframe, text='SELECT', command=loadTBL)
    SalesSelectBtn2 = Button(topframe, text='ScatterPlot', command=ScatterPlot)
    SalesSelectBtn3 = Button(topframe, text='HeatMap', command=HeatMap)
    SalesSelectBtn4 = Button(topframe, text='RegPlot', command=RegPlot)
    #########################
    label1.pack(side=LEFT, pady=5); SalesSelectYear.pack(side=LEFT, padx=10, pady=5)
    label2.pack(side=LEFT, pady=5); SalesSelectMonth.pack(side=LEFT, padx=10, pady=5)
    SalesSelectBtn1.pack(side=LEFT, padx=10, pady=5); label3.pack(side=LEFT, pady=5); label4.pack(side=LEFT, pady=5)
    SalesSelectBtn2.pack(side=LEFT, padx=10, pady=5); SalesSelectBtn3.pack(side=LEFT, padx=10, pady=5)
    SalesSelectBtn4.pack(side=LEFT, padx=10, pady=5)

from matplotlib.figure import Figure
from sqlalchemy import create_engine
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
def loadTBL():
    global SalesSelectYear, SalesSelectMonth
    global monthlyTBL,window
    engine = create_engine("mysql+pymysql://root:" + "1234" + "@192.168.111.141:3306/companyDB?charset=utf8", encoding='utf-8')
    conn = engine.connect
    con = pymysql.connect(host="192.168.111.141", port=3306, user="root", passwd="1234", db="companyDB", charset='utf8')
    #########################
    year = SalesSelectYear.get(); month= SalesSelectMonth.get()
    SQL = "SELECT * FROM sales_"+year+"_"+month+"TBL"
    salesTBL = pd.read_sql(SQL, con)
    SQL = "SELECT * FROM customerTBL"
    customerTBL = pd.read_sql(SQL, con)
    #########################
    salesTBL_invoice = salesTBL[["id", "invoice_num"]].groupby("id").count()
    salesTBL_cost = salesTBL[["id", "cost"]].groupby("id").sum()
    #########################
    salesTBL_invoice = pd.DataFrame(salesTBL_invoice)
    salesTBL_invoice["id"] = salesTBL_invoice.index
    salesTBL_invoice = salesTBL_invoice.reset_index(drop=True)
    salesTBL_cost = pd.DataFrame(salesTBL_cost)
    salesTBL_cost["id"] = salesTBL_cost.index
    salesTBL_cost = salesTBL_cost.reset_index(drop=True)
    #########################
    salesTBL_merge = pd.merge(salesTBL_invoice, salesTBL_cost)
    salesTBL_merge["count"] = salesTBL_merge["invoice_num"]
    salesTBL_merge["costSum"] = salesTBL_merge["cost"]
    salesTBL_merge = pd.DataFrame(salesTBL_merge, columns=["id", "count", "costSum"])
    #########################
    monthlyTBL = pd.merge(salesTBL_merge, customerTBL)
    nation_word = {'Korea': 'Kor', 'Canada': 'Can', 'America': 'Ame', 'France': 'Fra', 'China': 'Chi', 'Germany': 'Ger'}
    nation_number = {'Korea': 0, 'Canada': 1, 'America': 2, 'France': 3, 'China': 4, 'Germany': 5}
    monthlyTBL["nation_word"] = monthlyTBL["nation"].map(nation_word)
    monthlyTBL["nation_num"] = monthlyTBL["nation"].map(nation_number).astype(int)
    #########################
    con.close()
    #########################
    fig = Figure(figsize=(17, 4.5))
    axis1 = fig.add_subplot(1,2,1)
    axis2 = fig.add_subplot(1,2,2)
    #########################
    sns.countplot('nation_word', data=monthlyTBL, ax=axis1)
    axis1.set_title("Customer's nationality", fontsize=12)
    axis1.set_xlabel("nation", fontsize=10)
    axis1.set_ylabel("count", fontsize=10)
    #########################
    sns.kdeplot(monthlyTBL.age, shade=True, ax=axis2)
    axis2.set_title("Customer's Age", fontsize=12)
    axis2.set_xlabel("age range", fontsize=10)
    #########################
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.get_tk_widget().pack()
    canvas.draw()

def ScatterPlot():
    global monthlyTBL
    sns.catplot(x="count", y="costSum", hue="nation",col="gender", data=monthlyTBL)
    plt.show()

def HeatMap():
    global monthlyTBL
    corr = monthlyTBL.corr()
    mask = np.array(corr)
    mask[np.tril_indices_from(mask)] = False
    plt.figure(figsize=(8, 7))
    sns.heatmap(corr, mask=mask, square=True, cmap="YlGnBu")
    plt.show()

def RegPlot():
    global monthlyTBL
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    sns.regplot("costSum", "count", data=monthlyTBL, color="steelblue", label='count', marker='x', ax=ax1)
    sns.regplot("costSum", "age", data=monthlyTBL, color="darkorange", label='age', marker='x', ax=ax2)
    sns.regplot("count", "nation_num", data=monthlyTBL, color="g",label='nation_num', marker='x', ax=ax3)
    sns.regplot("nation_num", "age", data=monthlyTBL, color="firebrick", label='age', marker='x', ax=ax4)
    # fig.suptitle("Linear regression")
    # fig.set_size_inches(12, 7)
    plt.tight_layout()
    plt.show()

################################ Global Variable ##################################

window, canvas, paper = [None] * 3
sheet = None
VIEW_X, VIEW_Y = 516, 516
#########################
csvList,excelList = [],[]
#########################
filename, photo, cvPhoto  = [None] *3
inImage, outImage = [], []
inW, inH, outW, outH = [200] * 4
inImageR, inImageG, inImageB, outImageR, outImageG, outImageB = [],[],[],[],[],[]

#################################### GUI ##########################################

window = Tk(); window.title('Bigtata Integration Tool (Ver 0.06)')
window.geometry('800x500')
#########################
mainMenu = Menu(window)
window.config(menu=mainMenu)

################################# Status Bar ######################################

status = Label(window, text='info :', bd=1, relief=SUNKEN, anchor=W)
status.pack(side=BOTTOM, fill=X)

############################### Grayscale Image ####################################
Menu1 = Menu(mainMenu)
mainMenu.add_cascade(label="Image Processing", menu=Menu1)
#########################
Menu1_1 = Menu(Menu1)
Menu1.add_cascade(label="GrayScale Image", menu=Menu1_1)
Menu1_1_1 = Menu(Menu1_1)
Menu1_1.add_cascade(label="Open", menu=Menu1_1_1)
Menu1_1_1.add_command(label="Open File", command=openImage)
Menu1_1_1.add_separator()
Menu1_1_1.add_command(label="DB Open (Longblob)", command=loadDB)
Menu1_1_1.add_command(label="DB Open (Pixel)", command=PixelDBToRaw)
#########################
Menu1_1_2 = Menu(Menu1_1)
Menu1_1.add_cascade(label="Save", menu=Menu1_1_2)
Menu1_1_2.add_command(label="Save to File", command=saveFile)
Menu1_1_2.add_separator()
Menu1_1_2.add_command(label="Save to DB (Longblob)", command=None)
Menu1_1_2.add_command(label="Save to DB (Pixel)", command=rawToPixelDB)
Menu1_1_2.add_separator()
Menu1_1_2.add_command(label="Save to Excel (Pixel)", command=saveExcelImage)
#########################
Menu1_1_3 = Menu(Menu1_1)
Menu1_1.add_cascade(label="Image Processing", menu=Menu1_1_3)
Menu1_1_3.add_command(label="Brighter", command=addImage)
Menu1_1_3.add_command(label="Darker", command=None)
Menu1_1_3.add_command(label="Color Inversion", command=None)
Menu1_1_3.add_separator()
Menu1_1_3.add_command(label="Mirroring", command=None)
Menu1_1_3.add_command(label="Rotation", command=None)
Menu1_1_3.add_command(label="Zoom In", command=zoomInImage)
Menu1_1_3.add_command(label="Zoom Out", command=zoomOutImage)
Menu1_1_3.add_separator()
Menu1_1_3.add_command(label="Embossing(Mask)", command=embossingMaskGray)
Menu1_1_3.add_command(label="Blurring(Mask)", command=None)
Menu1_1_3.add_command(label="Sharpening(Mask)", command=None)
Menu1_1_3.add_separator()
Menu1_1_3.add_command(label="Embossing(pillow)", command=None)
Menu1_1_3.add_command(label="Blurring(pillow)", command=None)
Menu1_1_3.add_command(label="Sharpening(pillow)", command=None)
#########################
Menu1_1_4 = Menu(Menu1_1)
Menu1_1.add_cascade(label="Statistical Analysis", menu=Menu1_1_4)
Menu1_1_4.add_command(label="Image Information", command=averageRAW)
Menu1_1_4.add_command(label="histogram", command=histoRAW)
Menu1_1_4.add_command(label="matplotlib", command=matHistoRAW)

################################## Color Image #####################################

Menu1_2 = Menu(Menu1)
Menu1.add_cascade(label="Color Image", menu=Menu1_2)
#########################
Menu1_2_1 = Menu(Menu1_2)
Menu1_2.add_cascade(label="Open", menu=Menu1_2_1)
Menu1_2_1.add_command(label="Open File", command=openImageColor)
Menu1_2_1.add_separator()
Menu1_2_1.add_command(label="DB Open (Longblob)", command=None)
Menu1_2_1.add_command(label="DB Open (Pixel)", command=PixelDBToColor)
#########################
Menu1_2_2 = Menu(Menu1_2)
Menu1_2.add_cascade(label="Save", menu=Menu1_2_2)
Menu1_2_2.add_command(label="Save to File", command=saveImageColor)
Menu1_2_2.add_separator()
Menu1_2_2.add_command(label="Save to DB (Longblob)", command=None)
Menu1_2_2.add_command(label="Save to DB (Pixel)", command=colorToPixelDB)
#########################
Menu1_2_3 = Menu(Menu1_2)
Menu1_2.add_cascade(label="Image Processing", menu=Menu1_2_3)
Menu1_2_3.add_command(label="Brighter", command=None)
Menu1_2_3.add_command(label="Darker", command=None)
Menu1_2_3.add_command(label="Color Inversion", command=None)
Menu1_2_3.add_command(label="Black & White", command=bwImageColor)
Menu1_2_3.add_separator()
Menu1_2_3.add_command(label="Mirroring", command=mirrorImageColor)
Menu1_2_3.add_command(label="Rotation", command=None)
Menu1_2_3.add_command(label="Color Reverse", command=reverseImageColorNumPy)
Menu1_2_3.add_command(label="Zoom In", command=zoomInImageColor)
Menu1_2_3.add_command(label="Zoom Out", command=zoomOutImageColor)


Menu1_2_3.add_separator()
Menu1_2_3.add_command(label="Embossing(Mask)", command=None)
Menu1_2_3.add_command(label="Blurring(Mask)", command=None)
Menu1_2_3.add_command(label="Sharpening(Mask)", command=None)
Menu1_2_3.add_separator()
Menu1_2_3.add_command(label="Embossing(pillow)", command=embossingColorPillow)
Menu1_2_3.add_command(label="Blurring(pillow)", command=None)
Menu1_2_3.add_command(label="Sharpening(pillow)", command=None)
#########################
Menu1_2_4 = Menu(Menu1_2)
Menu1_2.add_cascade(label="Statistical Analysis", menu=Menu1_2_4)
Menu1_2_4.add_command(label="Image Information", command=None)
Menu1_2_4.add_command(label="histogram", command=None)
Menu1_2_4.add_command(label="matplotlib", command=matHistoColor)

################################## OpenCV Image ####################################

Menu1_3 = Menu(Menu1)
Menu1.add_cascade(label="OpenCV Image", menu=Menu1_3)
#########################
Menu1_3_1 = Menu(Menu1_3)
Menu1_3.add_cascade(label="Open", menu=Menu1_3_1)
Menu1_3_1.add_command(label="Open File", command=openOpenCV)
#########################
Menu1_3_2 = Menu(Menu1_3)
Menu1_3.add_cascade(label="Save", menu=Menu1_3_2)
Menu1_3_2.add_command(label="Save to File", command=None)
Menu1_3_2.add_separator()
Menu1_3_2.add_command(label="Save to DB (Longblob)", command=None)
Menu1_3_2.add_command(label="Save to DB (Pixel)", command=None)
#########################
Menu1_3_3 = Menu(Menu1_3)
Menu1_3.add_cascade(label="Image Processing", menu=Menu1_3_3)
Menu1_3_3.add_command(label="Brighter", command=None)
Menu1_3_3.add_command(label="Darker", command=None)
Menu1_3_3.add_command(label="Color Inversion", command=None)
Menu1_3_3.add_command(label="Black & White", command=None)
Menu1_3_3.add_separator()
Menu1_3_3.add_command(label="Mirroring", command=None)
Menu1_3_3.add_command(label="Rotation", command=None)
Menu1_3_3.add_command(label="확대&축소(포워딩)", command=None)
Menu1_3_3.add_command(label="확대&축소(백워딩)", command=None)
Menu1_3_3.add_separator()
Menu1_3_3.add_command(label="Embossing(openCV)", command=embossingCV2)
Menu1_3_3.add_command(label="Blurring(openCV)", command=None)
Menu1_3_3.add_command(label="Sharpening(openCV)", command=None)
Menu1_3_3.add_separator()
Menu1_3_3.add_command(label="Cartoon", command=None)
#########################
Menu1_3_4 = Menu(Menu1_3)
Menu1_3.add_cascade(label="Statistical Analysis", menu=Menu1_3_4)
Menu1_3_4.add_command(label="Image Information", command=None)
Menu1_3_4.add_command(label="histogram", command=None)
Menu1_3_4.add_command(label="matplotlib", command=None)
#########################
Menu1_3.add_separator()
Menu1_3_5 = Menu(Menu1_3)
Menu1_3.add_cascade(label="Machine-Learning", menu=Menu1_3_5)
Menu1_3_5.add_command(label="Face Recognition", command=faceCV2)
Menu1_3_5.add_command(label="Mask Sticker", command=maskCV2)
Menu1_3_5 = Menu(Menu1_3)
Menu1_3.add_cascade(label="Deep-Learning", menu=Menu1_3_5)
Menu1_3_5.add_command(label="Object Recognition", command=objectCV2)
Menu1_3_5.add_command(label="Video Recognition", command=videoCV2)

################################## Excel File ######################################

Menu2 = Menu(mainMenu)
mainMenu.add_cascade(label="Text Processing", menu=Menu2)
#########################
Menu2_1 = Menu(Menu2)
Menu2.add_cascade(label="Excel File", menu=Menu2_1)
Menu2_1.add_command(label="Open", command=openExcelFile)
Menu2_1.add_command(label="Save to File", command=saveExcelFile)
Menu2_1_3 = Menu(Menu2_1)
Menu2_1.add_cascade(label="Save to DB", menu=Menu2_1_3)
Menu2_1_3.add_command(label="sales_2019_01TBL", command=None)
Menu2_1_3.add_command(label="sales_2019_02TBL", command=None)
Menu2_1_3.add_separator()
Menu2_1_3.add_command(label="supplier_2018_12TBL", command=None)
Menu2_1_3.add_command(label="supplier_2019_01TBL", command=None)
Menu2_1_3.add_command(label="supplier_2019_02TBL", command=None)
Menu2_1_3.add_command(label="supplier_2019_03TBL", command=saveExcelToDB_sales_2019_03)
Menu2_1_3 = Menu(Menu2_1)
Menu2_1.add_cascade(label="Data Modification", menu=Menu2_1_3)
Menu2_1_3.add_command(label="a 10% increase in costs", command=None)
Menu2_1_3.add_command(label="a 20% increase in costs", command=None)
Menu2_1_3.add_command(label="a 20% increase in costs", command=None)

#################################### CSV File ######################################

Menu2_2 = Menu(Menu2)
Menu2.add_cascade(label="CSV File", menu=Menu2_2)
Menu2_2.add_command(label="Open", command=openCSVFile)
Menu2_2.add_command(label="Save to File", command=saveCSVFile)
Menu2_2_3 = Menu(Menu2_2)
Menu2_2.add_cascade(label="Save to DB", menu=Menu2_2_3)
Menu2_2_3.add_command(label="sales_2018_12TBL", command=saveCsvToDB_sales_2018_12)
Menu2_2_3.add_command(label="sales_2019_01TBL", command=saveCsvToDB_sales_2019_01)
Menu2_2_3.add_command(label="sales_2019_02TBL", command=saveCsvToDB_sales_2019_02)
Menu2_2_3.add_command(label="sales_2019_03TBL", command=saveCsvToDB_sales_2019_03)
Menu2_2_3.add_separator()
Menu2_2_3.add_command(label="supplier_2019_01TBL", command=None)
Menu2_2_3.add_command(label="supplier_2019_02TBL", command=None)
Menu2_2_4 = Menu(Menu2_2)
Menu2_2.add_cascade(label="Data Modification", menu=Menu2_2_4)
Menu2_2_4.add_command(label="a 10% increase in costs", command=csvUp10)
Menu2_2_4.add_command(label="a 20% increase in costs", command=csvUp20)
#################################### Information ###################################

Menu3 = Menu(mainMenu)
mainMenu.add_cascade(label="Database Management", menu=Menu3)
#########################
Menu3_1 = Menu(Menu3)
Menu3.add_cascade(label="Basic Information", menu=Menu3_1)
Menu3_1_1 = Menu(Menu3_1)
Menu3_1.add_cascade(label="customerTBL", menu=Menu3_1_1)
Menu3_1_1.add_command(label="Select Data", command=selectCustomerTBL)
Menu3_1_1.add_command(label="Insert Data", command=insertCustomerTBL)
Menu3_1_1.add_command(label="Delete Data", command=deleteCustomerTBL)
Menu3_1_2 = Menu(Menu3_1)
Menu3_1.add_cascade(label="productTBL", menu=Menu3_1_2)
Menu3_1_2.add_command(label="Select Data", command=None)
Menu3_1_2.add_command(label="Insert Data", command=None)
Menu3_1_2.add_command(label="Delete Data", command=None)
Menu3_1_3 = Menu(Menu3_1)
Menu3_1.add_cascade(label="supplierTBL", menu=Menu3_1_3)
Menu3_1_3.add_command(label="Select Data", command=None)
Menu3_1_3.add_command(label="Insert Data", command=None)
Menu3_1_3.add_command(label="Delete Data", command=None)

#################################### sales data ####################################

Menu3_2 = Menu(Menu3)
Menu3.add_cascade(label="Sales", menu=Menu3_2)
Menu3_2_1 = Menu(Menu3_2)
Menu3_2.add_cascade(label="sales_2018_12TBL", menu=Menu3_2_1)
Menu3_2_1.add_command(label="Select Data", command=None)
Menu3_2_1.add_command(label="Insert Data", command=None)
Menu3_2_1.add_command(label="Delete Data", command=None)
Menu3_2_2 = Menu(Menu3_2)
Menu3_2.add_cascade(label="sales_2019_01TBL", menu=Menu3_2_2)
Menu3_2_2.add_command(label="Select Data", command=None)
Menu3_2_2.add_command(label="Insert Data", command=None)
Menu3_2_2.add_command(label="Delete Data", command=None)
Menu3_2_3 = Menu(Menu3_2)
Menu3_2.add_cascade(label="sales_2019_02TBL", menu=Menu3_2_3)
Menu3_2_3.add_command(label="Select Data", command=None)
Menu3_2_3.add_command(label="Insert Data", command=None)
Menu3_2_3.add_command(label="Delete Data", command=None)
Menu3_2_4 = Menu(Menu3_2)
Menu3_2.add_cascade(label="sales_2019_03TBL", menu=Menu3_2_4)
Menu3_2_4.add_command(label="Select Data", command=selectSales03TBL)
Menu3_2_4.add_command(label="Insert Data", command=None)
Menu3_2_4.add_command(label="Delete Data", command=None)

################################## supplies data ###################################

Menu3_3 = Menu(Menu3)
Menu3.add_cascade(label="Supplies", menu=Menu3_3)
Menu3_3_1 = Menu(Menu3_3)
Menu3_3.add_cascade(label="supplies_2018_12TBL", menu=Menu3_3_1)
Menu3_3_1.add_command(label="Select Data", command=None)
Menu3_3_1.add_command(label="Insert Data", command=None)
Menu3_3_1.add_command(label="Delete Data", command=None)
Menu3_3_2 = Menu(Menu3_3)
Menu3_3.add_cascade(label="supplies_2019_01TBL", menu=Menu3_3_2)
Menu3_3_2.add_command(label="Select Data", command=None)
Menu3_3_2.add_command(label="Insert Data", command=None)
Menu3_3_2.add_command(label="Delete Data", command=None)
Menu3_3_3 = Menu(Menu3_3)
Menu3_3.add_cascade(label="supplies_2019_02TBL", menu=Menu3_3_3)
Menu3_3_3.add_command(label="Select Data", command=None)
Menu3_3_3.add_command(label="Insert Data", command=None)
Menu3_3_3.add_command(label="Delete Data", command=None)
Menu3_3_4 = Menu(Menu3_3)
Menu3_3.add_cascade(label="supplies_2019_03TBL", menu=Menu3_3_4)
Menu3_3_4.add_command(label="Select Data", command=selectSupplies03TBL)
Menu3_3_4.add_command(label="Insert Data", command=None)
Menu3_3_4.add_command(label="Delete Data", command=None)

#################################### image data ####################################

Menu3_4 = Menu(Menu3)
Menu3.add_cascade(label="Image Data", menu=Menu3_4)
Menu3_4_1 = Menu(Menu3_4)
Menu3_4.add_cascade(label="longblobImageTBL", menu=Menu3_4_1)
Menu3_4_1.add_command(label="Select Data", command=None)
Menu3_4_1.add_command(label="Insert Data", command=None)
Menu3_4_1.add_command(label="Delete Data", command=None)
Menu3_4_2 = Menu(Menu3_4)
Menu3_4.add_cascade(label="pixelImageTBL", menu=Menu3_4_2)
Menu3_4_2.add_command(label="Select Data", command=None)
Menu3_4_2.add_command(label="Insert Data", command=None)
Menu3_4_2.add_command(label="Delete Data", command=None)
#########################
Menu3.add_separator()
Menu3.add_command(label="Use SQL", command=readySQL)

################################## Data Analysis ###################################

Menu6 = Menu(mainMenu)
mainMenu.add_cascade(label="Data Analysis", menu=Menu6)
#########################
Menu6_1 = Menu(Menu6)
Menu6.add_cascade(label="Sales Data", menu=Menu6_1)
Menu6_1.add_command(label="Yearly Graph", command=None)
Menu6_1.add_command(label="Monthly Graph", command=None)
Menu6_1.add_command(label="Analysis Tool", command=selectSalesTBL)
Menu6_2 = Menu(Menu6)
Menu6.add_cascade(label="Supplies Data", menu=Menu6_2)
Menu6_2.add_command(label="Yearly Graph", command=None)
Menu6_2.add_command(label="Monthly Graph", command=None)
Menu6_2.add_command(label="Analysis Tool", command=None)

####################################################################################

window.mainloop()