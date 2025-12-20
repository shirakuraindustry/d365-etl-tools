import requests
import pandas as pd

# Dataverse API URL and credentials
dataverse_url = "https://<your-dataverse-instance>.api.crm.dynamics.com/api/data/v9.2/"
table_name = "accounts"  # Replace with your table name
access_token = "<your-access-token>"  # Replace with your access token

# Headers for the API request
headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json"
}

# Fetch data from Dataverse
response = requests.get(f"{dataverse_url}{table_name}", headers=headers)

if response.status_code == 200:
    data = response.json().get("value", [])
    df = pd.DataFrame(data)
    print(df.head())  # Display the first few rows of the data
    df.to_csv(f"{table_name}.csv", index=False)  # Save data to a CSV file
    print(f"Data saved to {table_name}.csv")
else:
    print(f"Failed to fetch data: {response.status_code} - {response.text}")