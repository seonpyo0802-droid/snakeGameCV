import mediapipe as mp
import random as r
import math as m
import numpy as np
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import time

cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

pTime = 0
run = True

detector = HandDetector(detectionCon= 0.7, maxHands= 1)

class SnakeGameClass:
    def __init__(self, pathFood):
        self.points = []
        self.lengths = []
        self.currentLength = 0
        self.allowedLength = 150
        self.previousHead = 0,0

        self.imgFood = cv2.imread(pathFood, cv2.IMREAD_UNCHANGED)
        self.hfood ,self.wfood, _ = self.imgFood.shape
        self.foodPoint = 0,0
        self.randomFoodLocation()

        self.score = 0
        self.gameOver = False
        # Change Donut Location
    def randomFoodLocation(self):
        self.foodPoint = r.randint(100,1180), r.randint(100,620)

        # Main Update Loop
    def update(self, imgMain, currentHead):
        # Game Over Check
        if self.gameOver:
            cvzone.putTextRect(imgMain, "Game Over", [300,400],scale=7, thickness=5, offset=20)
            cvzone.putTextRect(imgMain, f'Your score: {self.score}',[300,550],scale=7,thickness=5,offset=20)
        else:
            px,py = self.previousHead
            cx,cy = currentHead

            self.points.append([cx,cy])
            distance = m.hypot(cx-px,cy-py)
            self.lengths.append(distance)
            self.currentLength += distance
            self.previousHead = cx,cy

            #Length Reduction
            if self.currentLength > self.allowedLength:
                for i, length in enumerate(self.lengths):
                    self.currentLength -= length
                    self.lengths.pop(i)
                    self.points.pop(i)
                    if self.currentLength < self.allowedLength:
                        break
            
            #Check for Eating Donut
            rx, ry = self.foodPoint
            if rx - self.wfood //2 < cx < rx + self.wfood //2 and \
                ry - self.hfood // 2 < cy < ry + self.hfood:
                self.randomFoodLocation()
                self.allowedLength += 50
                self.score += 1

            # Draw Snake
            if self.points:
                for i, point in enumerate(self.points):
                    if i!=0:
                        cv2.line(imgMain,self.points[i-1], self.points[i],(0,0,255),20)
                cv2.circle(imgMain, self.points[-1],20,(0,255,0),cv2.FILLED)
                        
            rx, ry = self.foodPoint

            # Draw Food
            imgMain = cvzone.overlayPNG(imgMain, self.imgFood, 
                                        (rx - self.wfood // 2,
                                        ry - self.hfood // 2))
            cvzone.putTextRect(imgMain, f'Score: {self.score}',[50,80],
                            scale=3, thickness=3,offset=10)
            
            # Check for Collision
            pts = np.array(self.points[:-2], np.int32)
            pts = pts.reshape(-1,1,2)
            cv2.polylines(imgMain,[pts], False, (0,255,0),3)
            minDist = cv2.pointPolygonTest(pts, (cx,cy), True)
            
            if -1<=minDist<=1:
                print('hit')
                self.gameOver=True
        return imgMain


game = SnakeGameClass("CD/image/Donut.png")

while run:
    success, img = cap.read()
    img = cv2.flip(img,1)
    hands, img = detector.findHands(img, flipType = False)

    if hands:
        lmlist = hands[0]['lmList']
        pointIndex = lmlist[8][0:2]
        img = game.update(img, pointIndex)

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img,f'FPS:{int(fps)}',(20,70),cv2.FONT_HERSHEY_PLAIN,3,(0,255,0),3)
    cv2.imshow("Setup", img)
    key = cv2.waitKey(1)

    if key == ord('q'):
        run = False
    
    if key==ord('r') and game.gameOver==True:
        game.points=[]
        game.lengths=[]
        game.currentLength=0
        game.allowedLength=150
        game.previousHead=0,0
        game.score=0
        game.gameOver = False  
        game.randomFoodLocation()