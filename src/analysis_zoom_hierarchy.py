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

# 2. Cohort Definition
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
    """
    Finds the correct RegionName in the dataframe.
    Handles exact matches and specific fuzzy cases like 'Bend, OR' -> 'Bend-Redmond, OR'.
    """
    if target_city in available_regions:
        return target_city
    
    # Specific fuzzy match logic
    if target_city == "Bend, OR":
        # Look for Bend-Redmond
        matches = [r for r in available_regions if "Bend" in r and "OR" in r]
        if matches:
            print(f"Fuzzy match: '{target_city}' -> '{matches[0]}'")
            return matches[0]
            
    print(f"Warning: Could not find region for '{target_city}'")
    return None

def process_and_aggregate(df):
    available_regions = df['RegionName'].unique()
    
    # Map cohorts to actual region names found in data
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
    
    # Normalize (March 2020 Baseline)
    baseline_date = pd.Timestamp('2020-03-31')
    normalized_dfs = []
    
    for city in df_long['RegionName'].unique():
        city_data = df_long[df_long['RegionName'] == city].copy().sort_values('Date')
        try:
            baseline_val = city_data.loc[city_data['Date'] == baseline_date, 'ZHVI'].values[0]
            city_data['PctChange'] = ((city_data['ZHVI'] - baseline_val) / baseline_val) * 100
            
            # Assign Cohort
            for cohort_name, actual_cities in cohort_map.items():
                if city in actual_cities:
                    city_data['Cohort'] = cohort_name
                    break
            
            normalized_dfs.append(city_data)
        except IndexError:
            print(f"Warning: Baseline not found for {city}")
            
    df_norm = pd.concat(normalized_dfs)
    
    # Aggregate: Group by Date and Cohort
    df_agg = df_norm.groupby(['Date', 'Cohort'])['PctChange'].agg(['mean', 'min', 'max']).reset_index()
    return df_agg, df_norm

# 3. Visualization
def plot_hierarchy(df_agg):
    plt.figure(figsize=(12, 8))
    
    # Filter for plot range
    df_plot = df_agg[df_agg['Date'] >= '2018-01-01']
    
    # Define styles
    styles = {
        "Cohort A: Wealth Exporters (The Core)": {"color": "tab:blue", "style": "--"},
        "Cohort B: Major Sunbelt Hubs (Urban Importers)": {"color": "tab:orange", "style": "-"},
        "Cohort C: Nature Enclaves (Scenic Importers)": {"color": "tab:green", "style": "-"}
    }
    
    for cohort in COHORTS.keys():
        subset = df_plot[df_plot['Cohort'] == cohort]
        style = styles.get(cohort, {"color": "gray", "style": "-"})
        
        # Plot Mean Line
        plt.plot(subset['Date'], subset['mean'], label=cohort, color=style['color'], linestyle=style['style'], linewidth=2.5)
        
        # Plot Shaded Range
        plt.fill_between(subset['Date'], subset['min'], subset['max'], color=style['color'], alpha=0.15)
        
    plt.title('The "Zoom Town" Hierarchy: Housing Inflation Shock (2018-2025)')
    plt.ylabel('Cumulative % Change (Baseline: March 2020)')
    plt.xlabel('Year')
    plt.axhline(0, color='black', linewidth=0.8)
    plt.axvline(pd.Timestamp('2020-03-31'), color='red', linestyle=':', alpha=0.5)
    
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('output/zoom_town_hierarchy.png')
    print("Chart saved to output/zoom_town_hierarchy.png")

# 4. Summary
def generate_summary(df_agg):
    latest_date = df_agg['Date'].max()
    latest_stats = df_agg[df_agg['Date'] == latest_date]
    
    summary = f"""
    ZOOM TOWN HIERARCHY SUMMARY
    ===========================
    Analysis Date: {latest_date.strftime('%Y-%m-%d')}
    """
    
    for cohort in COHORTS.keys():
        stats = latest_stats[latest_stats['Cohort'] == cohort]
        if not stats.empty:
            mean_val = stats['mean'].values[0]
            min_val = stats['min'].values[0]
            max_val = stats['max'].values[0]
            summary += f"\n    {cohort}:\n      - Mean Growth: {mean_val:.2f}%\n      - Range: {min_val:.2f}% to {max_val:.2f}%\n"
            
    with open('output/cohort_summary.txt', 'w') as f:
        f.write(summary)
    print("Summary saved to output/cohort_summary.txt")
    print(summary)

def main():
    df = fetch_data(DATA_URL)
    df_agg, df_norm = process_and_aggregate(df)
    plot_hierarchy(df_agg)
    generate_summary(df_agg)

if __name__ == "__main__":
    main()
