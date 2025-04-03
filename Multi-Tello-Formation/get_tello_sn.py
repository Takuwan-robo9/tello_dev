import socket
import time

def get_tello_sn():
    """
    Telloドローンのシリアル番号を取得する関数
    """
    # ソケットを作成
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 8889))
    
    # コマンドモードに入る
    print("Sending command...")
    sock.sendto('command'.encode('utf-8'), ('192.168.10.1', 8889))
    response, ip = sock.recvfrom(100)
    print(f"Response: {response.decode('utf-8')}")
    
    # シリアル番号を取得
    print("Getting serial number...")
    sock.sendto('sn?'.encode('utf-8'), ('192.168.10.1', 8889))
    response, ip = sock.recvfrom(100)
    sn = response.decode('utf-8')
    print(f"Serial Number: {sn}")
    
    return sn

if __name__ == "__main__":
    print("Make sure your PC is connected to the Tello WiFi network (TELLO-XXXXXX)")
    input("Press Enter to continue...")
    
    try:
        sn = get_tello_sn()
        print(f"\nTello Serial Number: {sn}")
        print("You can now use this serial number in your network_config.yaml file.")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure your PC is connected to the Tello WiFi network.")
