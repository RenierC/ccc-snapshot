import csv
import os

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
opensea_api_key = os.getenv('OPENSEA_API_KEY')

# this script is specific to our collection but serves as a template for other collections


def trait_writer(trait_name: str, trait_list: list):
    """Function to write a csv file for each type of capy

    Args:
        The type of capy to write to a csv file
        The list of wallets with the capy type

    Returns:
        A csv file for each type of capy in the root of the project
    """
    with open(trait_name + '.csv', 'w') as csv_file:
        write = csv.writer(csv_file)
        for trait in trait_list:
            write.writerow([trait])


def holders_by_trait(snapshot_name: str):
    """Funtion to generate a csv file for each type of capy

    Args:
        The name of the csv file with the snapshot data

    Returns:
        A csv file for each type of capy in the root of the project
    """
    with open(snapshot_name, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        wallets = []
        robots = []
        slimes = []
        naturals = []
        for row in reader:
            wallets.append(row['wallet'])
            if(row['robot_count'] != '0'):
                robots.append(row['wallet'])
            if(row['slime_count'] != '0'):
                slimes.append(row['wallet'])
            if(row['natural_count'] != '0'):
                naturals.append(row['wallet'])

        trait_writer('robot_holders', robots)
        trait_writer('slime_holders', slimes)
        trait_writer('natural_holders', naturals)

        # print("total wallets: ", wallets.__len__())  # 1179
        # print("total robots: ", robots.__len__())  # 316
        # print("total slimes: ", slimes.__len__())  # 158
        # print("total naturals: ", naturals.__len__())  # 1028


holders_by_trait('balance.csv')
