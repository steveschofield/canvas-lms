from datetime import datetime, timedelta
from canvas_module_creator import create_multiple_modules
from canvas_assignment_creator import create_multiple_assignments
from canvas_discussion_topic_creator import create_multiple_discussion_topics
from canvas_page_creator import create_multiple_pages
import configparser
import json

# Configuration variables
# Create a config parser object
config = configparser.ConfigParser()

# Read the configuration file
config.read('/etc/config.ini')

# Retrieve settings
COURSE_ID = config['canvas_data']['COURSE_ID']
API_TOKEN = config['canvas_data']['API_TOKEN']
CANVAS_DOMAIN_URL = config['canvas_data']['CANVAS_DOMAIN_URL']

def main():

    def read_from_json(file_path, dataType):
        """
        Reads module names from a JSON file.
        :param file_path: Path to the JSON file
        :param dataType: Data being retrieved in JSON file
        :return: List of data
        """
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data[dataType]
    
    #MODULE_NAMES = read_from_json("datafiles/module-data.json","MODULES")
    #ASSIGNMENTS = read_from_json("datafiles/assignment-data.json","ASSIGNMENTS")
    #PAGES = read_from_json("datafiles/pages-data.json","PAGES")
    DICUSSION_TOPICS = read_from_json("datafiles/discussion-topic-data.json","DISCUSSION_TOPICS")

    # Create modules
    # created_modules = create_multiple_modules(
    #     COURSE_ID,
    #     API_TOKEN,
    #     CANVAS_DOMAIN_URL,
    #     MODULE_NAMES
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

    created_discussion_topic = create_multiple_discussion_topics(
        COURSE_ID, 
        API_TOKEN,
        CANVAS_DOMAIN_URL,
        DICUSSION_TOPICS
    )

    
if __name__ == "__main__":
    main()