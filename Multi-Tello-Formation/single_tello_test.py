from djitellopy import Tello
import time

def test_single_tello():
    # ドローンのインスタンスを作成
    tello = Tello()

    try:
        # ドローンに接続
        print("Telloドローンに接続しています...")
        tello.connect()
        
        # バッテリー残量を確認
        battery = tello.get_battery()
        print(f"バッテリー残量: {battery}%")
        
        # SDK バージョンを確認
        sdk = tello.query_sdk_version()
        print(f"SDKバージョン: {sdk}")
        
        # シリアル番号を確認
        sn = tello.query_serial_number()
        print(f"シリアル番号: {sn}")
        
        # 温度を確認
        temp = tello.get_temperature()
        print(f"温度: {temp}°C")
        
        print("\nテスト完了: ドローンと正常に通信できています")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
    
    finally:
        # 接続を終了
        tello.end()
        print("接続を終了しました")

if __name__ == "__main__":
    print("Tello-1 (TELLO-99B9FA) との接続テストを開始します")
    print("注意: テストを実行する前に、PCがTelloのWiFiネットワークに接続されていることを確認してください")
    input("Enterキーを押してテストを開始...")
    test_single_tello()
