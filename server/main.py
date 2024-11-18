import cv2
import numpy as np
import mediapipe as mp
import math
from image_segmentation.img_seg import ImageSegmentation
from image_segmentation.metrics import iou,dice_coef,dice_loss
from pathlib import Path
#from tf_bodypix.api import download_model, load_model, BodyPixModelPaths

#Image Preprocessing
def preProcessing(path):
    image = cv2.imread(path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resized_image = cv2.resize(image, (368, 716))
    return path

#Image Segmentation
def imageSegmentation1(path):
    segmentation = ImageSegmentation(iou,dice_coef,dice_loss)
    segmented_img_path = segmentation.segmentation(path)
    return segmented_img_path

#Pixel Estimation
def pixelEstimation(masked_image_path,height_inp):
    masked_image = cv2.imread(masked_image_path)
    topPoint = 0
    bottomPoint = 0
    break_out_flag = False
    h, w, _ = masked_image.shape
    for row in range(len(masked_image)):
        for col in range(len(masked_image[0])):
            if(masked_image[row][col][0] > 0):
                topPoint = row
                break_out_flag = True
                break
        if break_out_flag:
            break
    break_out_flag=False
    for row in range(len(masked_image)-1,-1,-1):
        for col in range(len(masked_image[0])-1,-1,-1):
            if(masked_image[row][col][0] > 0):
                bottomPoint = row
                break_out_flag = True
                break
        if break_out_flag:
            break
    pixel = height_inp / (bottomPoint-topPoint)
    #print("pixel_in_cm",pixel)
    return pixel

#Pose Estimation for linear measurements
def poseEstimation(masked_image_path,height_inp,pixel_1):
    masked_image = cv2.imread(masked_image_path)
    mpDraw = mp.solutions.drawing_utils
    mpPose = mp.solutions.pose
    pose = mpPose.Pose() 
    img = masked_image
    rgbIMG = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(img)
    topPointx = 0
    bottomPointx = 0
    topPointY = 0
    bottomPointY = 0
    left_x = 0
    right_x = 0
    left_y = 0
    right_y = 0
    down_x = 0
    down_y = 0
    arm_x = 0
    arm_y = 0
    s_len = 0
    if results.pose_landmarks:
        mpDraw.draw_landmarks(rgbIMG, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
        for id, lm in enumerate(results.pose_landmarks.landmark):
            h, w, _ = rgbIMG.shape
            cx, cy = int(lm.x * w), int(lm.y * h)

            if(id==12):
                right_x=int(lm.x*w)
                right_y=int(lm.y*h)
                for i in range(0,w):
                    if(max(masked_image[right_y][i])!=0):
                        shoulder_right1=i
                        break
                for i in range(w-1,-1,-1):
                    if(max(masked_image[right_y][i])!=0):
                        shoulder_left1=i
                        break  

                for i in range(right_y,-1,-1):
                    if(max(masked_image[i][right_x])==0):
                        s_len = i+1
                        break   
                cv2.line(rgbIMG,(shoulder_right1, right_y) , (shoulder_left1,right_y), (255,0,0),5)
                cv2.line(rgbIMG,(right_x, s_len) , (right_x,right_y), (255,0,0),5) 

                
            if(id==11):

                left_x=int(lm.x*w)
                left_y=int(lm.y*h)

                for i in range(w-1,-1,-1):
                
                    if(max(masked_image[left_y][i])!=0):
                        shoulder_left2=i
                        break
                for i in range(0,w):
                
                    if(max(masked_image[left_y][i])!=0):
                        shoulder_right2=i
                        break
  
                cv2.line(rgbIMG,(shoulder_right2, left_y) , (shoulder_left2,left_y), (255,255,0),5)
            
            if(id==0):
                topPointx = cx
                topPointY = cy
            if(id==32):
                bottomPointx = cx
                bottomPointY = cy
            if(id==12):
                right_x= cx
                right_y= cy
            if(id==11):
                left_x= cx
                left_y= cy
            if(id==24):
                down_x= cx
                down_y= cy
                for i in range(down_y,-1,-1):
                    if(max(masked_image[i][down_x])==0):
                        s_len = i+1
                        break
            if(id==16):
                arm_x= cx
                arm_y= cy

            cv2.circle(rgbIMG, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
 
                
        pixel = height_inp / (math.sqrt((bottomPointx-topPointx)**2+(bottomPointY-topPointY)**2))
        print("pixel_in_cm",pixel)
        shoulderlen=math.sqrt((shoulder_left2-shoulder_right1)**2+(left_y-right_y)**2)*pixel_1
        print("shoulderlen",shoulderlen)
        shirtlen=math.sqrt((down_y-s_len)**2)*pixel
        print("shirtlen",shirtlen+5)
        pantlen=math.sqrt((bottomPointY-down_y)**2+(bottomPointx-down_x)**2)*pixel
        print("pantlen",pantlen)
        armlen = math.sqrt((right_x-arm_x)**2+(right_y-arm_y)**2)*pixel
        print("armlen",armlen)
    
    
    fileName = Path(masked_image_path).stem
    return (pixel,shoulderlen,shirtlen+5,pantlen,armlen,masked_image_path)

def main(img_path,height_inp):
    preprocessed_img_path = preProcessing(img_path)
    masked_img_path1 = imageSegmentation1(preprocessed_img_path)
    pixel = pixelEstimation(masked_img_path1,height_inp)
    return poseEstimation(masked_img_path1,height_inp,pixel)


