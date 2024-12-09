from datetime import datetime, timedelta
from canvas_module_creator import create_multiple_modules
from canvas_assignment_creator import create_canvas_assignment
from canvas_discussion_topic_creator import create_canvas_discussion_topic
from canvas_page_creator import create_canvas_page
import configparser

# Configuration variables
# Create a config parser object
config = configparser.ConfigParser()

# Read the configuration file
config.read('config.ini')

# Retrieve settings
COURSE_ID = config['canvas_data']['COURSE_ID']
API_TOKEN = config['canvas_data'],['API_TOKEN']
CANVAS_DOMAIN_URL = config['canvas_data']['CANVAS_DOMAIN_URL']


def main():
    #Prepare module payload
    specific_date = datetime.now()
    future_date = specific_date + timedelta(days=30)
    
    # Serialize the datetime to ISO 8601 format
    unlock_at_iso = future_date.isoformat()
    # List of module names to create
    # MODULE_NAMES = [
    #     "Module 1",
    #     "Module 2"
    # ]

    # # Create modules
    # created_modules = create_multiple_modules(
    #     COURSE_ID, 
    #     MODULE_NAMES, 
    #     API_TOKEN,
    #     unlock_at_iso
    # )

    # created_assignments = create_canvas_assignment(
    #     COURSE_ID, 
    #     API_TOKEN, 
    #     assignment_name="Sample Assignment 1",
    #     points_possible="5",
    #     due_date=unlock_at_iso,
    #     lock_at=unlock_at_iso,
    #     unlock_at=unlock_at_iso,
    #     description="Example Description",
    #     published=True
    # )

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