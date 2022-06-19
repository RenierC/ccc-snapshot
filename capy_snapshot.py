import argparse
from ast import Str
import json
import csv
import os

from typing import Dict, List, Tuple
import requests
import time

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# these come from the .env file
opensea_api_key = os.getenv('OPENSEA_API_KEY')
contract_address = os.getenv('CONTRACT_ADDRESS')


def get_assets(address: str, api_key: str, cursor: str, limit=50) -> Tuple[str, Dict]:
    """_summary_

    Args:
        address (str): Contract address that mints the NFTs
        api_key (str): OpenSea API KEY
        cursor (str): Token that points to next current page.
        limit (int): Max amount of assets that can be returned in one get request.OpenSea caps to 50 assets per request.

    Returns:
        Tuple[str,str,Dict]: returns cursor of next and previous page and result of the api request in a dictionary
    """
    url = f"https://api.opensea.io/api/v1/assets?order_direction=desc&asset_contract_address={address}&limit={limit}&include_orders=true"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }
    if cursor:
        url = f"{url}&cursor={cursor}"

    statusResponse = requests.request("GET", url, headers=headers)
    data = statusResponse.json()
    next_cursor = None
    prev_cursor = None
    if statusResponse.status_code == 200:
        next_cursor = data['next']
        prev_cursor = data['previous']

    return next_cursor, prev_cursor, data['assets']


def get_bulk_assets(address: str, api_key: str, total: int) -> List[Dict]:
    """
    Fuction that iterate through the assets and returns a list of {total} assets

    Args:
        address (str): Contract address that mints the NFTs
        api_key (str): OpenSea API KEY

    Returns:
        List[Dict]: List of {total} assets
    """
    assets = list()
    next_cursor = None
    assets_per_request = 50
    for i in range(0, total, assets_per_request):
        print(i)
        next_cursor, prev_cursor, data = get_assets(
            address, api_key, next_cursor, limit=assets_per_request)
        assets = assets + data
        time.sleep(0.26)

    return assets


def get_slug(address: str, api_key: str) -> str:
    """ Function that request the slug of the collection
    Args:
        address (str): Contract address that mints the NFTs
        api_key (str): OpenSea API KEY

    Returns:
        slug (str): Slug of the collection
    """
    url = f"https://api.opensea.io/api/v1/asset_contract/{address}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }
    statusResponse = requests.request("GET", url, headers=headers)
    slug = None
    if statusResponse.status_code == 200:
        slug = statusResponse.json()['collection']['slug']
    return slug


def get_collection_info(slug: str, api_key: str) -> Dict:
    """Fuction that request the info of the collectio

    Args:
        slug (str): slug of the collection. You can obtain it with {get_slug}
        api_key (str): OpenSea API KEY

    Returns:
        Dict: Dictionarie with the info of the collection
    """
    url = f"https://api.opensea.io/api/v1/collection/{slug}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }
    statusResponse = requests.request("GET", url, headers=headers)
    data = None
    if statusResponse.status_code == 200:
        data = statusResponse.json()
    return data['collection']


def get_params():
    arg_parser = argparse.ArgumentParser(description="Wallet submission bot")
    arg_parser.add_argument("--address", "-a", type=str,
                            default=contract_address, help="Contract address of the NFT")
    arg_parser.add_argument("--output_dir", "-o", type=str,
                            default=".", help="Output directory")
    arg_parser.add_argument(
        "--format", type=str, default="csv", help="Desired format [csv, json, all]")
    return arg_parser.parse_args()


def capy_type(list_of_traits):
    for trait in list_of_traits:
        if trait['trait_type'] == 'Type' and trait['value'] == 'Robot':
            return "Robot"
        if trait['trait_type'] == 'Type' and trait['value'] == 'Slime':
            return "Slime"
        if trait['trait_type'] == 'Type' and trait['value'] == 'Natural':
            return "Natural"


def main(args):
    contract_address = args.address
    output_dir = args.output_dir
    output_format = args.format

    slug = get_slug(contract_address, opensea_api_key)
    info = get_collection_info(slug, opensea_api_key)
    total_supply = int(info['stats']['total_supply'])
    raw_assets = get_bulk_assets(
        contract_address, opensea_api_key, total_supply)

    owners = dict()
    for asset in raw_assets:

        owner = asset["owner"]
        token_id = asset['token_id']
        is_listed = not asset['sell_orders'] is None
        wallet = owner['address']
        list_of_traits = asset['traits']

        try:
            username = owner['user']['username']
        except:
            username = 'N/A'
        username = username if username is not None else 'N/A'

        if owners.get(wallet) is None:
            owners[wallet] = dict()
            owners[wallet]["username"] = username
            owners[wallet]["hold_count"] = 0
            owners[wallet]["hold_ids"] = list()
            owners[wallet]["listed_count"] = 0
            owners[wallet]["listed_ids"] = list()
            owners[wallet]["robot_count"] = 0
            owners[wallet]["slime_count"] = 0
            owners[wallet]["natural_count"] = 0

        if is_listed:
            owners[wallet]["listed_count"] += 1
            owners[wallet]["listed_ids"].append(token_id)

        else:
            owners[wallet]["hold_count"] += 1
            owners[wallet]["hold_ids"].append(token_id)

        # ---- capy types
        if (capy_type(list_of_traits) == "Robot"):
            owners[wallet]["robot_count"] += 1
        if(capy_type(list_of_traits) == "Slime"):
            owners[wallet]["slime_count"] += 1
        if(capy_type(list_of_traits) == "Natural"):
            owners[wallet]["natural_count"] += 1
        # ---- end capy types

    if output_format in ['json', 'all']:
        with open(f'{output_dir}/balances.json', 'w') as fp:
            json.dump(owners, fp)

    if output_format in ['csv', 'all']:
        with open(f'{output_dir}/balance.csv', 'w') as csv_file:
            writer = csv.writer(csv_file)
            header = ['wallet'] + list(list(owners.values())[0].keys())
            writer.writerow(header)
            for owner, data in owners.items():
                writer.writerow([owner] + list(data.values()))

    # This part is specific to most collections so you can adapt it to your needs
    if os.path.isfile(f'{output_dir}/balance.csv'):
        os.system(f'python holders_by_trait.py -o {output_dir}')


if __name__ == '__main__':
    main(get_params())
