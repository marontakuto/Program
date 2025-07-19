import csv
import math
import pyproj
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Yu Gothic'

# 投影法（中心はデータの起点周辺）
proj = pyproj.Proj(proj='aeqd', lat_0=35.0000, lon_0=135.0000)

def latlon_to_xy(lat, lon):
    return proj(lon, lat)

# CSV 読み込み
with open('log.csv', newline='') as f:
    reader = csv.DictReader(f)
    data = [row for row in reader]

# 旋回状態のフィルタリング（軌跡解析用）
turn_status_data = []
found_0_to_3 = False

for row in data:
    if row['turn_status']:
        status = int(row['turn_status'])
        if status == 0 and not found_0_to_3:
            found_0_to_3 = True
        if found_0_to_3:
            turn_status_data.append(row)
            if status == 1 and any(int(prev_row['turn_status']) == 3 for prev_row in turn_status_data[-5:] if prev_row['turn_status']):
                break

# 基準線算出に必要なデータを取得（最初に見つかったもの）
reference_data = None
for row in data:  # 元データから取得（フィルタリング不要）
    if (row['target_lat'] and row['target_lon'] and 
        row['heading_deg'] and row['offset_deg']):
        reference_data = {
            'target_lat': float(row['target_lat']),
            'target_lon': float(row['target_lon']),
            'heading_deg': float(row['heading_deg']),
            'offset_deg': float(row['offset_deg'])
        }
        break

if reference_data is None:
    print("基準線算出に必要なデータが不足しています")
    print("必要データ: target_lat, target_lon, heading_deg, offset_deg")
    exit(1)

# 基準線の算出
# 基準線の方向 = heading_deg - offset_deg
# （offset_degは基準線からのずれなので、heading_degから引く）
baseline_heading = reference_data['heading_deg'] - reference_data['offset_deg']

# target座標を投影座標系に変換
target_x, target_y = latlon_to_xy(reference_data['target_lat'], reference_data['target_lon'])

# 基準線の方向ベクトルを算出（北基準、時計回り）
baseline_rad = math.radians(baseline_heading)
# 北をY軸正方向とする座標系での方向ベクトル
baseline_unit_x = math.sin(baseline_rad)  # 東方向成分
baseline_unit_y = math.cos(baseline_rad)  # 北方向成分

# 基準線に垂直な方向ベクトル（右手系、基準線から見て右側が正）
baseline_perp_x = baseline_unit_y   # 垂直方向のX成分
baseline_perp_y = -baseline_unit_x  # 垂直方向のY成分

# 軌跡用データを抽出
trajectory_data = []
for row in turn_status_data:
    if row['lat'] and row['lon']:
        trajectory_data.append(row)

# 軌跡データの座標変換
trajectory_xys = []
for row in trajectory_data:
    lat = float(row['lat'])
    lon = float(row['lon'])
    x, y = latlon_to_xy(lat, lon)
    trajectory_xys.append((x, y))

# 基準線を基準とした座標系への変換
transformed_trajectory = []
cross_track_errors = []

for i, (x, y) in enumerate(trajectory_xys):
    # target点からの相対位置
    dx, dy = x - target_x, y - target_y
    
    # 基準線方向をY軸、垂直方向をX軸とする座標系に変換
    transformed_x = dx * baseline_perp_x + dy * baseline_perp_y  # 横方向（基準線からの距離）
    transformed_y = dx * baseline_unit_x + dy * baseline_unit_y  # 縦方向（基準線方向）
    transformed_trajectory.append((transformed_x, transformed_y))

# プロット
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

# 元の座標系でのプロット
if trajectory_xys:
    xs, ys = zip(*trajectory_xys)
    ax1.plot(xs, ys, '-', linewidth=2, label='軌跡', alpha=0.7)
    
    # 基準線の描画（target点を通る基準線方向の直線）
    x_span = max(xs) - min(xs) if len(xs) > 1 else 1000
    y_span = max(ys) - min(ys) if len(ys) > 1 else 1000
    line_scale = max(x_span, y_span) * 0.8
    
    # 基準線
    line_start_x = target_x - baseline_unit_x * line_scale * 1.5
    line_start_y = target_y - baseline_unit_y * line_scale * 1.5
    line_end_x = target_x + baseline_unit_x * line_scale * 0.5
    line_end_y = target_y + baseline_unit_y * line_scale * 0.5
    
    ax1.plot([line_start_x, line_end_x], [line_start_y, line_end_y], 
             '--', color='red', linewidth=1, label=f'基準線 (方位={baseline_heading:.1f}°)')
    
    # ターゲット点に接して基準線に垂直な線を描画
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
    
    # 基準線（Y軸）
    ax2.axvline(x=0, color='red', linestyle='--', linewidth=1, label='基準線')
    
    # 垂直線（X軸）
    ax2.axhline(y=0, color='blue', linestyle=':', linewidth=1, label='垂直線')

ax2.set_title("基準線基準の座標系")
ax2.set_xlabel("基準線からの横方向距離 [m]")
ax2.set_ylabel("基準線方向の距離 [m]")
ax2.axis('equal')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
