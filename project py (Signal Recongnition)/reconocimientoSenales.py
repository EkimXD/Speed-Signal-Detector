import cv2
from sklearn.externals import joblib
from skimage.feature import hog
import numpy as np
import serial, time

arduino = serial.Serial('COM5', 9600)
#cargar modelos xml y pkl
clf = joblib.load("digits_cls.pkl")
senalM = cv2.CascadeClassifier('./lbpCascade.xml')
nuM=0
nU=0
def detNum(imagen):
    ban =False
    numero=0
    tamano=0
    contador=0
    contador1=0
    im_gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    im_gray = cv2.GaussianBlur(im_gray, (5, 5), 0)
    ret, im_th = cv2.threshold(im_gray, 90, 255, cv2.THRESH_BINARY_INV)
    ctrs, hier = cv2.findContours(im_th.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for ctr in ctrs:#aumentado
        if cv2.contourArea(ctr) > tamano:
            tamano = cv2.contourArea(ctr)
            contador1=contador
        else:
            contador += 1  # aumentado
    #cv2.drawContours(imagen, ctrs[contador1], -1, (0, 0, 255), 2, cv2.LINE_AA)
    try:
        rects = [cv2.boundingRect(ctr) for ctr in ctrs]
        # for rect in rects:
        rect = rects[contador1]  # cambio x for
        #rect=ctrs[contador1]
        #cv2.drawContours(imagen, rect, -1, (0, 0, 255), 2, cv2.LINE_AA)
        # Draw the rectangles
        leng = int(rect[3] * 1.6)
        cv2.rectangle(imagen, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), (0, 255, 0), 3)
        # Make the rectangular region around the digit
        pt1 = int(rect[1] + rect[3] // 2 - leng // 2)
        pt2 = int(rect[0] + rect[2] // 2 - leng // 2)
        roi = im_th[pt1:pt1 + leng, pt2:pt2 + leng]
        # Resize the image
        roi = cv2.resize(roi, (28, 28), interpolation=cv2.INTER_AREA)
        roi = cv2.dilate(roi, (3, 3))
        # Calculate the HOG features
        roi_hog_fd = hog(roi, orientations=9, pixels_per_cell=(14, 14), cells_per_block=(1, 1), visualise=False)
        nbr = clf.predict(np.array([roi_hog_fd], 'float64'))
        cv2.putText(imagen, str(int(nbr[0])), (rect[0], rect[1]), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 255, 255), 3)
        numero = int(nbr[0])
        ban = True
    except:
        ban=False
    return numero,ban


cap=cv2.VideoCapture(0)
nU=0
while(True):
    ret, img  = cap.read()
    bandera=False
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces = senalM.detectMultiScale(gray,1.3,2)
    try:
        (x, y, w, h) = faces[0]
        #if cv2.contourArea((x, y, w, h)) > 300:
        #    continue
            # print(y, y+h, x, x+w)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)
        img = img[y+ int(h/6):y + h -int(h/6) , x+int(w/6):x + int(w/2)+1]
        #img = img[y + int(h / 5):y + h - int(h / 5), x + int(w / 5):x + int(w-w / 5) ]
        cv2.imshow("", img)
        #cv2.waitKey()
        bandera=True
    except:
        bandera=False

    if bandera:
        nuM, bandera=detNum(img)
        #print(nuM)
        #cv2.imwrite("ima.jpg",img)
        #cv2.imshow("", img)
        if bandera:
            nU=nuM
            #check output
    rawString = arduino.readline()
    lala = str(rawString)
    lala = lala.replace("\\r\\n'", "").replace("b'", "")
    lol= float(lala)
    if lol>float(nU):
        print("maxima exedida",lol,nU)
    else:
        print("velocidad normal", lol, nU)
    #salir
    if cv2.waitKey(30) & 0xFF == ord('s'):
        break


time.sleep(2)
#rawString = arduino.readline()

arduino.close()
cap.release()
cv2.destroyAllWindows()
