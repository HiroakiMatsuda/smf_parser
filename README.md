smf_parser
======================
smf_parserはSMF(Standard MIDI File)形式の音楽データの構文解釈を行うPython Scriptです．     

動作確認環境
------
Python:  
2.6.6  

pySerial:  
2.6(2003-2010)まで対応  

OS:  
Windows 8/8.1 64bit / 32bit  

SMFの対応形式:   
フォーマットは0または1に対応しています．    
デルタタイムは絶対時間には対応していません． 

更新履歴:  
------

ファイル構成
------
smf\_parser  
│― data   
│― midifile  
│　　　│― simpletest.mid  
│    
│― smf\_parser.py  

* data  
解析した結果を保存するフォルダです．デフォルトでは空です．    

* midifile  
テスト用のMIDIファイルが格納されています．  

* smf\_parser.py  
モジュール本体です．    

＊ 本モジュールにおいてユーザーが操作すると想定しているファイルのみ説明しています．  
 
使い方
------
###音楽ファイルを解析して保存してみる###
コンソールからsmf_parser.pyを以下のようにコマンドで起動します． 

```python smf\_parser ./midifile/simpletest.mid ./data/simpletest.txt```

以上のコマンドで，simpletest.midを解析し，その解析結果がsimpletest.txtに保存されます．  
 
ライセンス
----------
Copyright &copy; 2014 Hiroaki Matsuda  
Licensed under the [Apache License, Version 2.0][Apache]  
Distributed under the [MIT License][mit].  
Dual licensed under the [MIT license][MIT] and [GPL license][GPL].  
 
[Apache]: http://www.apache.org/licenses/LICENSE-2.0
[MIT]: http://www.opensource.org/licenses/mit-license.php
[GPL]: http://www.gnu.org/licenses/gpl.html