import pandas as pd
import matplotlib.pyplot as plt
import io
import requests

# 1. Data Fetching
DATA_URL = "https://files.zillowstatic.com/research/public_csvs/zhvi/Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"

def fetch_data(url):
    print(f"Fetching data from {url}...")
    s = requests.get(url).content
    df = pd.read_csv(io.StringIO(s.decode('utf-8')))
    return df

# 2. Cohort Definition (Reused from analysis_zoom_hierarchy.py)
COHORTS = {
    "Cohort A: Wealth Exporters (The Core)": [
        "San Francisco, CA", "New York, NY", "San Jose, CA", "Boston, MA",
        "Los Angeles, CA", "Washington, DC", 
        "Seattle, WA", "Chicago, IL"
    ],
    "Cohort B: Major Sunbelt Hubs (Urban Importers)": [
        "Austin, TX", "Phoenix, AZ", "Miami, FL", "Tampa, FL",
        "Dallas, TX", "Atlanta, GA", "Nashville, TN", 
        "Las Vegas, NV", "Charlotte, NC"
    ],
    "Cohort C: Nature Enclaves (Scenic Importers)": [
        "Bozeman, MT", "Bend, OR", "Coeur d'Alene, ID", "Asheville, NC",
        "Reno, NV", "Spokane, WA", "Portland, ME", "Knoxville, TN"
    ]
}

def get_region_name(target_city, available_regions):
    if target_city in available_regions:
        return target_city
    
    # Specific fuzzy match logic
    if target_city == "Bend, OR":
        matches = [r for r in available_regions if "Bend" in r and "OR" in r]
        if matches:
            return matches[0]
            
    print(f"Warning: Could not find region for '{target_city}'")
    return None

def process_and_aggregate(df):
    available_regions = df['RegionName'].unique()
    
    # Map cohorts
    cohort_map = {}
    all_found_cities = []
    
    for cohort_name, cities in COHORTS.items():
        cohort_map[cohort_name] = []
        for city in cities:
            actual_name = get_region_name(city, available_regions)
            if actual_name:
                cohort_map[cohort_name].append(actual_name)
                all_found_cities.append(actual_name)
    
    # Filter Data
    df_filtered = df[df['RegionName'].isin(all_found_cities)].copy()
    
    # Reshape
    date_cols = [c for c in df.columns if c not in ['RegionID', 'SizeRank', 'RegionName', 'RegionType', 'StateName']]
    df_long = df_filtered.melt(id_vars=['RegionName'], value_vars=date_cols, var_name='Date', value_name='ZHVI')
    df_long['Date'] = pd.to_datetime(df_long['Date'])
    
    # Filter for 2010-2019
    df_long = df_long[(df_long['Date'] >= '2010-01-01') & (df_long['Date'] <= '2019-12-31')]
    
    # Normalize (Jan 2010 Baseline)
    baseline_date = pd.Timestamp('2010-01-31')
    normalized_dfs = []
    
    for city in df_long['RegionName'].unique():
        city_data = df_long[df_long['RegionName'] == city].copy().sort_values('Date')
        try:
            # Find baseline value (Jan 2010)
            # Note: Zillow dates are usually end of month
            baseline_val = city_data.loc[city_data['Date'] == baseline_date, 'ZHVI'].values[0]
            city_data['PctChange'] = ((city_data['ZHVI'] - baseline_val) / baseline_val) * 100
            
            # Assign Cohort
            for cohort_name, actual_cities in cohort_map.items():
                if city in actual_cities:
                    city_data['Cohort'] = cohort_name
                    break
            
            normalized_dfs.append(city_data)
        except IndexError:
            print(f"Warning: Baseline (Jan 2010) not found for {city}")
            
    df_norm = pd.concat(normalized_dfs)
    
    # Aggregate: Group by Date and Cohort
    df_agg = df_norm.groupby(['Date', 'Cohort'])['PctChange'].mean().reset_index()
    return df_agg

def plot_trends(df_agg):
    plt.figure(figsize=(12, 8))
    
    colors = {
        "Cohort A: Wealth Exporters (The Core)": "tab:blue",
        "Cohort B: Major Sunbelt Hubs (Urban Importers)": "tab:orange",
        "Cohort C: Nature Enclaves (Scenic Importers)": "tab:green"
    }
    
    for cohort in COHORTS.keys():
        subset = df_agg[df_agg['Cohort'] == cohort]
        plt.plot(subset['Date'], subset['PctChange'], label=cohort, color=colors[cohort], linewidth=2.5)
        
    plt.title('Parallel Trends Check: Housing Price Growth (2010-2019)')
    plt.ylabel('Cumulative % Change (Baseline: Jan 2010)')
    plt.xlabel('Year')
    plt.axhline(0, color='black', linewidth=0.8)
    
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('output/parallel_trends_check.png')
    print("Chart saved to output/parallel_trends_check.png")

def generate_stats(df_agg):
    final_date = df_agg['Date'].max()
    final_stats = df_agg[df_agg['Date'] == final_date]
    
    summary = f"""
    PRE-PANDEMIC TRENDS SUMMARY (2010-2019)
    =======================================
    Analysis Date: {final_date.strftime('%Y-%m-%d')}
    Baseline: Jan 2010
    """
    
    for cohort in COHORTS.keys():
        val = final_stats[final_stats['Cohort'] == cohort]['PctChange'].values[0]
        summary += f"\n    {cohort}: {val:.2f}% Growth"
        
    with open('output/pre_trend_stats.txt', 'w') as f:
        f.write(summary)
    print("Stats saved to output/pre_trend_stats.txt")
    print(summary)

def main():
    df = fetch_data(DATA_URL)
    df_agg = process_and_aggregate(df)
    plot_trends(df_agg)
    generate_stats(df_agg)

if __name__ == "__main__":
    main()
