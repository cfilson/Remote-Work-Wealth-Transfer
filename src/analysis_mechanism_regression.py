import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import io
import requests
from analysis_zoom_hierarchy import fetch_data, DATA_URL, COHORTS, get_region_name

# Input Paths
MIGRATION_CSV = "data/migration_history_2011_2019.csv"

def load_and_merge_data():
    print("Loading Migration Data...")
    df_mig = pd.read_csv(MIGRATION_CSV)
    
    print("Loading Housing Data...")
    df_housing = fetch_data(DATA_URL)
    
    # Process Housing Data
    # 1. Filter for Cohort A (Wealth Exporters) - The target of the hypothesis
    target_cohort = "Cohort A: Wealth Exporters (The Core)"
    target_cities = COHORTS[target_cohort]
    
    available_regions = df_housing['RegionName'].unique()
    found_regions = []
    for city in target_cities:
        r = get_region_name(city, available_regions)
        if r: found_regions.append(r)
        
    df_housing = df_housing[df_housing['RegionName'].isin(found_regions)].copy()
    
    # 2. Reshape and Filter for 2011-2019
    date_cols = [c for c in df_housing.columns if c not in ['RegionID', 'SizeRank', 'RegionName', 'RegionType', 'StateName']]
    df_long = df_housing.melt(id_vars=['RegionName'], value_vars=date_cols, var_name='Date', value_name='ZHVI')
    df_long['Date'] = pd.to_datetime(df_long['Date'])
    df_long['Year'] = df_long['Date'].dt.year
    
    # 3. Annualize (Mean ZHVI per Year)
    df_housing_annual = df_long.groupby(['RegionName', 'Year'])['ZHVI'].mean().reset_index()
    
    # 4. Merge
    # We need to map RegionName (Housing) to City (Migration)
    # Migration CSV has 'City' column (e.g. "San Francisco")
    # Housing has 'RegionName' (e.g. "San Francisco, CA")
    
    # Let's create a mapping column in df_housing_annual
    df_housing_annual['City_Key'] = df_housing_annual['RegionName'].apply(lambda x: x.split(',')[0])
    # Handle special cases if any (e.g. "Los Angeles-Long Beach..." -> "Los Angeles")
    # The migration script used fuzzy matching on the simple city name.
    # Let's try to match back.
    
    merged_data = []
    
    for city_full in target_cities:
        # city_full is "San Francisco, CA"
        # Migration data uses "San Francisco" (simple name)
        # We need to derive the simple name to match migration data
        city_simple = city_full.split(',')[0]
        
        # Migration Data for this city
        mig_subset = df_mig[(df_mig['Cohort'] == target_cohort) & (df_mig['City'] == city_simple)]
        
        # Housing Data for this city
        # Find the region name again
        region_name = get_region_name(city_full, available_regions)
        if not region_name: continue
        
        housing_subset = df_housing_annual[df_housing_annual['RegionName'] == region_name]
        
        # Merge on Year
        if not mig_subset.empty and not housing_subset.empty:
            merged = pd.merge(mig_subset, housing_subset, on='Year', how='inner')
            merged_data.append(merged)
        
    df_final = pd.concat(merged_data)
    return df_final

def run_regression(df):
    print("Running OLS Regression (Price ~ Net_Migration_Rate)...")
    
    # Y = ZHVI
    # X = NetMigrationRate
    # Add constant
    X = sm.add_constant(df['NetMigrationRate'])
    Y = df['ZHVI']
    
    model = sm.OLS(Y, X).fit()
    
    # Save Results
    with open('output/regression_results.txt', 'w') as f:
        f.write(model.summary().as_text())
    
    print("Regression results saved to output/regression_results.txt")
    print(f"Beta (Migration): {model.params['NetMigrationRate']:.4f}")
    print(f"P-Value: {model.pvalues['NetMigrationRate']:.4f}")
    print(f"R-Squared: {model.rsquared:.4f}")
    
    return model

def plot_mechanism(df):
    # Plot for San Francisco as the representative case
    city = "San Francisco"
    subset = df[df['City'] == city].sort_values('Year')
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    color = 'tab:blue'
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Housing Price (ZHVI)', color=color)
    ax1.plot(subset['Year'], subset['ZHVI'], color=color, linewidth=3, marker='o', label='Housing Price')
    ax1.tick_params(axis='y', labelcolor=color)
    
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    
    color = 'tab:red'
    ax2.set_ylabel('Net Migration Rate (per 1k)', color=color)  # we already handled the x-label with ax1
    bars = ax2.bar(subset['Year'], subset['NetMigrationRate'], color=color, alpha=0.3, label='Net Migration')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.axhline(0, color='black', linewidth=0.8, linestyle='--')
    
    plt.title(f'The "Golden Handcuffs": {city} (2011-2019)\nPrices Rose While People Left')
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.savefig('output/mechanism_chart.png')
    print("Chart saved to output/mechanism_chart.png")

def main():
    df = load_and_merge_data()
    if not df.empty:
        run_regression(df)
        plot_mechanism(df)
    else:
        print("No data found for regression.")

if __name__ == "__main__":
    main()
