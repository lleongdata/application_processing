import os
import pandas as pd
import hashlib
import datetime
import re
from glob import glob

def is_valid_email(email):
    return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|net)$", email)

def is_above_18(dob, reference_date):
    return (reference_date - dob).days >= 18 * 365

def process_name(name):
    name = re.sub(r'^(Mr\.|Mrs\.|Dr\.|Ms\.)\s*', '', name)
    parts = name.split()
    first_name = parts[0] if len(parts) > 0 else ''
    last_name = parts[1] if len(parts) > 1 else ''
    return first_name, last_name

def parse_date(dob):
    for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y', '%m-%d-%Y', '%m/%d/%Y'):
        try:
            return datetime.datetime.strptime(dob, fmt)
        except ValueError:
            pass
    raise ValueError(f"Date format for '{dob}' is not supported.")

# Read all CSV files in the applications_datasets folder
csv_files = glob('applications_datasets/*.csv')
dataframes = [pd.read_csv(file) for file in csv_files]
combined_df = pd.concat(dataframes, ignore_index=True)

# Filter valid and invalid applications
reference_date = datetime.datetime(2022, 1, 1)
combined_df['valid'] = combined_df.apply(lambda row: (
    len(str(row['mobile_no'])) == 8 and
    is_valid_email(row['email']) and
    row['name'].strip() != '' and
    is_above_18(parse_date(row['date_of_birth']), reference_date)
), axis=1)

successful_apps = combined_df[combined_df['valid']].copy()
unsuccessful_apps = combined_df[~combined_df['valid']].copy()

# Process successful applications
successful_apps['date_of_birth'] = successful_apps['date_of_birth'].apply(lambda dob: parse_date(dob).strftime('%Y%m%d'))
successful_apps[['first_name', 'last_name']] = successful_apps['name'].apply(lambda name: pd.Series(process_name(name)))
successful_apps['above_18'] = successful_apps['date_of_birth'].apply(lambda dob: is_above_18(parse_date(dob), reference_date))

successful_apps['membership_id'] = successful_apps.apply(
    lambda row: f"{row['last_name']}_{hashlib.sha256(row['date_of_birth'].encode()).hexdigest()[:5]}", axis=1)

# Get current date and time for filenames
current_datetime = datetime.datetime.now().strftime('%d%b%Y-%H%M')

# Define output filenames
successful_filename = f'applications_datasets/successful_{current_datetime}.csv'
unsuccessful_filename = f'applications_datasets/unsuccessful_{current_datetime}.csv'

# Save to CSV files
successful_apps.to_csv(successful_filename, index=False)
unsuccessful_apps.to_csv(unsuccessful_filename, index=False)
