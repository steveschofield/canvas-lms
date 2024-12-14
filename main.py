from datetime import datetime, timedelta
from canvas_module_creator import create_multiple_modules
from canvas_assignment_creator import create_multiple_assignments
from canvas_discussion_topic_creator import create_canvas_discussion_topic
from canvas_page_creator import create_canvas_page
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
    #Prepare module payload
    # specific_date = datetime.now()
    # future_date = specific_date + timedelta(days=30)
    # print(future_date)
    # Serialize the datetime to ISO 8601 format
    #unlock_at_iso = future_date.isoformat()
    # List of module names to create

    def read_from_json(file_path, dataType):
        """
        Reads module names from a JSON file.

        :param file_path: Path to the JSON file
        :return: List of module names
        """
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data[dataType]
    
    #MODULE_NAMES = read_from_json("datafiles/module-data.json","MODULES")
    ASSIGNMENTS = read_from_json("datafiles/assignment-data.json","ASSIGNMENTS")

    # Create modules
    # created_modules = create_multiple_modules(
    #     COURSE_ID,
    #     API_TOKEN,
    #     CANVAS_DOMAIN_URL,
    #     MODULE_NAMES
    # )

    created_assignments = create_multiple_assignments(
        COURSE_ID, 
        API_TOKEN, 
        CANVAS_DOMAIN_URL,
        ASSIGNMENTS,
    )

    # created_discussion_topic = create_canvas_discussion_topic(
    #     COURSE_ID, 
    #     API_TOKEN, 
    #     title="Module 1 discussion board",
    #     message="there will be some text here",
    #     published=True,
    #     lock_at=unlock_at_iso
    # )

    created_canvas_page = create_canvas_page(
        COURSE_ID, 
        API_TOKEN, 
        CANVAS_DOMAIN_URL,
        title="Start here > in Module 1, you will cover",
        body="""<h1>Welcome to the Module 1.  This covers Supporting Network Management.</h1>
        <h2>Welcome to the Module 1</h2>"""
    )

if __name__ == "__main__":
    main()