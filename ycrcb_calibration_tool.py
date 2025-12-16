#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YCrCb Calibration Tool for Raspbot (Blown-out Light Detection)
목적: 빛이 너무 강해서 하얗게 보이는(백화현상) 빨간색 LED를 감지하기 위함.
      HSV보다 YCrCb 색공간이 '붉은 기운'을 감지하는 데 훨씬 유리합니다.

사용법:
1. 트랙바를 움직여서 하얗게 날아간 신호등 불빛을 잡아보세요.
2. 특히 'Cr' (Red-difference) 값을 조절하는 것이 핵심입니다.

Keyboard:
  'q' or 'ESC': 종료
  's': 현재 설정값 저장 (print)
"""

import cv2
import numpy as np

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
    cap.set(cv2.CAP_PROP_BRIGHTNESS, 32) # 너무 밝으면 낮추는 것도 방법

    # 윈도우 생성
    cv2.namedWindow("Trackbars", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Trackbars", 640, 300)
    
    cv2.namedWindow("Original", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Mask", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Result", cv2.WINDOW_NORMAL)

    # 트랙바 생성 (Y:밝기, Cr:붉은정도, Cb:푸른정도)
    # 초기값: Red detection 용 (Cr이 높아야 함)
    cv2.createTrackbar("L - Y", "Trackbars", 0, 255, nothing)
    cv2.createTrackbar("L - Cr", "Trackbars", 140, 255, nothing) # 140이상 (붉은기)
    cv2.createTrackbar("L - Cb", "Trackbars", 0, 255, nothing)
    
    cv2.createTrackbar("U - Y", "Trackbars", 255, 255, nothing)
    cv2.createTrackbar("U - Cr", "Trackbars", 255, 255, nothing)
    cv2.createTrackbar("U - Cb", "Trackbars", 255, 255, nothing)

    print("-----------------------------------")
    print("YCrCb Calibration Tool Started")
    print("Adjust 'Cr' (Redness) is most important!")
    print("CLICK on the camera view to see YCrCb values!")
    print("-----------------------------------")

    # 마우스 클릭 이벤트 함수
    def pick_color(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            pixel = frame[y, x]
            # BGR to YCrCb 변환
            pixel_ycrcb = cv2.cvtColor(np.uint8([[pixel]]), cv2.COLOR_BGR2YCrCb)[0][0]
            print(f"🎯 Clicked Pixel (x={x}, y={y}): YCrCb[{pixel_ycrcb[0]}, {pixel_ycrcb[1]}, {pixel_ycrcb[2]}]")
            print(f"   -> [Y=Bright, Cr=Red, Cb=Blue]")
            print(f"   -> For RED light, look for High 'Cr' value even if it looks white!")

    cv2.setMouseCallback("Original", pick_color)

    while True:
        global frame 
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.resize(frame, (320, 240))
        # BGR -> YCrCb 변환
        ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)

        # 트랙바 값 읽기
        l_y = cv2.getTrackbarPos("L - Y", "Trackbars")
        l_cr = cv2.getTrackbarPos("L - Cr", "Trackbars")
        l_cb = cv2.getTrackbarPos("L - Cb", "Trackbars")
        u_y = cv2.getTrackbarPos("U - Y", "Trackbars")
        u_cr = cv2.getTrackbarPos("U - Cr", "Trackbars")
        u_cb = cv2.getTrackbarPos("U - Cb", "Trackbars")

        lower_range = np.array([l_y, l_cr, l_cb])
        upper_range = np.array([u_y, u_cr, u_cb])

        # 마스크 생성
        mask = cv2.inRange(ycrcb, lower_range, upper_range)
        
        # 결과 합치기
        result = cv2.bitwise_and(frame, frame, mask=mask)

        # 정보 표시
        info_text = f"Y:{l_y}~{u_y} Cr:{l_cr}~{u_cr} Cb:{l_cb}~{u_cb}"
        cv2.putText(result, info_text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        cv2.imshow("Original", frame)
        cv2.imshow("Mask", mask)
        cv2.imshow("Result", result)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == 27:
            print("\n" + "="*40)
            print("🎨 COPY THIS (YCrCb):")
            print(f"LOWER_YCRCB = np.array([{l_y}, {l_cr}, {l_cb}])")
            print(f"UPPER_YCRCB = np.array([{u_y}, {u_cr}, {u_cb}])")
            print("="*40 + "\n")
            break
        elif key == ord("s"):
            print(f"\n[Saved] Lower: [{l_y}, {l_cr}, {l_cb}], Upper: [{u_y}, {u_cr}, {u_cb}]")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
