## NFT Snapshot using the opensea API

This script uses the opensea api to query the capybaras country club collection https://opensea.io/collection/capybarascountryclub and take a snapshot of current holders and listed and unlisted assets on opensea.

To get an api key from them go here https://docs.opensea.io/reference/request-an-api-key

### How to run this script

1. Rename the .env_example file to .env
2. Fill in the values for the .env file with your own (the key and the contract address)
3. Run the `capy_snapshot.py` script to get the data in a csv file and 3 other csv files with the owners per trait

### Recomended steps to run/work with the files

1. Install pipenv `pip3 install pipenv`
2. Create a virtual enviroment `pipenv shell`
3. Install the dependencies `pip install -r requirements.txt`
4. Run the script `python capy_snapshot.py`

### Notes:

The `holders_per_trait.csv` script is what generates our 3 files with the owners per trait. In our case is collection specific in case that you want this functionality you'd have to change the name of the rows to match your own
