"""
SC Localization 
- Author: 김보성,손원영, 김재위위
- Description: SC 알고리즘 기반 실내 위치 추정 시뮬레이션
- Inputs: 라디오맵 CSV, PDR+RSSI 측정 CSV
- Output: 실시간 추정 경로 시각화
"""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches

# True 경로 좌표 정의
#true_points = [(0, 0), (102, 0), (102, 4), (130, 4), (130, -3),(121, -3), (121, 4), (102, 4), (102, 0), (0, 0)] #장경로

#true_points = [(0, 0), (17,0),(17,11),(17,0),(0,0)] # 단경로

true_points = [(0, 0), (52,0)] # 밴드경로

def generate_true_path(points, step_length=1.0):
    path = []
    for start, end in zip(points[:-1], points[1:]):
        start = np.array(start, dtype=float)
        end = np.array(end, dtype=float)
        vec = end - start
        dist = np.linalg.norm(vec)
        if dist == 0:
            continue
        direction = vec / dist
        num_steps = int(np.floor(dist / step_length))
        for s in range(num_steps):
            pos = start + s * step_length * direction
            path.append(pos)
    path.append(np.array(points[-1]))
    return np.array(path)


true_path = generate_true_path(true_points, step_length=1.0)

# ===================== 1. 라디오맵 불러오기 =====================
radio_map_path = r"C:\Users\"#경로 채우기!
radio_map_df = pd.read_csv(radio_map_path)

# ===================== 2. PDR + RSSI 데이터 불러오기 =====================
pdr_csv_path = r"C:\Users\"  #경로 채우기!
df = pd.read_csv(pdr_csv_path)
pdr_path = df[['x', 'y']].values

# ===================== 3. 공통 AP 리스트 추출 =====================
radio_ap_list = [c for c in radio_map_df.columns if c not in ('x', 'y')]
pdr_ap_list = [c for c in df.columns if c not in ('y', 'x', 'step', 'time', 'timestamp')]
common_aps = sorted(list(set(radio_ap_list) & set(pdr_ap_list)))
print(f">>> 사용할 AP 개수: {len(common_aps)}")

# ===================== 4. 라디오맵 3D 배열 생성 =====================
x_vals = sorted(radio_map_df['x'].unique())
y_vals = sorted(radio_map_df['y'].unique())
num_aps = len(common_aps)
H, W = len(y_vals), len(x_vals)

radio_map = np.full((num_aps, H, W), -100.0, dtype=float)
x_to_i = {x: i for i, x in enumerate(x_vals)}
y_to_i = {y: i for i, y in enumerate(y_vals)}

for _, row in radio_map_df.iterrows():
    xi, yi = x_to_i[row['x']], y_to_i[row['y']]
    for k, ap in enumerate(common_aps):
        radio_map[k, yi, xi] = row[ap]

rssi_history = df[common_aps].values

# ===================== 5. URS 생성 및 위치 찾기 =====================
# URS를 라디오맵 위에서 슬라이딩하며 MAE 기반 위치 비교
def generate_single_urs_dynamic(pdr_path, rssi_values, resolution=1.0):
    origin = pdr_path[0].copy()

    def get_cell(pos):
        cell_x = int(np.round((pos[0] - origin[0]) / resolution))
        cell_y = int(np.round((pos[1] - origin[1]) / resolution))
        return cell_x, cell_y
       

    grid_cells = np.array([get_cell(pos) for pos in pdr_path])
    x_min, x_max = grid_cells[:, 0].min(), grid_cells[:, 0].max()
    y_min, y_max = grid_cells[:, 1].min(), grid_cells[:, 1].max()

    num_aps = rssi_values.shape[1]
    urs = np.full((num_aps, y_max - y_min + 1, x_max - x_min + 1), -100.0)

    for i, (gx, gy) in enumerate(grid_cells):
        px = gx - x_min
        py = gy - y_min
        if 0 <= px < urs.shape[2] and 0 <= py < urs.shape[1]:
            urs[:, py, px] = rssi_values[i]

    offset_x = grid_cells[-1][0] - x_min
    offset_y = grid_cells[-1][1] - y_min

    return urs, (offset_x, offset_y), x_min, y_min

def rotate_path(path, angle_deg):
    rad = np.deg2rad(angle_deg)
    R = np.array([[np.cos(rad), -np.sin(rad)],
                  [np.sin(rad),  np.cos(rad)]])
    return (path - path[0]) @ R.T + path[0]

def calculate_correlation(urs, radio_map):
    best_corr = np.inf
    best_pos = (0, 0)
    urs_flat = urs.flatten()
    mask = urs_flat > -100
    H, W = urs.shape[1], urs.shape[2]

    for i in range(radio_map.shape[1] - H + 1):
        for j in range(radio_map.shape[2] - W + 1):
            seg_flat = radio_map[:, i:i + H, j:j + W].flatten()
            diff = np.mean(np.abs(urs_flat[mask] - seg_flat[mask]))
            if diff < best_corr:
                best_corr = diff
                best_pos = (j, i)

    return best_pos, best_corr

# ===================== 6. SC 경로 추정 루프 및 시각화 =====================
floor_img = mpimg.imread("C:/Users/jaemi/OneDrive/바탕 화면/연구/code/캡스톤/할룽8.png")
buffer_size = 20
estimated = []
current_angle = 0.0  

plt.figure(figsize=(12, 6))
mng = plt.get_current_fig_manager()
try:
    mng.full_screen_toggle()
except:
    pass

for step in range(len(pdr_path)):
    s = max(0, step - buffer_size + 1)
    seg_pdr = pdr_path[s:step + 1]
    seg_rssi = rssi_history[s:step + 1]

    candidates = []
    urs_candidates = []
    for ang in [current_angle-10, current_angle, current_angle+10]:
            rotated = rotate_path(seg_pdr, ang)
            urs, (off_x, off_y), x_min, y_min = generate_single_urs_dynamic(rotated, seg_rssi)
            (j, i), corr = calculate_correlation(urs, radio_map)
            candidates.append(
                (corr, ang, j, i, off_x, off_y, x_min, y_min, urs)
            )


    # 최적 후보 계산산
    best = min(candidates, key=lambda x: x[0])
    corr, best_angle, best_j, best_i, off_x, off_y, best_x_min, best_y_min, best_urs = best
    est_j = best_j + off_x
    est_i = best_i + off_y
    ex = x_vals[est_j]
    ey = y_vals[est_i]
    estimated.append((ex, ey))
    current_angle = best_angle



    # ---- 시각화 ----
    plt.clf()
    plt.imshow(floor_img, extent=[-2, 152, -11, 14], aspect='auto', alpha=1.0)
    plt.plot(np.array(estimated)[:, 0], np.array(estimated)[:, 1], 'yo', markersize=8, label='Estimated positions')
    #plt.plot(ex, ey, 'yo', label='SC Estimated')  # 현재 추정 위치만 점으로 보고싶으면 주석 지우기기
    #plt.scatter(radio_map_df['x'], radio_map_df['y'],facecolors='none', edgecolors='red', s=50, label='RP')# RP 보고싶으면 주석 지우기기
    #plt.plot(pdr_path[:step + 1, 0], pdr_path[:step + 1, 1], 'b--', label='PDR Path') #PDR Path
    plt.plot(true_path[:, 0], true_path[:, 1], 'r--', linewidth=1, label='True Path')
    estimated_np = np.array(estimated)

    plt.plot(0, 0, 'g*', markersize=12, label='start')   # 시작점
    if step == len(pdr_path) - 1:
        plt.plot(estimated_np[-1, 0], estimated_np[-1, 1], 'b*', markersize=12, label='Last Estimated position')#마지막 추정 위치

    plt.axis('equal')
    plt.title(f"Step {step+1} / {len(pdr_path)}")
    plt.legend(loc='upper right')
    plt.pause(0.001)
plt.show()
