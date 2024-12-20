import requests
import configparser
from canvas_assignment_creator_test import create_multiple_assignments 
import json

# Create a config parser object
config = configparser.ConfigParser()

# Read the configuration file
config.read('/Users/ss/etc/config.ini')

# Retrieve settings
COURSE_ID = config['canvas_data']['COURSE_ID']
API_TOKEN = config['canvas_data']['API_TOKEN']
CANVAS_DOMAIN_URL = config['canvas_data']['CANVAS_DOMAIN_URL']

def main():

    def read_from_json(file_path, dataType):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data[dataType]
    
    ASSIGNMENTS = read_from_json("datafiles/CSTC240-assignment-data-test.json","ASSIGNMENTS")

    created_assignments = create_multiple_assignments(
        COURSE_ID, 
        API_TOKEN, 
        CANVAS_DOMAIN_URL,
        ASSIGNMENTS,
    )

    
if __name__ == "__main__":
    main()