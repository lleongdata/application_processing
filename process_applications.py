import os
import pandas as pd
import hashlib
from datetime import datetime
import re
from glob import glob
from github import Github

# Read all CSV files in the applications_datasets folder
csv_files = glob('applications_datasets/*.csv')
dataframes = [pd.read_csv(file) for file in csv_files]
df = pd.concat(dataframes, ignore_index=True)

# Helper functions
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|net)$'
    return re.match(pattern, email) is not None

def is_valid_mobile(mobile_no):
    return len(str(mobile_no)) == 8

def parse_date(dob):
    # Check if dob is already a datetime object
    if isinstance(dob, datetime):
        return dob
    
    # Try parsing with additional formats including YYYYMMDD
    for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y', '%m-%d-%Y', '%m/%d/%Y', '%Y%m%d'):
        try:
            return datetime.strptime(str(dob), fmt)
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



# GitHub credentials
username = 'lleongdata'
repo_name = 'application_processing'
access_token = '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'

# Initialize PyGitHub
g = Github(access_token)

# Get the user and repository
user = g.get_user(username)
repo = user.get_repo(repo_name)

# List contents of the repository
contents = repo.get_contents("")

# Check if folders already exist
folder_names = ['successful', 'unsuccessful']
existing_folders = [content for content in contents if content.type == "dir" and content.name in folder_names]

# Create folders if they don't exist
for folder_name in folder_names:
    if folder_name not in [folder.name for folder in existing_folders]:
        repo.create_file(folder_name + '/.keep', 'Initial commit', '')
        print(f"Created folder '{folder_name}' in repository '{repo_name}'.")
    else:
        print(f"Folder '{folder_name}' already exists in repository '{repo_name}'.")



# Set the reference date
reference_date = datetime(2022, 1, 1)

# Convert date_of_birth to datetime objects
df['date_of_birth'] = df['date_of_birth'].apply(parse_date)

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

# Get current date and time for filenames
current_datetime = datetime.now().strftime('%d%b%Y-%H%M')

# Define output filenames
successful_filename = f'successful_{current_datetime}.csv'
unsuccessful_filename = f'unsuccessful_{current_datetime}.csv'

# Save to CSV files
# successful_apps.to_csv(successful_filename, index=False)
# unsuccessful_apps.to_csv(unsuccessful_filename, index=False)





# List contents of the repository
contents = repo.get_contents("")
print(contents)

# Function to create or update file in repo
def create_or_update_file(folder_name, file_name, file_content, commit_message):
    # Check if folder exists
    existing_folders = [content for content in contents if content.type == "dir" and content.name == folder_name]
    if not existing_folders:
        repo.create_file(folder_name + '/.keep', 'Initial commit', '')
        print(f"Created folder '{folder_name}' in repository '{repo_name}'.")

    # Create or update file
    repo.create_file(folder_name + '/' + file_name, commit_message, file_content)
    print(f"Created file '{file_name}' in folder '{folder_name}' in repository '{repo_name}'.")




# Convert DataFrames to CSV format
successful_csv = successful_apps.to_csv(index=False)
unsuccessful_csv = unsuccessful_apps.to_csv(index=False)

# Create or update files in respective folders
create_or_update_file('successful', successful_filename, successful_csv, f'Updated {successful_filename}')
create_or_update_file('unsuccessful', unsuccessful_filename, unsuccessful_csv, f'Updated {unsuccessful_filename}')
