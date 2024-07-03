import os
import pandas as pd
import hashlib
from datetime import datetime
import re

# Create directories if they don't exist
os.makedirs('successful', exist_ok=True)
os.makedirs('unsuccessful', exist_ok=True)

# Load the datasets
df1 = pd.read_csv('applications_dataset_1.csv')
df2 = pd.read_csv('applications_dataset_2.csv')

# Combine the datasets
df = pd.concat([df1, df2], ignore_index=True)

# Helper functions
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|net)$'
    return re.match(pattern, email) is not None

def is_valid_mobile(mobile_no):
    return len(str(mobile_no)) == 8

def parse_date(dob):
    for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y', '%m-%d-%Y', '%m/%d/%Y'):
        try:
            return datetime.strptime(dob, fmt)
        except ValueError:
            pass
    raise ValueError(f"Date format for '{dob}' is not supported.")

def is_above_18(dob, reference_date):
    return (reference_date - parse_date(dob)).days // 365 >= 18

def generate_membership_id(last_name, dob):
    hash_object = hashlib.sha256(dob.encode())
    hash_digest = hash_object.hexdigest()
    return f"{last_name}_{hash_digest[:5]}"

def process_name(name):
    # Remove Mr., Mrs., Dr., or Ms.
    name = re.sub(r'^(Mr\.|Mrs\.|Dr\.|Ms\.)\s+', '', name)
    # Split the name
    parts = name.split()
    first_name = parts[0] if len(parts) > 0 else ''
    last_name = parts[1] if len(parts) > 1 else ''
    return first_name, last_name

# Set the reference date
reference_date = datetime(2022, 1, 1)

# Determine successful and unsuccessful applications
successful_apps = df[
    df['name'].notna() & 
    df['email'].apply(is_valid_email) & 
    df['mobile_no'].apply(is_valid_mobile) & 
    df['date_of_birth'].apply(lambda dob: is_above_18(dob, reference_date))
]

unsuccessful_apps = df.drop(successful_apps.index)

# Process successful applications
successful_apps = successful_apps.copy()
successful_apps['first_name'], successful_apps['last_name'] = zip(*successful_apps['name'].apply(process_name))
successful_apps['date_of_birth'] = successful_apps['date_of_birth'].apply(parse_date).dt.strftime('%Y%m%d')
successful_apps['above_18'] = True
successful_apps['membership_id'] = successful_apps.apply(
    lambda row: generate_membership_id(row['last_name'], row['date_of_birth']), axis=1
)

# Reorder and select columns for successful applications
successful_apps = successful_apps[['first_name', 'last_name', 'email', 'date_of_birth', 'mobile_no', 'above_18', 'membership_id']]

# Save the successful and unsuccessful applications to separate CSV files
successful_apps.to_csv('successful/successful_applications.csv', index=False)
unsuccessful_apps.to_csv('unsuccessful/unsuccessful_applications.csv', index=False)
