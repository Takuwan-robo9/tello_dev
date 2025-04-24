# Telloドローン飛行実行記録

## 実行日時
2025年4月24日 午後5時27分

## 実行環境
- スクリプト: multi_tello_test_py3.py
- コマンドファイル: test_tello_2.txt

## 検出されたドローン
1. IP: 192.168.11.8, SN: 0TQ3GBG00SS131, バッテリー: 94%
2. IP: 192.168.11.10, SN: 0TQZK8PED02YFL, バッテリー: 94%

## 実行コマンドシーケンス
1. `scan 2` - 2台のTelloドローンをスキャンして接続
2. `battery_check 20` - バッテリーが20%以上あるか確認
3. `correct_ip` - IPアドレスを修正
4. `1=0TQZK8PED02YFL` と `2=0TQ3GBG00SS131` - ドローンのシリアル番号を指定
5. `*>mon` - すべてのドローンをモニターモードに設定
6. `*>takeoff` - すべてのドローンを離陸させる
7. `sync 15` - 15秒間同期待機
8. `1>go 50 0 80 60` と `2>go -50 0 80 60` - ドローン1は右に、ドローン2は左に移動
9. `sync 15` - 15秒間同期待機
10. `*>land` - すべてのドローンを着陸させる

## 実行結果
すべてのコマンドが正常に実行され、エラーは発生しませんでした。ドローンは正常に飛行し、指示通りに動作しました。

## 注意点
- formation_setup_tello2.pyスクリプトは、Telloドローンを初めて設定する場合にのみ必要です。
- keyboard_formation_control.pyは開発中のファイルで、現時点では使用しないでください。
- multi_tello_test_py3.pyを使用する場合は、コマンドファイル（例：test_tello_2.txt）を指定する必要があります。

## 実行コマンド
```bash
cd Multi-Tello-Formation/src && python3 multi_tello_test_py3.py ../cmd/test_tello_2.txt
```
