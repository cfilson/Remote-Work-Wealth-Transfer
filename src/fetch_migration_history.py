import pandas as pd
import matplotlib.pyplot as plt
import requests
import io

# Census API Endpoint (Vintage 2019 Population Estimates - Components of Change)
CENSUS_URL = "https://api.census.gov/data/2019/pep/components"

# Cohorts (Same as Zoom Town Analysis)
COHORTS = {
    "Cohort A: Wealth Exporters (The Core)": [
        "San Francisco", "New York", "San Jose", "Boston",
        "Los Angeles", "Washington", "Seattle", "Chicago"
    ],
    "Cohort B: Major Sunbelt Hubs (Urban Importers)": [
        "Austin", "Phoenix", "Miami", "Tampa",
        "Dallas", "Atlanta", "Nashville", "Las Vegas", "Charlotte"
    ],
    "Cohort C: Nature Enclaves (Scenic Importers)": [
        "Bozeman", "Bend", "Coeur d'Alene", "Asheville",
        "Reno", "Spokane", "Portland", "Knoxville"
    ]
}

def fetch_census_data():
    print("Fetching Census Data (Vintage 2019 Components)...")
    
    # Variables: NAME, RNETMIG (Net Migration Rate), PERIOD_CODE
    # PERIOD_CODE: 3=2011, ..., 11=2019
    params = {
        "get": "NAME,RNETMIG,PERIOD_CODE",
        "for": "metropolitan statistical area/micropolitan statistical area:*"
    }
    
    try:
        r = requests.get(CENSUS_URL, params=params)
        r.raise_for_status()
        data = r.json()
        
        headers = data[0]
        rows = data[1:]
        df = pd.DataFrame(rows, columns=headers)
        return df
    except Exception as e:
        print(f"Error fetching Census data: {e}")
        return pd.DataFrame()

def process_data(df):
    # Convert columns to numeric
    df['RNETMIG'] = pd.to_numeric(df['RNETMIG'], errors='coerce')
    df['PERIOD_CODE'] = pd.to_numeric(df['PERIOD_CODE'], errors='coerce')
    print(f"Unique PERIOD_CODEs found: {sorted(df['PERIOD_CODE'].unique())}")
    
    # Filter for Years 2011-2019 (PERIOD_CODE 3-11)
    # Map: 3->2011, 4->2012, ..., 11->2019
    period_map = {
        3: 2011, 4: 2012, 5: 2013, 6: 2014, 7: 2015, 
        8: 2016, 9: 2017, 10: 2018, 11: 2019
    }
    
    df = df[df['PERIOD_CODE'].isin(period_map.keys())].copy()
    df['Year'] = df['PERIOD_CODE'].map(period_map)
    
    # Filter and Assign Cohorts
    cohort_data = []
    
    for cohort_name, cities in COHORTS.items():
        for city in cities:
            # Fuzzy match city name in 'NAME' column
            match = df[df['NAME'].str.contains(city, case=False, na=False)]
            
            if not match.empty:
                # Handle specific cases
                if city == "Portland":
                    # User meant Portland, ME (Cohort C)
                    # Portland-South Portland, ME
                    match = match[match['NAME'].str.contains("ME")]
                elif city == "Washington":
                    # Washington-Arlington-Alexandria, DC-VA-MD-WV
                    match = match[match['NAME'].str.contains("DC")]
                
                if not match.empty:
                    # Take the first match (usually the correct Metro Area)
                    # Iterate over the years for this city
                    city_rows = match.copy()
                    for _, row in city_rows.iterrows():
                        cohort_data.append({
                            "Cohort": cohort_name,
                            "City": city,
                            "Year": row['Year'],
                            "NetMigrationRate": row['RNETMIG']
                        })
            else:
                print(f"Warning: Could not find Census data for {city}")
                
    return pd.DataFrame(cohort_data)

def plot_trends(df_long):
    plt.figure(figsize=(12, 8))
    
    # Aggregate by Cohort and Year
    df_agg = df_long.groupby(['Cohort', 'Year'])['NetMigrationRate'].mean().reset_index()
    
    colors = {
        "Cohort A: Wealth Exporters (The Core)": "tab:blue",
        "Cohort B: Major Sunbelt Hubs (Urban Importers)": "tab:orange",
        "Cohort C: Nature Enclaves (Scenic Importers)": "tab:green"
    }
    
    for cohort in COHORTS.keys():
        subset = df_agg[df_agg['Cohort'] == cohort]
        plt.plot(subset['Year'], subset['NetMigrationRate'], label=cohort, color=colors[cohort], linewidth=2.5, marker='o')
        
    plt.axhline(0, color='black', linewidth=1, linestyle='-')
    plt.title('The "Golden Handcuffs" Breached: Pre-Pandemic Net Migration Rates (2011-2019)')
    plt.ylabel('Net Migration Rate (per 1,000 residents)')
    plt.xlabel('Year')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Annotation for Exporters
    # Use the latest available year
    max_year = df_agg['Year'].max()
    exporters_latest = df_agg[(df_agg['Cohort'] == "Cohort A: Wealth Exporters (The Core)") & (df_agg['Year'] == max_year)]['NetMigrationRate'].values[0]
    
    if exporters_latest < 0:
        plt.annotate('Negative Migration\nBefore COVID', xy=(max_year, exporters_latest), 
                     xytext=(max_year - 2, exporters_latest - 2),
                     arrowprops=dict(facecolor='black', shrink=0.05))
    
    plt.tight_layout()
    plt.savefig('output/migration_pre_trend.png')
    print("Chart saved to output/migration_pre_trend.png")

def main():
    df_census = fetch_census_data()
    if not df_census.empty:
        df_processed = process_data(df_census)
        if not df_processed.empty:
            # Save CSV
            df_processed.to_csv('data/migration_history_2011_2019.csv', index=False)
            print("Data saved to data/migration_history_2011_2019.csv")
            
            plot_trends(df_processed)
        else:
            print("No data processed.")
    else:
        print("Failed to fetch Census data.")

if __name__ == "__main__":
    main()
