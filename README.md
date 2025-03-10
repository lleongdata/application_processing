### Senior Data Engineer Tech Challenge Section 1: Data Pipelines 
* The main file is process_applications.py.  This file is located at the root directory of the repository.
* This python file is activated by a yaml file (hourly.yml) that runs at hourly intervals. 

* The file hourly.yml is in the sub-folder .github/workflows

* The input files need to be dropped into the folder applications_datasets. Currently, the samples given are in this folder. 

* The output files will be in 2 folders, successful and unsuccessful. The successful membership files are formatted.
* There is a date-timestamp on each of the output files created, e..g, successful_05Jul2024-0155.csv so that you will know which batch it is.


### FAQ

1. How are the successful applications selected?
- The applications are filtered in process_applications.py in the segment below. I have provided the comments in the python file. 
```
successful_apps = df[
    df['name'].notna() & 
    df['email'].apply(is_valid_email) & 
    df['mobile_no'].apply(is_valid_mobile) & 
    df['date_of_birth'].apply(lambda dob: is_above_18(dob, reference_date))
]
```

2. How is the formatting into the defined manner for successful applications done? 
- The formatting is done in the code segment below: 
```
successful_apps['first_name'], successful_apps['last_name'] = zip(*successful_apps['name'].apply(process_name))
successful_apps['date_of_birth'] = successful_apps['date_of_birth'].apply(parse_date).dt.strftime('%Y%m%d')
successful_apps['above_18'] = True
successful_apps['membership_id'] = successful_apps.apply(
    lambda row: generate_membership_id(row['last_name'], row['date_of_birth']), axis=1
)
```

3. Where is the check for: Application mobile number is 8 digits?
- The check is done by using the len function to check if the length of mobile_no is exactly 8.
```
def is_valid_mobile(mobile_no):
    return len(str(mobile_no)) == 8
```

4. Where is the check for Applicant is over 18 years old as of 1 Jan 2022?
- First we check the dob field against various possible formats e.g. '%Y-%m-%d', '%Y/%m/%d'.
- Then we use datetime.strptime to transform dob into a datetime object.
- Lastly we check if the dob is above 18 years old by changing the date into days and dividing it by 365 to convert to years.
```
def parse_date(dob):
    if isinstance(dob, datetime):
        return dob

    for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y', '%m-%d-%Y', '%m/%d/%Y', '%Y%m%d'):
        try:
            return datetime.strptime(str(dob), fmt)
        except ValueError:
            pass
    
    raise ValueError(f"Date format for '{dob}' is not supported.")

def is_above_18(dob, reference date):
    return (reference_date - parse_date(dob)).days // 365 >= 18
```

5. Where is the check for Applicant has a valid email?
- We use the re.match function to match it against the regex pattern [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|net)$'
- That represents the combination of characters, followed by @ symbol, and again the combination of characters, and ending with .com or .net

```
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|net)$'
    return re.match(pattern, email) is not None
```

6. How did I split the names into first name and last name? How did I account for the appearance of Mr., Mrs. Dr. and Ms. in the names?
- The names are split using the function name split(), and then putting the first part as the first name and second part as last name. 
- The names are cleaned by the below function which removes these titles using the re.sub function. 

```
def process_name(name):
    # Remove Mr., Mrs., Dr., or Ms.
    name = re.sub(r'^(Mr\.|Mrs\.|Dr\.|Ms\.)\s+', '', name)
    # Split the name
    parts = name.split()
    first_name = parts[0] if len(parts) > 0 else ''
    last_name = parts[1] if len(parts) > 1 else ''
    return first_name, last_name
```

7. How did I format the birthday field into YYYYMMDD?
- I used dt.strftime() and the format '%Y%m%d' on the output of parse_date 

```
successful_apps['date_of_birth'] = successful_apps['date_of_birth'].apply(parse_date).dt.strftime('%Y%m%d')
```

8. How did I remove any rows which do not have a name field 
- I used df['name'].notna() to filter out empty name fields.


9. How did I create a new field named above_18 based on the applicant's birthday
- I deducted datetime(2022, 1, 1) from the birthday to obtain the number of days, convert it to years, then check if it is above 18
```
def is_above_18(dob, reference_date):
    return (reference_date - parse_date(dob)).days // 365 >= 18

df['date_of_birth'].apply(lambda dob: is_above_18(dob, reference_date))
```

10. How did I generate the Membership IDs for successful applications?
- Firstly use the hashlib.sha256 function to encode the dob, then obtain the hash with .hexdigest(). 
- Secondly I Truncate the hash to only 5 digits with hash_digest[:5].
- Lastly, I return the last name and hash appended together with underscore.
```
def generate_membership_id(last_name, dob):
    hash_object = hashlib.sha256(dob.encode())
    hash_digest = hash_object.hexdigest()
    return f"{last_name}_{hash_digest[:5]}"
```

11. How did I consolidate these datasets and output the successful applications into a folder?
- I used the function repo.create_file to create the filenames and output to Git.

```
def create_or_update_file(folder_name, file_name, file_content, commit_message):

    existing_folders = [content for content in contents if content.type == "dir" and content.name == folder_name]
    if not any(existing_folders):
        repo.create_file(folder_name + '/.keep', 'Initial commit', '')
        print(f"Created folder '{folder_name}' in repository '{repo_name}'.")
    else:
        print(f"Folder '{folder_name}' already exists in repository '{repo_name}'.")


    repo.create_file(folder_name + '/' + file_name, commit_message, file_content)
    print(f"Created file '{file_name}' in folder '{folder_name}' in repository '{repo_name}'.")

```

12. How did I output the successful applications into a folder?
- I checked if the folders existed, created the folders then output the csv files into the correct folder. 

```
folder_names = ['successful', 'unsuccessful']
existing_folders = [content for content in contents if content.type == "dir" and content.name in folder_names]

for folder_name in folder_names:
    if folder_name not in [folder.name for folder in existing_folders]:
        repo.create_file(folder_name + '/.keep', 'Initial commit', '')
        print(f"Created folder '{folder_name}' in repository '{repo_name}'.")
    else:
        print(f"Folder '{folder_name}' already exists in repository '{repo_name}'.")

successful_filename = f'successful_{current_datetime}.csv'
unsuccessful_filename = f'unsuccessful_{current_datetime}.csv'
successful_apps.to_csv(successful_filename, index=False)
```

13. How did I output the unsuccessful applications into a separate folder?
- I output to csv in the unsuccessful folder. 
```
unsuccessful_apps.to_csv(unsuccessful_filename, index=False)
```

14. How did I implement the scheduling component?
- A hourly.yml file contains the code to run the process_applications.py every hour. 

```
   on:
     schedule:
       - cron: '0 * * * *'  # Runs every hour
```
- This yml file is located in the folder application_processing/.github/workflows/.
- The hourly triggering logs of the python file can be seen in GitHub actions tab: 
- https://github.com/lleongdata/application_processing/actions