Air_Hockey_full.ttt 與 Air_Hockey.ttt
差異為完整版與簡化版

hsv_test.py 是用來測試HSV過濾值域的範圍

ColorRecognition.py 與 ColorRecognition_multi.py
差異只有在 track_yellow_object
為了辨識球桌四個角落的黃色標記點來矯正影像
所以改寫為可以辨識多個形心位置

main_flask.py 中有用到CoppeliaSim API中雙預設port
分別為 19997 與19999
所以不管模擬有無執行都可以藉由 19997 或 19999開始執行
設定需要到CoppeliaSim安裝資料夾中的remoteApiConnections.txt
新增以下三行

portIndex2_port             = 19999
portIndex2_debug            = false
portIndex2_syncSimTrigger   = true

模擬檔案路徑 scene_path 需對應到模擬檔案 Air_Hockey_full.ttt
flask_ip 目前設為 140.130.17.108

及時串流運用Flask的 Response 於 main_flask.py 144 行 來快速取代圖像達到影像之效果
網頁控制 運用 jquery.min.js 擷取對網頁上按鈕之操作並回傳python 執行操作對應之指令

所以整體架構如下
運用CoppeliaSim Remote API 擷取影像 CoppeliaSim 攝影機之影像
經由Python處理 Flask 建立網頁並顯示及時影像
再由網頁之 JavaScript的jquery 接收網頁之命令並透過python執行CoppeliaSim Remote API 來達到控制模擬