# Annual Report Workbench

涓€涓敤浜庡勾鎶ュ叕鍛婃姄鍙栥€丳DF 涓嬭浇鍜屾枃鏈彁鍙栫殑妗岄潰宸ュ叿銆?

## 椤圭洰绠€浠?

杩欐槸涓€涓熀浜?Python + Vue + pywebview 鐨勬闈㈠簲鐢紝閫傚悎鎵归噺澶勭悊骞存姤鐩稿叧鏁版嵁锛屽苟鍦ㄧ晫闈腑鏌ョ湅杩涘害銆佹棩蹇楀拰鍘嗗彶浠诲姟銆?

![Annual Report Workbench 棰勮鍥綸(assets/gpt-image-4.png)

搴旂敤闈㈠悜骞存姤鏁版嵁澶勭悊鍦烘櫙锛屾彁渚涗粠鍏憡閾炬帴鎶撳彇銆丳DF 涓嬭浇鍒版枃鏈彁鍙栫殑瀹屾暣澶勭悊閾捐矾銆傜浉姣斿懡浠よ鑴氭湰锛屽畠鏇撮€傚悎闇€瑕佹壒閲忚繍琛屻€佹煡鐪嬭繃绋嬬姸鎬併€佷繚鐣欏巻鍙茶褰曞拰鍙嶅璋冨弬鐨勬闈㈠伐浣滄祦銆?

## 涓昏鍔熻兘

- 鍏憡閾炬帴鎶撳彇
- PDF 鎵归噺涓嬭浇
- PDF 鏂囨湰鎻愬彇
- 鍗曢樁娈佃繍琛屽拰鍏ㄦ祦绋嬩覆鑱?
- 浠诲姟鏆傚仠銆佺户缁拰缁堟
- 瀹炴椂鏃ュ織銆佽繘搴﹀拰鍥捐〃灞曠ず
- 鍘嗗彶浠诲姟璁板綍鍜岄厤缃悓姝?

## 蹇€熷紑濮?

1. 瀹夎 Python 渚濊禆锛歚pip install -r requirements.txt`
2. 瀹夎鍓嶇渚濊禆锛歚cd webui && npm install`
3. 鏋勫缓鍓嶇锛歚npm run build`
4. 绫诲瀷妫€鏌ワ細`npm run typecheck`
5. 鍚姩妗岄潰绋嬪簭锛歚python -m webview_console`

## 甯哥敤鍛戒护

- 鍚屾鐗堟湰鍒版洿鏂版竻鍗曪細`python .\scripts\sync_update_manifest.py 1.0.2`
- 鏋勫缓 GUI锛歚powershell -ExecutionPolicy Bypass -File .\scripts\build_gui.ps1 -Mode onedir`
- 鏋勫缓瀹夎鍖咃細`powershell -ExecutionPolicy Bypass -File .\scripts\build_installer.ps1 -Mode onedir`
- 杩愯娴嬭瘯锛歚python -m unittest .\tests\test_release_metadata.py`

## 浠撳簱鍦板潃

- GitHub: https://github.com/Little-pig-create/AnnualReportWorkbench
- Gitee: https://gitee.com/xiaozhusir/AnnualReportWorkbench

