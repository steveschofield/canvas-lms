import configparser
import json

#from custom classes
from datetime import datetime, timedelta
from canvas_module_creator import create_multiple_modules
from canvas_assignment_creator import create_multiple_assignments
from canvas_assignment_groups_creator import create_multiple_assignment_groups
from canvas_page_creator import create_multiple_pages
from canvas_discussion_board import create_discussion_boards

# Create a config parser object
config = configparser.ConfigParser()

# Read the configuration file
config.read('/Users/ss/etc/config.ini')

# Retrieve settings
COURSE_ID = config['canvas_data']['COURSE_ID']
API_TOKEN = config['canvas_data']['API_TOKEN']
CANVAS_DOMAIN_URL = config['canvas_data']['CANVAS_DOMAIN_URL']
MCC_CANVAS_DOMAIN = config['canvas_data']['MCC_CANVAS_DOMAIN']

def main():

    def read_from_json(file_path, dataType):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data[dataType]
    
    MODULE_NAMES = read_from_json("datafiles/CSTC240-module-data.json","MODULE_NAMES")
    ASSIGNMENT_GROUPS = read_from_json("datafiles/CSTC240-assignment-groups-data.json","ASSIGNMENT_GROUPS")
    ASSIGNMENTS = read_from_json("datafiles/CSTC240-assignment-data.json","ASSIGNMENTS")
    PAGES = read_from_json("datafiles/CSTC240-pages-data.json","PAGES")
    DICUSSION_TOPICS = "datafiles/CSTC240-discussion-topic-data.json"
    
    created_modules = create_multiple_modules(
        COURSE_ID,
        API_TOKEN,
        CANVAS_DOMAIN_URL,
        MCC_CANVAS_DOMAIN,
        MODULE_NAMES
    )

    created_assignment_groups = create_multiple_assignment_groups(
        COURSE_ID, 
        API_TOKEN, 
        CANVAS_DOMAIN_URL,
        ASSIGNMENT_GROUPS,
    )

    created_assignments = create_multiple_assignments(
        COURSE_ID, 
        API_TOKEN, 
        CANVAS_DOMAIN_URL,
        ASSIGNMENTS,
    )

    created_canvas_page = create_multiple_pages(
        COURSE_ID, 
        API_TOKEN, 
        CANVAS_DOMAIN_URL,
        PAGES
    )

    discussion_board_test = create_discussion_boards(
        COURSE_ID, 
        API_TOKEN, 
        MCC_CANVAS_DOMAIN,
        DICUSSION_TOPICS
    )
   
if __name__ == "__main__":
    main()