import pandas as pd
import re
import pandas as pd
import numpy as np
from urllib.parse import urlparse

def extract_extension(url):
    try:
        domain = urlparse(url).netloc
        return "." + domain.split(".")[-1]   # last part → com, ch, de ...
    except:
        return None

def filter_rows(df: pd.DataFrame) -> pd.DataFrame:
    pattern = r"REFUGEE"
    mask_themes = df["THEMES"].str.contains(pattern, flags=re.IGNORECASE, na=False)

    countries = ["Switzerland", "Germany", "Canada", "United Kingdom"]
    #pattern = r"(" + "|".join(map(re.escape, countries)) + r")"
    #mask_locations = df["LOCATIONS"].str.contains(pattern, case=False, na=False)

    mask = mask_themes #& mask_locations

    def find_countries(text):
        return [w for w in countries if w in text]
    
    filtered =  df[mask].copy()
    filtered["COUNTRY"] = filtered["LOCATIONS"].apply(find_countries)

    tld_pattern = r"(?:\.ch|\.de|\.co\.uk|\.ca)(?=/|$)"
    mask_url = df["SOURCES"].str.contains(tld_pattern, case=True, na=False)

    filtered = filtered[mask_url].copy()
    
    filtered["DOMAIN_EXT"] = filtered["SOURCES"].apply(extract_extension)


    return filtered


#sugma balls
def filter_rows_2(df: pd.DataFrame) -> pd.DataFrame:
    # Define the filters
    refugee_ethnic_codes = ['UKR', 'SYR']  # Ukrainian and Syrian ethnic codes
    refugee_type_code = 'REF'  # General refugee role
    #host_countries = ['CAN', 'CHE', 'DEU', 'GBR']  # Canada, Switzerland, Germany, UK
    refugee_event_codes = [
        73, 233, 75, 333,  # Humanitarian aid and asylum
        1033, 1055,  # Demands for aid and involvement
        42, 43, 44,  # Movement and visits
        14, 343, 833  # Protests and rights
    ]

    ref_syr = (
        df['Actor1EthnicCode'].isin(['SYR']) |
        df['Actor2EthnicCode'].isin(['SYR']) |
        df['Actor1CountryCode'].isin(['SYR']) |
        df['Actor2CountryCode'].isin(['SYR']) 
    )
    ref_ukr = (
        df['Actor1EthnicCode'].isin(['UKR']) |
        df['Actor2EthnicCode'].isin(['UKR']) |
        df['Actor1CountryCode'].isin(['UKR']) |
        df['Actor2CountryCode'].isin(['UKR']) 
    )
    # Filter for Ukrainian/Syrian refugees OR general refugee role
    refugee_mask = ref_syr | ref_ukr
    df["RegionTopic"] = [""]*len(df)
    df.loc[ref_syr, "RegionTopic"] = "SYR"
    df.loc[ref_ukr, "RegionTopic"] = "UKR"

    hanspeter = (df['Actor1Type1Code'].str.contains(refugee_type_code, na=False) |
                    df['Actor2Type1Code'].str.contains(refugee_type_code, na=False))

    # Filter for host countries (CAN, CHE, DEU, GBR)
    #host_mask = (df['Actor1Geo_CountryCode'].isin(host_countries) | df['Actor2Geo_CountryCode'].isin(host_countries) |  df['ActionGeo_CountryCode'].isin(host_countries))

    # Filter for refugee-related events
    event_mask = df['EventCode'].isin(refugee_event_codes)

    # Combine all filters
    filtered_df = df[refugee_mask & (event_mask | hanspeter)].copy()

    filtered_df["DOMAIN_EXT"] = filtered_df["SOURCEURLS"].apply(extract_extension)
    # Display the results
    
    # url_mask = filtered_df["DOMAIN_EXT"].isin([".ch", ".de", ".co.uk", ".ca", "com"]) # Filter for specific domain extensions for the countries i want - NOT ACTIVE
                                               
    print(f"Found {len(filtered_df)} records.")
    filtered_df.head()
    return filtered_df

def remove_duplicate_sourceurls(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates(subset="SOURCEURLS", keep="first").reset_index(drop=True)
