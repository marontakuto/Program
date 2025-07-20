"""
軌跡解析および可視化システム

GPS軌跡データを読み込み、基準線を基準とした座標変換を行い、
元の座標系と変換後の座標系で軌跡を可視化する。
"""

import csv
import math
import sys
from typing import List, Dict, Optional, Tuple
import pyproj
import matplotlib.pyplot as plt


# 設定定数
PROJECTION_LAT_CENTER = 35.0000
PROJECTION_LON_CENTER = 135.0000
CSV_FILE_PATH = r'log.csv'
REQUIRED_FIELDS = ['target_lat', 'target_lon', 'heading_deg', 'offset_deg']
FIGURE_SIZE = (15, 7)
FONT_FAMILY = 'Yu Gothic'


class TrajectoryAnalyzer:
    """軌跡解析のメインクラス"""
    
    def __init__(self):
        """初期化"""
        self.proj = pyproj.Proj(proj='aeqd', lat_0=PROJECTION_LAT_CENTER, lon_0=PROJECTION_LON_CENTER)
        plt.rcParams['font.family'] = FONT_FAMILY
    
    def latlon_to_xy(self, lat: float, lon: float) -> Tuple[float, float]:
        """緯度経度をXY座標に変換"""
        return self.proj(lon, lat)
    
    def load_csv_data(self, file_path: str) -> List[Dict[str, str]]:
        """CSVファイルを読み込む"""
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                return list(csv.DictReader(f))
        except FileNotFoundError:
            print(f"エラー: ファイル '{file_path}' が見つかりません")
            sys.exit(1)
        except Exception as e:
            print(f"CSVファイル読み込みエラー: {e}")
            sys.exit(1)
    
    def filter_turn_status_data(self, data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """旋回状態のデータをフィルタリング"""
        turn_status_data = []
        found_0_to_3 = False
        
        for row in data:
            if not row.get('turn_status'):
                continue
            
            try:
                status = int(row['turn_status'])
                if status == 0 and not found_0_to_3:
                    found_0_to_3 = True
                
                if found_0_to_3:
                    turn_status_data.append(row)
                    if status == 1:
                        # 直近5件にstatus=3があるかチェック
                        recent_statuses = [
                            int(prev_row['turn_status']) 
                            for prev_row in turn_status_data[-5:] 
                            if prev_row.get('turn_status')
                        ]
                        if 3 in recent_statuses:
                            break
            except ValueError:
                continue
        
        return turn_status_data
    
    def extract_reference_data(self, data: List[Dict[str, str]]) -> Optional[Dict[str, float]]:
        """基準線算出に必要なデータを抽出"""
        for row in data:
            if all(row.get(field) for field in REQUIRED_FIELDS):
                try:
                    return {
                        'target_lat': float(row['target_lat']),
                        'target_lon': float(row['target_lon']),
                        'heading_deg': float(row['heading_deg']),
                        'offset_deg': float(row['offset_deg'])
                    }
                except ValueError:
                    continue
        return None
    
    def calculate_baseline_vectors(self, heading_deg: float, offset_deg: float) -> Tuple[float, float, float, float, float]:
        """基準線の方向ベクトルと垂直ベクトルを計算"""
        # 基準線の方向 = heading_deg - offset_deg
        baseline_heading = heading_deg - offset_deg
        baseline_rad = math.radians(baseline_heading)
        
        # 基準線の方向ベクトル（北基準、時計回り）
        baseline_unit_x = math.sin(baseline_rad)  # 東方向成分
        baseline_unit_y = math.cos(baseline_rad)  # 北方向成分
        
        # 基準線に垂直な方向ベクトル（右手系、基準線から見て右側が正）
        baseline_perp_x = baseline_unit_y
        baseline_perp_y = -baseline_unit_x
        
        return baseline_unit_x, baseline_unit_y, baseline_perp_x, baseline_perp_y, baseline_heading
    
    def extract_trajectory_coordinates(self, data: List[Dict[str, str]]) -> List[Tuple[float, float]]:
        """軌跡データをXY座標に変換"""
        trajectory_xys = []
        for row in data:
            if row.get('lat') and row.get('lon'):
                try:
                    lat, lon = float(row['lat']), float(row['lon'])
                    x, y = self.latlon_to_xy(lat, lon)
                    trajectory_xys.append((x, y))
                except ValueError:
                    continue
        return trajectory_xys
    
    def transform_to_baseline_coordinate(self, trajectory_xys: List[Tuple[float, float]],
                                       target_x: float, target_y: float,
                                       baseline_unit_x: float, baseline_unit_y: float,
                                       baseline_perp_x: float, baseline_perp_y: float) -> List[Tuple[float, float]]:
        """基準線を基準とした座標系に変換"""
        transformed_trajectory = []
        
        for x, y in trajectory_xys:
            # target点からの相対位置
            dx, dy = x - target_x, y - target_y
            
            # 基準線方向をY軸、垂直方向をX軸とする座標系に変換
            transformed_x = dx * baseline_perp_x + dy * baseline_perp_y  # 横方向
            transformed_y = dx * baseline_unit_x + dy * baseline_unit_y  # 縦方向
            transformed_trajectory.append((transformed_x, transformed_y))
        
        return transformed_trajectory
    
    def plot_results(self, trajectory_xys: List[Tuple[float, float]],
                    transformed_trajectory: List[Tuple[float, float]],
                    target_x: float, target_y: float,
                    baseline_unit_x: float, baseline_unit_y: float,
                    baseline_perp_x: float, baseline_perp_y: float,
                    baseline_heading: float) -> None:
        """結果をプロット"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=FIGURE_SIZE)
        
        # 元の座標系でのプロット
        if trajectory_xys:
            xs, ys = zip(*trajectory_xys)
            ax1.plot(xs, ys, '-', linewidth=2, label='軌跡', alpha=0.7)
            
            # スケール計算
            x_span = max(xs) - min(xs) if len(xs) > 1 else 1000
            y_span = max(ys) - min(ys) if len(ys) > 1 else 1000
            line_scale = max(x_span, y_span) * 0.8
            
            # 基準線の描画
            line_start_x = target_x - baseline_unit_x * line_scale * 1.5
            line_start_y = target_y - baseline_unit_y * line_scale * 1.5
            line_end_x = target_x + baseline_unit_x * line_scale * 0.5
            line_end_y = target_y + baseline_unit_y * line_scale * 0.5
            
            ax1.plot([line_start_x, line_end_x], [line_start_y, line_end_y],
                    '--', color='red', linewidth=1, label=f'基準線 (方位={baseline_heading:.1f}°)')
            
            # 垂直線の描画
            perp_start_x = target_x - baseline_perp_x * line_scale * 0.5
            perp_start_y = target_y - baseline_perp_y * line_scale * 0.5
            perp_end_x = target_x + baseline_perp_x * line_scale * 0.5
            perp_end_y = target_y + baseline_perp_y * line_scale * 0.5
            
            ax1.plot([perp_start_x, perp_end_x], [perp_start_y, perp_end_y],
                    ':', color='blue', linewidth=1, label='垂直線')
        
        ax1.set_title("NED座標系")
        ax1.axis('equal')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 変換後のプロット
        if transformed_trajectory:
            t_xs, t_ys = zip(*transformed_trajectory)
            ax2.plot(t_xs, t_ys, '-', linewidth=2, color='green', label='軌跡')
            
            # 基準線（Y軸）と垂直線（X軸）
            ax2.axvline(x=0, color='red', linestyle='--', linewidth=1, label='基準線')
            ax2.axhline(y=0, color='blue', linestyle=':', linewidth=1, label='垂直線')
        
        ax2.set_title("基準線基準の座標系")
        ax2.set_xlabel("基準線からの横方向距離 [m]")
        ax2.set_ylabel("基準線方向の距離 [m]")
        ax2.axis('equal')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def analyze(self) -> None:
        """軌跡解析を実行"""
        # データ読み込み
        data = self.load_csv_data(CSV_FILE_PATH)
        
        # 基準データの抽出
        reference_data = self.extract_reference_data(data)
        if reference_data is None:
            print("基準線算出に必要なデータが不足しています")
            print(f"必要データ: {', '.join(REQUIRED_FIELDS)}")
            sys.exit(1)
        
        # 基準線計算
        baseline_unit_x, baseline_unit_y, baseline_perp_x, baseline_perp_y, baseline_heading = \
            self.calculate_baseline_vectors(reference_data['heading_deg'], reference_data['offset_deg'])
        
        # ターゲット座標変換
        target_x, target_y = self.latlon_to_xy(reference_data['target_lat'], reference_data['target_lon'])
        
        # 軌跡データ処理
        turn_status_data = self.filter_turn_status_data(data)
        trajectory_xys = self.extract_trajectory_coordinates(turn_status_data)
        
        # 座標変換
        transformed_trajectory = self.transform_to_baseline_coordinate(
            trajectory_xys, target_x, target_y,
            baseline_unit_x, baseline_unit_y, baseline_perp_x, baseline_perp_y
        )
        
        # 結果をプロット
        self.plot_results(
            trajectory_xys, transformed_trajectory, target_x, target_y,
            baseline_unit_x, baseline_unit_y, baseline_perp_x, baseline_perp_y,
            baseline_heading
        )


def main() -> None:
    """メイン関数"""
    analyzer = TrajectoryAnalyzer()
    analyzer.analyze()


if __name__ == "__main__":
    main()
