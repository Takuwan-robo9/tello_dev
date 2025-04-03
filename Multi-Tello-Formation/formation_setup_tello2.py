import socket

def set_ap(ssid, password):
    '''
    A Function to set tello in AP mode
    :param ssid: the ssid of the network (e.g. name of the Wi-Fi)
    :param password: the password of the network
    :return:
    '''
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
    my_socket.bind(('', 8889))
    cmd_str = 'command'
    print('sending command %s' % cmd_str)
    my_socket.sendto(cmd_str.encode('utf-8'), ('192.168.10.1', 8889))
    response, ip = my_socket.recvfrom(100)
    print('from %s: %s' % (ip, response.decode('utf-8')))

    cmd_str = 'ap %s %s' % (ssid, password)
    print('sending command %s' % cmd_str)
    my_socket.sendto(cmd_str.encode('utf-8'), ('192.168.10.1', 8889))
    response, ip = my_socket.recvfrom(100)
    print('from %s: %s' % (ip, response.decode('utf-8')))

# ここでWi-FiのSSIDとパスワードを設定します
# 注意: このスクリプトを実行する前に、PCがTelloのWi-Fiに接続されていることを確認してください
set_ap('Buffalo-2G-C740', 'petutumg44xbb')
