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
CONFIG_PATH = 'etc/config.txt'
CONFIG_SECTION = 'canvas-lms-test'  # matches the section name in config.txt
config.read(CONFIG_PATH)

if CONFIG_SECTION not in config:
    raise KeyError(
        f"Section [{CONFIG_SECTION}] not found in {CONFIG_PATH}. "
        f"Available sections: {config.sections()}"
    )

# Retrieve settings
COURSE_ID = config[CONFIG_SECTION]['COURSE_ID']
API_TOKEN = config[CONFIG_SECTION]['API_TOKEN']
CANVAS_DOMAIN_URL = config[CONFIG_SECTION]['CANVAS_DOMAIN_URL']

def main():

    def read_from_json(file_path, dataType):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data[dataType]
    
    #MODULE_NAMES = read_from_json("datafiles/<CourseID>-module-data.json","MODULE_NAMES")
    #ASSIGNMENT_GROUPS = read_from_json("datafiles/<CourseID>-assignment-groups-data.json","ASSIGNMENT_GROUPS")
    #ASSIGNMENTS = read_from_json("datafiles/<CourseID>-assignment-data.json","ASSIGNMENTS")
    #PAGES = read_from_json("datafiles/CBSY101-pages-data.json","PAGES")
    DISCUSSION_TOPICS_PATH = "datafiles/CBSY101-discussion-topic-data.json"
    
    # created_modules = create_multiple_modules(
    #     COURSE_ID,
    #     API_TOKEN,
    #     CANVAS_DOMAIN_URL,
    #     COLLEGE_CANVAS_DOMAIN,
    #     MODULE_NAMES
    # )

    # created_assignment_groups = create_multiple_assignment_groups(
    #     COURSE_ID, 
    #     API_TOKEN, 
    #     CANVAS_DOMAIN_URL,
    #     ASSIGNMENT_GROUPS,
    # )

    # created_assignments = create_multiple_assignments(
    #     COURSE_ID, 
    #     API_TOKEN, 
    #     CANVAS_DOMAIN_URL,
    #     ASSIGNMENTS,
    # )

    # created_canvas_page = create_multiple_pages(
    #     COURSE_ID, 
    #     API_TOKEN, 
    #     CANVAS_DOMAIN_URL,
    #     PAGES
    # )

    discussion_board_test = create_discussion_boards(
        COURSE_ID, 
        API_TOKEN, 
        CANVAS_DOMAIN_URL,
        DISCUSSION_TOPICS_PATH
    )
   
if __name__ == "__main__":
    main()
