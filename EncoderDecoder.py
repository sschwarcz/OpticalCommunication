import cv2
import numpy as np
from PIL import Image


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def remove_sufix(text, prefix):
    if text.endswith(prefix):
        text = text[:-(len(prefix))]
    return text
def text_toBinary(str):
    binaryMessage=''
    for i in range(len(str)):
        binaryMessage = binaryMessage + format(ord(str[i]),'08b')

    return binaryMessage

def image_toBinary(img):
    w , h ,pix = len(img[0]) , len(img),len(img[0][0])
    binary_image=""
    for i in range(h):
        for j in range(w):
            for z in range(pix):
                binary_image =binary_image+ format(img[i][j][z] , '08b')


    return(binary_image)


def binary_toImage(binary_string):
    charAT =""
    rValue=0
    gValue=0
    bValue=0
    count=0
    countz=0
    counth=0
    countw=0
    img1=np.zeros((256,256,3),dtype=np.uint8)#change to originalWeihigh
    for i in range(len(binary_string)):

        charAT =charAT+ binary_string[i]
        count=count+1
        if count==8:
            if countz==0:
                rValue=charAT
                rValue=int(rValue, 2)
                img1[counth][countw][countz]=rValue
                charAT=""
                countz=1
            elif countz==1:
                gValue = charAT
                gValue = int(gValue , 2)
                img1[counth][countw][countz] = gValue
                charAT = ""
                countz = 2
            elif countz==2:
                bValue = charAT
                bValue = int(bValue , 2)
                img1[counth][countw][countz] = bValue
                charAT = ""
                countz=3
            count=0

        if countz==3:
            countz=0
            countw=countw+1

        if countw==256:#change to Wei
            countw=0
            counth=counth+1
            if counth==256:#change to hight
                break

    # img = Image.fromarray(img1 , 'RGB')
    #
    # img.show()
    return img1


def binary_toText(binary_string):
    binary_string = remove_prefix(binary_string , '1')
    binary_string = remove_sufix(binary_string , '10000000000')
    charAT=""
    final_string=""
    count=0
    for i in range(len(binary_string)):
        charAT = charAT + binary_string[i]

        count = count + 1
        if count == 8:
            final_string = final_string + chr(int(charAT , 2))
            charAT = ""
            count = 0



    return final_string





# image = cv2.imread(r"C:\Users\Dell\Desktop\espace\photos\dix.png")
# cv2.imshow("poolpl",image)
# cv2.waitKey(0)
# bin=image_toBinary(image)
# print(bin)
# unziped_image =binary_toImage(bin)
#
#
# cv2.imshow('w',unziped_image)
# cv2.waitKey(0)

# image =Image.fromarray(image, 'RGB')

# image.show()
# unziped_image=Image.fromarray(unziped_image, 'RGB')
# unziped_image.show()





# char='01111111'
# str= ""
# print(text_toBinary(str))
# print(binary_toText("1010000100110111101100001011110100010000001101001011100110010000001110100011010000110010100100000011010110110100101101110011001110010000110000000000"))

# print(binary_toText("01001000011001010110110001101100011011110010000001000101011011000110000100100101001001010010010100100101001001010110010000100001"))

