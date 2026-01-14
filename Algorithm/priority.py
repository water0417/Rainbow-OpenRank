import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

INPUT_JSON = "all.json"
OUTPUT_CSV = "priority.csv"

W1 = 0.4
W2 = 0.35
W3 = 0.25

def extract_repo_data(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    repos = data['repos_data']
    
    repo_list = []
    for repo in repos:
        basic_info = repo.get('basic_info', {})
        metrics = repo.get('metrics', {})
        activity = repo.get('activity', {})
        timeline = repo.get('timeline', {})
        
        repo_data = {
            'repo_name': basic_info.get('full_name', ''),
            'owner': basic_info.get('owner', ''),
            'repo_name_short': basic_info.get('repo_name', ''),
            'language': basic_info.get('language', ''),
            'description': basic_info.get('description', ''),
            'html_url': basic_info.get('html_url', ''),
            
            'openrank': metrics.get('star_count', 0) * 0.1,
            'stars': metrics.get('star_count', 0),
            'technical_fork': metrics.get('fork_count', 0),
            'activity': activity.get('activity_score', 0),
            'active_dates_and_times': activity.get('commits_total', 0) / 100,
            'bus_factor': activity.get('contributors_total', 0),
            'new_contributors': activity.get('contributors_total', 0) / 10,
            'contributor_email_suffixes': len(repo.get('contributor_network', [])) / 10,
            'code_change_lines_sum': activity.get('commits_total', 0) * 10,
            'attention': metrics.get('star_count', 0) / 10,
            
            'created_at': timeline.get('created_at', ''),
            'updated_at': timeline.get('updated_at', ''),
            'pushed_at': timeline.get('pushed_at', '')
        }
        
        repo_list.append(repo_data)
    
    df = pd.DataFrame(repo_list)
    return df

def preprocess_data(df):
    df = df.fillna(0)
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        df[col] = df[col].apply(lambda x: max(0, x))
    
    return df

def normalize_to_0_10(df, cols):
    scaler = MinMaxScaler(feature_range=(0, 10))
    df_scaled = df.copy()
    df_scaled[cols] = scaler.fit_transform(df[cols])
    return df_scaled, scaler

def calculate_priority(df):
    df["star_fork_avg"] = (df["stars"] + df["technical_fork"]) / 2
    basic_sub_cols = ["openrank", "star_fork_avg", "activity"]
    df, basic_scaler = normalize_to_0_10(df, basic_sub_cols)
    
    df.rename(columns={
        "openrank": "norm_openrank",
        "star_fork_avg": "norm_star_fork_avg",
        "activity": "norm_activity"
    }, inplace=True)
    
    df["basic_strength_score"] = (
        df["norm_openrank"] * 0.5 +
        df["norm_star_fork_avg"] * 0.3 +
        df["norm_activity"] * 0.2
    )
    
    df["openrank_slope"] = df["norm_openrank"] / df["norm_openrank"].max() * 10
    df["activity_volatility"] = df["active_dates_and_times"] / df["active_dates_and_times"].mean() * 5
    df["star_growth_rate"] = df["stars"] / df["stars"].max() * 10
    
    temporal_sub_cols = ["openrank_slope", "activity_volatility", "star_growth_rate"]
    df, temporal_scaler = normalize_to_0_10(df, temporal_sub_cols)
    
    df["temporal_dynamic_score"] = (
        df["openrank_slope"] * 0.4 +
        df["activity_volatility"] * 0.3 +
        df["star_growth_rate"] * 0.3
    )
    
    df["ecosystem_correlation"] = (df["bus_factor"] + df["new_contributors"]) / 2
    df["contributor_strength"] = (df["contributor_email_suffixes"] + df["code_change_lines_sum"]) / df["code_change_lines_sum"].max() * 10
    df["semantic_similarity"] = df["attention"] / df["attention"].max() * 10
    
    relation_sub_cols = ["ecosystem_correlation", "contributor_strength", "semantic_similarity"]
    df, relation_scaler = normalize_to_0_10(df, relation_sub_cols)
    
    df["relationship_enhancement_score"] = (
        df["ecosystem_correlation"] * 0.5 +
        df["contributor_strength"] * 0.3 +
        df["semantic_similarity"] * 0.2
    )
    
    df["final_priority_score"] = (
        df["basic_strength_score"] * W1 +
        df["temporal_dynamic_score"] * W2 +
        df["relationship_enhancement_score"] * W3
    )
    
    return df

def save_results(df, output_path):
    output_cols = [
        "repo_name",
        "owner",
        "repo_name_short",
        "language",
        "description",
        "html_url",
        "norm_openrank", "norm_star_fork_avg", "norm_activity",
        "openrank_slope", "activity_volatility", "star_growth_rate",
        "ecosystem_correlation", "contributor_strength", "semantic_similarity",
        "basic_strength_score", "temporal_dynamic_score", "relationship_enhancement_score",
        "final_priority_score"
    ]
    
    df_output = df[output_cols].round(2)
    
    df_output = df_output.sort_values("final_priority_score", ascending=False)
    
    df_output.to_csv(output_path, index=False, encoding="utf-8")
    
    return df_output

def main():
    print("开始重新计算仓库优先度...")
    
    print(f"正在从 {INPUT_JSON} 提取仓库数据...")
    df = extract_repo_data(INPUT_JSON)
    print(f"提取完成：共 {len(df)} 个仓库")
    
    print("正在预处理数据...")
    df = preprocess_data(df)
    print("预处理完成")
    
    print("正在计算仓库优先度...")
    df = calculate_priority(df)
    print("优先度计算完成")
    
    print(f"正在保存结果到 {OUTPUT_CSV}...")
    df_output = save_results(df, OUTPUT_CSV)
    print("保存完成")
    
    print("\n前10个仓库的优先度结果预览：")
    print(df_output[['repo_name', 'final_priority_score', 'basic_strength_score', 'temporal_dynamic_score', 'relationship_enhancement_score']].head(10))
    
    print(f"\n所有仓库的优先度已重新计算完成！结果保存在 {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
