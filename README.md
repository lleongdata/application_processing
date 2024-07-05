# The main file is process_applications.py. Please run this python file first 

# The input files need to be dropped into applications_datasets.
# The output files will be in 2 folders, successful and unsuccessful. The successful membership files are formatted.

# There is a date-timestamp on each of the output files created, so that you will know which batch it is.
# it uses GitHub actions to schedule the run of the script every hour. 

FAQ: 

1. How are the successful applications selected?
It is done in process_applications.py in the code segment below:
# Determine successful and unsuccessful applications
successful_apps = df[
    df['name'].notna() & 
    df['email'].apply(is_valid_email) & 
    df['mobile_no'].apply(is_valid_mobile) & 
    df['date_of_birth'].apply(lambda dob: is_above_18(dob, reference_date))
]


2. How is the formatting into the defined manner for successful applications done? 
The formatting is done in the code segment below: 
# Format successful applications dataset
successful_apps['first_name'], successful_apps['last_name'] = zip(*successful_apps['name'].apply(process_name))
successful_apps['date_of_birth'] = successful_apps['date_of_birth'].apply(parse_date).dt.strftime('%Y%m%d')
successful_apps['above_18'] = True
successful_apps['membership_id'] = successful_apps.apply(
    lambda row: generate_membership_id(row['last_name'], row['date_of_birth']), axis=1
)


3. Where is the check for: Application mobile number is 8 digits?
The check is done by using the len function to check if the length of mobile_no is exactly 8.
def is_valid_mobile(mobile_no):
    return len(str(mobile_no)) == 8


4. Where is the check for Applicant is over 18 years old as of 1 Jan 2022?
First we check the dob field against various possible formats e.g. '%Y-%m-%d', '%Y/%m/%d'.
Then we use datetime.strptime to transform dob into a datetime object.
Lastly we check if the dob is above 18 years old by changing the date into days and dividing it by 365 to convert to years.

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

def is_above_18(dob, reference date):
    return (reference_date - parse_date(dob)).days // 365 >= 18


5. Where is the check for Applicant has a valid email (email ends with @emailprovider.com or @emailprovider.net)?
We use the re.match function to match it against the regex pattern [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|net)$'
That represents any combination of characters with an @ symbol, again by any combination of characters, and ending with .com or .net

# Email check
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|net)$'
    return re.match(pattern, email) is not None


6. How do I split the names into first name and last name? 
The names are split using the function name split(), and then putting the first part as the first name and second part as last name. 

How do we account for the appearance of Mr., Mrs. Dr. and Ms. in the names?
The names are cleaned by the below function which removes these titles using the re.sub function. 

def process_name(name):
    # Remove Mr., Mrs., Dr., or Ms.
    name = re.sub(r'^(Mr\.|Mrs\.|Dr\.|Ms\.)\s+', '', name)
    # Split the name
    parts = name.split()
    first_name = parts[0] if len(parts) > 0 else ''
    last_name = parts[1] if len(parts) > 1 else ''
    return first_name, last_name


7. How do I format the birthday field into YYYYMMDD?
I use dt.strftime() and the format '%Y%m%d' on the output of parse_date 
successful_apps['date_of_birth'] = successful_apps['date_of_birth'].apply(parse_date).dt.strftime('%Y%m%d')


8. How did I remove any rows which do not have a name field 
I use df['name'].notna() to filter out empty name fields


9. How did I create a new field named above_18 based on the applicant's birthday
I deduct datetime(2022, 1, 1) from the birthday to obtain the number of days, convert it to years, then check if it is above 18

def is_above_18(dob, reference_date):
    return (reference_date - parse_date(dob)).days // 365 >= 18

df['date_of_birth'].apply(lambda dob: is_above_18(dob, reference_date))


10. How did I generate the Membership IDs for successful applications?
Firstly use the hashlib.sha256 function to encode the dob, then obtain the hash with .hexdigest(). 
Secondly I Truncate the hash to only 5 digits with hash_digest[:5].
Lastly, I return the last name and hash appended together with underscore.
def generate_membership_id(last_name, dob):
    hash_object = hashlib.sha256(dob.encode())
    hash_digest = hash_object.hexdigest()
    return f"{last_name}_{hash_digest[:5]}"


11. How did I consolidate these datasets and output the successful applications into a folder?
I used the function repo.create_file to create the filenames and output to Git.

# Function to create the csv files in the repo
def create_or_update_file(folder_name, file_name, file_content, commit_message):
    # Check if folder exists
    existing_folders = [content for content in contents if content.type == "dir" and content.name == folder_name]
    if not any(existing_folders):
        repo.create_file(folder_name + '/.keep', 'Initial commit', '')
        print(f"Created folder '{folder_name}' in repository '{repo_name}'.")
    else:
        print(f"Folder '{folder_name}' already exists in repository '{repo_name}'.")

    # Create or update file
    repo.create_file(folder_name + '/' + file_name, commit_message, file_content)
    print(f"Created file '{file_name}' in folder '{folder_name}' in repository '{repo_name}'.")

# Save to CSV files

# unsuccessful_apps.to_csv(unsuccessful_filename, index=False)


12. How did I output the successful applications into a folder?
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

# Define output filenames
successful_filename = f'successful_{current_datetime}.csv'
unsuccessful_filename = f'unsuccessful_{current_datetime}.csv'
# successful_apps.to_csv(successful_filename, index=False)


13. How did I output the Unsuccessful applications into a separate folder?
I output to csv in the unsuccessful folder. 
# unsuccessful_apps.to_csv(unsuccessful_filename, index=False)


14. How did I implement the scheduling component?
A hourly.yml file contains the code to run the process_applications.py every hour. 

   on:
     schedule:
       - cron: '0 * * * *'  # Runs every hour
This yml file is located in the folder application_processing/.github/workflows/.

The hourly triggering logs of the python file can be seen in GitHub actions tab: 
https://github.com/lleongdata/application_processing/actions