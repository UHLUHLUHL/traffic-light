#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HSV Calibration Tool for Raspbot
목적: 실시간으로 카메라 영상을 보면서 HSV(색상, 채도, 밝기) 임계값을 조절하여
      원하는 색상을 정확하게 추출해내는 최적의 값을 찾기 위한 도구입니다.

사용법:
1. 트랙바를 움직여서 원하는 물체(신호등, 표지판)만 하얗게 보이도록 만드세요.
2. 터미널에 출력되는 'Lower'와 'Upper' 값을 복사하여 코드에 적용하세요.

Keyboard:
  'q' or 'ESC': 종료
  's': 현재 설정값 저장 (print)
"""

import cv2
import numpy as np
import time

def nothing(x):
    pass

def main():
    # 카메라 초기화
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("⚠️ Camera index 0 failed. Trying index -1...")
        cap = cv2.VideoCapture(-1)
        if not cap.isOpened():
            print("❌ Cannot open camera")
            return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cap.set(cv2.CAP_PROP_BRIGHTNESS, 32)
    # cap.set(cv2.CAP_PROP_EXPOSURE, 100) # 필요 시 주석 해제

    # 윈도우 생성
    cv2.namedWindow("Trackbars", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Trackbars", 640, 300)
    
    cv2.namedWindow("Original", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Mask", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Result", cv2.WINDOW_NORMAL)

    # 트랙바 생성 (초기값: 빨간색 감지용)
    # H: 0~179, S: 0~255, V: 0~255
    cv2.createTrackbar("L - H", "Trackbars", 0, 179, nothing)
    cv2.createTrackbar("L - S", "Trackbars", 100, 255, nothing)
    cv2.createTrackbar("L - V", "Trackbars", 100, 255, nothing)
    cv2.createTrackbar("U - H", "Trackbars", 10, 179, nothing)
    cv2.createTrackbar("U - S", "Trackbars", 255, 255, nothing)
    cv2.createTrackbar("U - V", "Trackbars", 255, 255, nothing)

    print("✅ HSV Calibration Tool Started")
    print("-----------------------------------")
    print("Adjust trackbars to isolate the desired color.")
    print("Press 'q' to quit.")
    print("-----------------------------------")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.resize(frame, (320, 240))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 트랙바 값 읽기
        l_h = cv2.getTrackbarPos("L - H", "Trackbars")
        l_s = cv2.getTrackbarPos("L - S", "Trackbars")
        l_v = cv2.getTrackbarPos("L - V", "Trackbars")
        u_h = cv2.getTrackbarPos("U - H", "Trackbars")
        u_s = cv2.getTrackbarPos("U - S", "Trackbars")
        u_v = cv2.getTrackbarPos("U - V", "Trackbars")

        lower_range = np.array([l_h, l_s, l_v])
        upper_range = np.array([u_h, u_s, u_v])

        # 마스크 생성
        mask = cv2.inRange(hsv, lower_range, upper_range)
        
        # 결과 합치기 (Bitwise AND)
        result = cv2.bitwise_and(frame, frame, mask=mask)

        # 정보 표시
        info_text = f"H:{l_h}~{u_h} S:{l_s}~{u_s} V:{l_v}~{u_v}"
        cv2.putText(result, info_text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        # 화면 출력
        cv2.imshow("Original", frame)
        cv2.imshow("Mask", mask)
        cv2.imshow("Result", result)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == 27:
            print("\n" + "="*40)
            print("🎨 COPY THIS CODE TO YOUR SCRIPT:")
            print("="*40)
            print(f"LOWER_VAL = np.array([{l_h}, {l_s}, {l_v}])")
            print(f"UPPER_VAL = np.array([{u_h}, {u_s}, {u_v}])")
            print("="*40 + "\n")
            break
        elif key == ord("s"):
            print(f"\n[Saved Snapshot] 📸")
            print(f"LOWER_VAL = np.array([{l_h}, {l_s}, {l_v}])")
            print(f"UPPER_VAL = np.array([{u_h}, {u_s}, {u_v}])")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
