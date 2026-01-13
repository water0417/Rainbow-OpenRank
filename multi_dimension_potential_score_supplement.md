# 多维度潜力得分模型补充文档

## 1. 代码示例与实际计算示例

### 1.1 完整代码实现

```python
import json
import numpy as np
import datetime
from datetime import datetime as dt

# 读取数据
def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 斜率计算
def calculate_growth_slope(timeline_data, months_count=6):
    if not timeline_data or len(timeline_data) < 2:
        return 0
  
    sorted_data = sorted(timeline_data, key=lambda x: x.get('month', x.get('date', '')))
    recent_data = sorted_data[-months_count:] if len(sorted_data) >= months_count else sorted_data
  
    months = []
    values = []
  
    for i, item in enumerate(recent_data):
        months.append(i)
        if 'stars' in item:
            values.append(item['stars'])
        elif 'value' in item:
            values.append(item['value'])
        elif 'count' in item:
            values.append(item['count'])
  
    if len(months) >= 2:
        slope, intercept = np.polyfit(months, values, 1)
        return max(slope, 0)
    else:
        return 0

# 标准化
def min_max_normalize(values):
    if not values or max(values) == min(values):
        return [0.0] * len(values)
    return [(v - min(values)) / (max(values) - min(values)) for v in values]

# 计算贡献者增长
def calculate_contributor_growth(repo):
    contributors = repo.get('contributors', [])
    if not contributors or len(contributors) < 2:
        return 0
  
    basic_info = repo['basic_info']
    created_at = basic_info.get('created_at', '2020-01-01 00:00:00')
    created_date = dt.strptime(created_at, '%Y-%m-%d %H:%M:%S')
    now = dt.now()
    months_existed = (now.year - created_date.year) * 12 + (now.month - created_date.month)
  
    if months_existed < 6:
        return 0
  
    monthly_growth = len(contributors) / months_existed
    recent_growth = [monthly_growth * (i+1) for i in range(6)]
  
    slope, _ = np.polyfit(range(6), recent_growth, 1)
    return max(slope, 0)

# 计算活动增长
def calculate_activity_growth(repo):
    metrics = repo['metrics']
    basic_info = repo['basic_info']
  
    created_at = basic_info.get('created_at', '2020-01-01 00:00:00')
    created_date = dt.strptime(created_at, '%Y-%m-%d %H:%M:%S')
    now = dt.now()
    months_existed = (now.year - created_date.year) * 12 + (now.month - created_date.month)
  
    if months_existed < 6:
        return 0
  
    total_activity = metrics.get('open_issues_count', 0)
    monthly_activity = total_activity / months_existed
    recent_activity = [monthly_activity * (i+1) for i in range(6)]
  
    slope, _ = np.polyfit(range(6), recent_activity, 1)
    return max(slope, 0)

# 计算协作增长
def calculate_collaboration_growth(repo):
    contributors = repo.get('contributors', [])
    basic_info = repo['basic_info']
  
    if len(contributors) < 2:
        return 0
  
    created_at = basic_info.get('created_at', '2020-01-01 00:00:00')
    created_date = dt.strptime(created_at, '%Y-%m-%d %H:%M:%S')
    now = dt.now()
    months_existed = (now.year - created_date.year) * 12 + (now.month - created_date.month)
  
    if months_existed < 6:
        return 0
  
    n = len(contributors)
    possible_connections = n * (n - 1) / 2
    actual_connections = min(n * 2, possible_connections)
    density = actual_connections / possible_connections if possible_connections > 0 else 0
  
    monthly_density_growth = density / months_existed
    recent_density = [monthly_density_growth * (i+1) for i in range(6)]
  
    slope, _ = np.polyfit(range(6), recent_density, 1)
    return max(slope, 0)

# 计算潜力得分
def calculate_potential_score(repo):
    stars_timeline = repo.get('stars_timeline', [])
    stars_slope = calculate_growth_slope(stars_timeline, 6)
  
    contributor_slope = calculate_contributor_growth(repo)
    activity_slope = calculate_activity_growth(repo)
    collaboration_slope = calculate_collaboration_growth(repo)
  
    slopes = {
        'stars': stars_slope,
        'contributor': contributor_slope,
        'activity': activity_slope,
        'collaboration': collaboration_slope
    }
  
    return slopes

# 主函数
def main():
    data = load_data('merged_1_2.json')
    processed_repos = []
  
    for repo in data['repos_data']:
        try:
            if 'stars_timeline' in repo and len(repo['stars_timeline']) >= 6:
                slopes = calculate_potential_score(repo)
                repo['slopes'] = slopes
                processed_repos.append(repo)
        except Exception as e:
            print(f"Error processing repo {repo['basic_info']['full_name']}: {e}")
            continue
  
    # 标准化和加权求和
    stars_slopes = [repo['slopes']['stars'] for repo in processed_repos]
    contributor_slopes = [repo['slopes']['contributor'] for repo in processed_repos]
    activity_slopes = [repo['slopes']['activity'] for repo in processed_repos]
    collaboration_slopes = [repo['slopes']['collaboration'] for repo in processed_repos]
  
    normalized_stars = min_max_normalize(stars_slopes)
    normalized_contributor = min_max_normalize(contributor_slopes)
    normalized_activity = min_max_normalize(activity_slopes)
    normalized_collaboration = min_max_normalize(collaboration_slopes)
  
    for i, repo in enumerate(processed_repos):
        repo['normalized_slopes'] = {
            'stars': normalized_stars[i],
            'contributor': normalized_contributor[i],
            'activity': normalized_activity[i],
            'collaboration': normalized_collaboration[i]
        }
    
        weights = {'stars': 0.4, 'contributor': 0.25, 'activity': 0.2, 'collaboration': 0.15}
        normalized_weighted_sum = (
            repo['normalized_slopes']['stars'] * weights['stars'] +
            repo['normalized_slopes']['contributor'] * weights['contributor'] +
            repo['normalized_slopes']['activity'] * weights['activity'] +
            repo['normalized_slopes']['collaboration'] * weights['collaboration']
        )
    
        metrics = repo['metrics']
        total_stars = metrics.get('star_count', 0)
        total_contributors = len(repo.get('contributors', []))
    
        niche_factor = 1.0
        if total_stars > 10000:
            niche_factor *= 0.8
        elif total_stars > 5000:
            niche_factor *= 0.9
        
        if total_contributors > 500:
            niche_factor *= 0.8
        elif total_contributors > 200:
            niche_factor *= 0.9
    
        repo['normalized_potential_score'] = normalized_weighted_sum * niche_factor
  
    # 排序输出
    sorted_repos = sorted(
        processed_repos,
        key=lambda x: x['normalized_potential_score'],
        reverse=True
    )[:10]
  
    # 保存结果
    result = {
        'generation_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'model_info': {
            'name': '多维度潜力得分模型',
            'version': '1.0'
        },
        'top_10_repos': sorted_repos
    }
  
    with open('top_10_potential_repos.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

if __name__ == '__main__':
    main()
```

### 1.2 实际计算示例

以一个虚构的仓库为例，演示潜力得分的完整计算过程：

#### 输入数据

```python
# 仓库示例数据
repo_example = {
    'basic_info': {
        'repo_name': 'example-repo',
        'full_name': 'user/example-repo',
        'created_at': '2025-01-01 12:00:00'
    },
    'metrics': {
        'star_count': 8500,
        'fork_count': 1200,
        'open_issues_count': 450
    },
    'stars_timeline': [
        {'month': '2025-07', 'stars': 1500},
        {'month': '2025-08', 'stars': 2100},
        {'month': '2025-09', 'stars': 2800},
        {'month': '2025-10', 'stars': 3900},
        {'month': '2025-11', 'stars': 5200},
        {'month': '2025-12', 'stars': 6800}
    ],
    'contributors': [
        {'id': 1, 'login': 'user1', 'contributions': 20},
        {'id': 2, 'login': 'user2', 'contributions': 15},
        {'id': 3, 'login': 'user3', 'contributions': 10},
        {'id': 4, 'login': 'user4', 'contributions': 8},
        {'id': 5, 'login': 'user5', 'contributions': 5}
    ]
}
```

#### 步骤1：计算各指标斜率

1. **Stars增长斜率计算**：

   ```
   月份索引: [0, 1, 2, 3, 4, 5]
   星标数: [1500, 2100, 2800, 3900, 5200, 6800]
   线性回归斜率: 1083.33
   ```
2. **贡献者增长斜率计算**：

   ```
   贡献者总数: 5
   仓库存在月数: 12
   月均增长: 5 / 12 = 0.4167
   增长序列: [0.4167, 0.8333, 1.25, 1.6667, 2.0833, 2.5]
   线性回归斜率: 0.4167
   ```
3. **活动增长斜率计算**：

   ```
   开放问题数: 450
   月均活动: 450 / 12 = 37.5
   活动序列: [37.5, 75, 112.5, 150, 187.5, 225]
   线性回归斜率: 37.5
   ```
4. **协作密度增长斜率计算**：

   ```
   贡献者数: 5
   可能的连接数: 5 * 4 / 2 = 10
   实际连接数: min(5 * 2, 10) = 10
   协作密度: 10 / 10 = 1.0
   月均密度增长: 1.0 / 12 = 0.0833
   密度序列: [0.0833, 0.1667, 0.25, 0.3333, 0.4167, 0.5]
   线性回归斜率: 0.0833
   ```

#### 步骤2：标准化处理

假设当前批次有1000个仓库，各指标的最大最小值为：

```
stars_max: 2500.0, stars_min: 0.0
contributor_max: 1.5, contributor_min: 0.0
activity_max: 100.0, activity_min: 0.0
collaboration_max: 0.2, collaboration_min: 0.0
```

标准化后的值：

```
stars_normalized: (1083.33 - 0) / (2500 - 0) = 0.4333
contributor_normalized: (0.4167 - 0) / (1.5 - 0) = 0.2778
activity_normalized: (37.5 - 0) / (100 - 0) = 0.3750
collaboration_normalized: (0.0833 - 0) / (0.2 - 0) = 0.4165
```

#### 步骤3：加权求和

```
weighted_sum = 0.4333 * 0.4 + 0.2778 * 0.25 + 0.3750 * 0.2 + 0.4165 * 0.15
            = 0.1733 + 0.0694 + 0.0750 + 0.0625
            = 0.3802
```

#### 步骤4：小众修正

```
total_stars = 8500 (在5000-10000之间，衰减因子0.9)
total_contributors = 5 (小于200，无衰减)

niche_factor = 1.0 * 0.9 = 0.9
```

#### 步骤5：最终潜力得分

```
potential_score = 0.3802 * 0.9 = 0.3422
```

## 2. 结果解释与应用

### 2.1 得分范围与含义

| 得分范围  | 潜力等级 | 含义                               |
| --------- | -------- | ---------------------------------- |
| 0.8 - 1.0 | S级      | 极高潜力，处于爆发增长期的小众项目 |
| 0.6 - 0.8 | A级      | 高潜力，增长趋势明显               |
| 0.4 - 0.6 | B级      | 中高潜力，有较好的增长迹象         |
| 0.2 - 0.4 | C级      | 中等潜力，增长平稳                 |
| 0.0 - 0.2 | D级      | 低潜力，增长缓慢或停滞             |

### 2.2 结果应用建议

#### 对于投资者

- **S级项目**：重点关注，考虑早期投资
- **A级项目**：持续跟踪，等待合适的投资时机
- **B级项目**：作为备选，关注其发展动态

#### 对于项目维护者

- **分析各指标贡献**：了解项目的优势和不足
- **针对性改进**：根据薄弱指标制定改进策略
- **对比同类项目**：了解自己在同类项目中的位置

#### 对于研究人员

- **趋势分析**：分析不同领域项目的潜力分布
- **模式识别**：识别高潜力项目的共同特征
- **预测验证**：验证模型预测的准确性

## 3. 可视化工具与最佳实践

### 3.1 数据可视化建议

#### Stars增长趋势图

```python
import matplotlib.pyplot as plt
import numpy as np

# 示例数据
months = ['2025-07', '2025-08', '2025-09', '2025-10', '2025-11', '2025-12']
stars = [1500, 2100, 2800, 3900, 5200, 6800]

# 计算趋势线
x = np.arange(len(months))
slope, intercept = np.polyfit(x, stars, 1)
trend_line = slope * x + intercept

# 绘制图表
plt.figure(figsize=(10, 6))
plt.plot(months, stars, 'o-', label='实际星标数')
plt.plot(months, trend_line, 'r--', label=f'趋势线 (斜率: {slope:.2f})')
plt.xlabel('月份')
plt.ylabel('星标数')
plt.title('Stars增长趋势与斜率')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('stars_growth_trend.png')
```

#### 多维度雷达图

```python
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D

def radar_factory(num_vars, frame='circle'):
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)
    class RadarTransform(PolarAxes.PolarTransform):
        def transform_path_non_affine(self, path):
            if path._interpolation_steps > 1:
                path = path.interpolated(num_vars * 2)
            return Path(self.transform(path.vertices), path.codes)
  
    class RadarAxes(PolarAxes):
        name = 'radar'
        PolarTransform = RadarTransform
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.set_theta_zero_location('N')
    
        def fill(self, *args, closed=True, **kwargs):
            return super().fill(closed=closed, *args, **kwargs)
    
        def plot(self, *args, **kwargs):
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)
    
        def _close_line(self, line):
            x, y = line.get_data()
            if x[0] != x[-1]:
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                line.set_data(x, y)
    
        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)
    
        def _gen_axes_patch(self):
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars, radius=.5, edgecolor="k")
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)
    
        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':
                spine = Spine(axes=self, spine_type='circle', path=Path.unit_regular_polygon(num_vars))
                spine.set_transform(Affine2D().scale(.5).translate(.5, .5) + self.transAxes)
                return {'polar': spine}
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)
  
    register_projection(RadarAxes)
    return theta

# 示例数据
categories = ['Stars增长', '贡献者增长', '活动增长', '协作密度增长']
values = [0.4333, 0.2778, 0.3750, 0.4165]

# 创建雷达图
theta = radar_factory(4, frame='polygon')
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='radar'))

ax.plot(theta, values, 'o-', linewidth=2, label='示例仓库')
ax.fill(theta, values, alpha=0.25)
ax.set_varlabels(categories)
ax.set_ylim(0, 1)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
ax.set_title('多维度潜力得分雷达图', pad=20)

plt.tight_layout()
plt.savefig('radar_chart.png')
```

### 3.2 最佳实践

1. **定期更新数据**：每周或每月更新一次数据，确保结果的时效性
2. **动态调整权重**：根据不同领域调整指标权重，如AI领域可增加活动指标权重
3. **结合定性分析**：潜力得分仅作为参考，还需结合项目内容、团队背景等定性因素
4. **设置监控阈值**：对得分突增的项目设置警报，及时发现爆发性项目

## 4. 常见问题与解决方案

### 4.1 数据质量问题

**问题**：部分仓库的stars_timeline数据不完整
**解决方案**：

- 仅处理数据完整的仓库
- 使用插值法填充缺失数据

**问题**：某些仓库的活动数据异常高
**解决方案**：

- 使用3σ原则过滤异常值
- 对活动数据进行对数转换

### 4.2 计算结果问题

**问题**：某些大众项目得分仍然较高
**解决方案**：

- 调整小众修正的阈值和衰减因子
- 增加更多小众特征指标

**问题**：某些项目的协作密度指标得分异常
**解决方案**：

- 优化协作密度的计算方法
- 增加更多协作网络特征

### 4.3 性能问题

**问题**：处理大量仓库时计算速度慢
**解决方案**：

- 使用并行计算库如multiprocessing
- 对数据进行采样处理
- 优化线性回归算法
