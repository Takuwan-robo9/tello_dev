#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
キーボード入力によるTello EDUの編隊飛行制御スクリプト

このスクリプトは、複数のTelloドローンをキーボード入力で同時に制御し、
リーダー・フォロワー型のフォーメーション制御を実現します。

キー操作:
- T: 全てのドローンを離陸
- L: 全てのドローンを着陸
- W/A/S/D: リーダードローンの移動（前後左右）
- 矢印キー上下: リーダードローンの上昇/下降
- 矢印キー左右: リーダードローンの左右回転
- F: リーダードローンのフリップ（前方向）
- ESC: プログラム終了！

フォーメーション制御:
- リーダードローンはキーボード入力で直接制御
- フォロワードローンはリーダーの動きに追従し、相対的な位置関係を維持
"""

import sys
import time
import math
import yaml
import socket
import threading
import KeyPressModule_getch as kp
from tello_manager_py3 import Tello_Manager
import numpy as np

# 設定
LEADER_IDX = 0  # リーダードローンのインデックス（0から始まる）
SPEED = 30      # 移動速度（cm/s）
ROTATION_SPEED = 30  # 回転速度（度/s）
INTERVAL = 0.05  # コマンド送信間隔（秒）

# フォーメーション形状の定義（リーダーを原点とした相対位置）
FORMATION = [
    np.array([0, 0]),      # リーダー（原点）
    np.array([0, -100]),   # フォロワー1: リーダーの後方100cm
]

class KeyboardFormationControl:
    def __init__(self):
        # 終了フラグ（最初に初期化）
        self.should_stop = False
        
        # キーボード入力の初期化
        kp.init()
        
        # Tello Managerの初期化
        self.manager = Tello_Manager()
        
        # ドローンの状態
        self.is_flying = False
        self.tellos = []
        self.tello_positions = []  # 各ドローンの推定位置
        self.tello_headings = []   # 各ドローンの推定向き（度）
        
        # ネットワーク設定の読み込み
        self.load_network_config()
        
        # ソケットの初期化（状態受信用）
        self.state_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.state_socket.bind(('', 8890))
        
        # 状態受信スレッドの開始
        self.state_thread = threading.Thread(target=self.state_receiver)
        self.state_thread.daemon = True
        self.state_thread.start()

    def load_network_config(self):
        """network_config.yamlからドローン設定を読み込む"""
        try:
            with open('network_config.yaml', 'r') as file:
                config = yaml.safe_load(file)
                self.drone_configs = config['drones']
                print(f"設定ファイルから{len(self.drone_configs)}機のドローン情報を読み込みました")
        except Exception as e:
            print(f"設定ファイルの読み込みエラー: {e}")
            sys.exit(1)

    def connect_drones(self):
        """ドローンに接続する"""
        print("ドローンへの接続を開始します...")
        
        # 利用可能なドローンを検索
        num_drones = len(self.drone_configs)
        self.manager.find_avaliable_tello(num_drones)
        self.tellos = self.manager.get_tello_list()
        
        if len(self.tellos) < num_drones:
            print(f"警告: {num_drones}機のドローンが必要ですが、{len(self.tellos)}機しか見つかりませんでした")
            if len(self.tellos) == 0:
                print("ドローンが見つかりません。終了します。")
                sys.exit(1)
        
        print(f"{len(self.tellos)}機のドローンに接続しました")
        
        # 各ドローンの初期位置と向きを設定
        self.tello_positions = [np.array([0, 0, 0]) for _ in range(len(self.tellos))]
        self.tello_headings = [0 for _ in range(len(self.tellos))]
        
        # 各ドローンをコマンドモードに設定
        for tello in self.tellos:
            tello.send_command("command")
            time.sleep(0.5)
            tello.send_command("speed " + str(SPEED))
            time.sleep(0.5)
            
        print("全てのドローンをコマンドモードに設定しました")
        return True

    def state_receiver(self):
        """ドローンの状態を受信するスレッド"""
        while not self.should_stop:
            try:
                data, ip = self.state_socket.recvfrom(1024)
                # 状態データの処理（必要に応じて実装）
            except Exception as e:
                pass
            time.sleep(0.01)

    def takeoff_all(self):
        """全てのドローンを離陸させる"""
        if self.is_flying:
            print("既に飛行中です")
            return
        
        print("全てのドローンを離陸させます...")
        
        # 全てのドローンに離陸コマンドを一度に送信
        for i, tello in enumerate(self.tellos):
            print(f"ドローン {i+1} に離陸コマンドを送信します...")
            tello.send_command("takeoff")
            time.sleep(0.5)  # コマンド送信間の短い待機
        
        # 全てのドローンの離陸完了を待機（十分な時間）
        print("全てのドローンの離陸完了を待機しています...")
        time.sleep(8)  # 離陸完了まで十分な時間待機
        
        self.is_flying = True
        print("全てのドローンが離陸しました")

    def land_all(self):
        """全てのドローンを着陸させる"""
        if not self.is_flying:
            print("飛行していません")
            return
        
        print("全てのドローンを着陸させます...")
        for tello in self.tellos:
            tello.send_command("land")
            time.sleep(0.1)
        
        # 着陸完了まで待機
        time.sleep(3)
        self.is_flying = False
        print("全てのドローンが着陸しました")

    def update_formation(self):
        """フォーメーション位置を更新し、各ドローンに移動コマンドを送信"""
        if not self.is_flying or len(self.tellos) < 2:
            return
        
        # リーダーの位置と向き
        leader_pos = self.tello_positions[LEADER_IDX]
        leader_heading_rad = math.radians(self.tello_headings[LEADER_IDX])
        
        # 回転行列（リーダーの向きに合わせてフォーメーションを回転）
        rotation_matrix = np.array([
            [math.cos(leader_heading_rad), -math.sin(leader_heading_rad)],
            [math.sin(leader_heading_rad), math.cos(leader_heading_rad)]
        ])
        
        # 各フォロワーの目標位置を計算
        for i in range(len(self.tellos)):
            if i == LEADER_IDX:
                continue  # リーダーはスキップ
            
            # フォロワーのインデックスに対応するフォーメーション位置
            follower_idx = i if i < len(FORMATION) else 0
            formation_pos_2d = FORMATION[follower_idx]
            
            # リーダーの向きに合わせて回転（行列の積）
            rotated_pos = np.dot(rotation_matrix, formation_pos_2d)
            
            # リーダーの位置を基準に目標位置を計算
            target_x = leader_pos[0] + rotated_pos[0]
            target_y = leader_pos[1] + rotated_pos[1]
            target_z = leader_pos[2]  # 高さはリーダーと同じ
            
            # 現在位置と目標位置の差分を計算
            current_pos = self.tello_positions[i]
            dx = target_x - current_pos[0]
            dy = target_y - current_pos[1]
            dz = target_z - current_pos[2]
            
            # 移動距離が小さい場合はコマンドを送信しない
            if abs(dx) < 20 and abs(dy) < 20 and abs(dz) < 20:
                continue
            
            # 移動コマンドを送信（小さな移動量に制限）
            max_distance = 50  # 一度に移動する最大距離（cm）
            dx = max(-max_distance, min(max_distance, dx))
            dy = max(-max_distance, min(max_distance, dy))
            dz = max(-max_distance, min(max_distance, dz))
            
            print(f"フォロワー {i+1} に移動コマンドを送信: dx={dx}, dy={dy}, dz={dz}")
            self.tellos[i].send_command(f"go {int(dx)} {int(dy)} {int(dz)} {SPEED}")
            
            # 移動完了を待機
            time.sleep(1)
            
            # 位置の更新（実際の移動量を反映）
            self.tello_positions[i] = self.tello_positions[i] + np.array([dx, dy, dz])

    def control_leader(self):
        """キーボード入力に基づいてリーダードローンを制御"""
        if not self.is_flying:
            return
        
        # リーダードローンの現在位置と向き
        leader_pos = self.tello_positions[LEADER_IDX]
        leader_heading = self.tello_headings[LEADER_IDX]
        
        # 移動量
        dx, dy, dz = 0, 0, 0
        dyaw = 0
        
        # 前後左右の移動（WASDキーを使用）
        if kp.getKey("w"):
            # 前進（現在の向きに合わせて）
            dx = int(SPEED * math.cos(math.radians(leader_heading)))
            dy = int(SPEED * math.sin(math.radians(leader_heading)))
        elif kp.getKey("s"):
            # 後退（現在の向きに合わせて）
            dx = -int(SPEED * math.cos(math.radians(leader_heading)))
            dy = -int(SPEED * math.sin(math.radians(leader_heading)))
        
        if kp.getKey("a"):
            # 左移動（現在の向きに対して垂直）
            dx = int(SPEED * math.cos(math.radians(leader_heading - 90)))
            dy = int(SPEED * math.sin(math.radians(leader_heading - 90)))
        elif kp.getKey("d"):
            # 右移動（現在の向きに対して垂直）
            dx = int(SPEED * math.cos(math.radians(leader_heading + 90)))
            dy = int(SPEED * math.sin(math.radians(leader_heading + 90)))
        
        # 上昇・下降（矢印キーの上下を使用）
        if kp.getKey("UP"):
            dz = SPEED
        elif kp.getKey("DOWN"):
            dz = -SPEED
        
        # 回転（矢印キーの左右を使用）
        if kp.getKey("LEFT"):
            dyaw = -ROTATION_SPEED
        elif kp.getKey("RIGHT"):
            dyaw = ROTATION_SPEED
        
        # 移動コマンドを送信
        if dx != 0 or dy != 0 or dz != 0:
            self.tellos[LEADER_IDX].send_command(f"go {dx} {dy} {dz} {SPEED}")
            
            # 位置の更新
            new_pos = leader_pos + np.array([dx, dy, dz])
            self.tello_positions[LEADER_IDX] = new_pos
        
        # 回転コマンドを送信
        if dyaw != 0:
            self.tellos[LEADER_IDX].send_command(f"cw {abs(dyaw)}" if dyaw > 0 else f"ccw {abs(dyaw)}")
            
            # 向きの更新
            new_heading = (leader_heading + dyaw) % 360
            self.tello_headings[LEADER_IDX] = new_heading
        
        # フリップ
        if kp.getKey("f"):
            self.tellos[LEADER_IDX].send_command("flip f")
            time.sleep(3)  # フリップ完了まで待機

    def run(self):
        """メインループ"""
        print("キーボード編隊飛行制御を開始します")
        print("キー操作:")
        print("- T: 全てのドローンを離陸")
        print("- L: 全てのドローンを着陸")
        print("- W/A/S/D: リーダードローンの移動（前後左右）")
        print("- 矢印キー上下: リーダードローンの上昇/下降")
        print("- 矢印キー左右: リーダードローンの左右回転")
        print("- F: リーダードローンのフリップ（前方向）")
        print("- ESC: プログラム終了")
        
        # ドローンに接続
        if not self.connect_drones():
            return
        
        try:
            while not self.should_stop:
                # キー入力の状態を表示（デバッグ用）
                pressed = []
                for key in ['t', 'l', 'w', 'a', 's', 'd', 'UP', 'DOWN', 'LEFT', 'RIGHT', 'ESCAPE']:
                    if kp.getKey(key):
                        pressed.append(key)
                if pressed:
                    print("押されているキー: " + ", ".join(pressed))
                
                # ESCキーで終了
                if kp.getKey("ESCAPE"):
                    print("ESCキーが押されました。終了します。")
                    self.should_stop = True
                    break
                
                # 離陸
                if kp.getKey("t"):
                    print("Tキーが押されました。離陸します。")
                    self.takeoff_all()
                    time.sleep(1)  # キーのバウンス防止
                
                # 着陸
                if kp.getKey("l"):
                    print("Lキーが押されました。着陸します。")
                    self.land_all()
                    time.sleep(1)  # キーのバウンス防止
                
                # リーダードローンの制御
                self.control_leader()
                
                # フォーメーション更新
                self.update_formation()
                
                time.sleep(INTERVAL)
        
        except KeyboardInterrupt:
            print("プログラムが中断されました")
        
        finally:
            # 終了処理
            if self.is_flying:
                self.land_all()
            print("プログラムを終了します")

if __name__ == "__main__":
    try:
        print("キーボード編隊飛行制御プログラムを開始します...")
        controller = KeyboardFormationControl()
        controller.run()
    except Exception as e:
        import traceback
        print(f"エラーが発生しました: {e}")
        print("詳細なエラー情報:")
        traceback.print_exc()
