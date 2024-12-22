from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
import configparser

from main import COLLEGE_CANVAS_DOMAIN

# Create a config parser object
config = configparser.ConfigParser()

# Read the configuration file
config.read('/Users/ss/etc/config.ini')

# Retrieve settings
COURSE_ID = config['canvas_data']['COURSE_ID']
API_TOKEN = config['canvas_data']['API_TOKEN']
COLLEGE_CANVAS_DOMAIN = config['canvas_data']['COLLEGE_CANVAS_DOMAIN']

# Initialize Canvas object
canvas = Canvas(COLLEGE_CANVAS_DOMAIN, API_TOKEN)

# Get the course
try:
    course = canvas.get_course(COURSE_ID)
except CanvasException as e:
    print(f"Failed to get course: {e}")
    exit(1)


def delete_assignments_in_group(canvas_url, api_key, course_id):
    """
    Deletes all assignments in the assignment group named 'Assignments'.

    :param canvas_url: URL of your Canvas instance
    :param api_key: Your Canvas API key
    :param course_id: The ID of the course in Canvas
    :return: None
    """
    # Initialize the Canvas object
    canvas = Canvas(canvas_url, api_key)

    # Get the course
    course = canvas.get_course(course_id)

    # Find the 'Assignments' group
    assignments_group = None
    for group in course.get_assignment_groups():
        if group.name == 'Assignments':
            assignments_group = group
            break

    if assignments_group:
        # Get all assignments for the course
        all_assignments = course.get_assignments()
        
        for assignment in all_assignments:
            if assignment.assignment_group_id == assignments_group.id:
                # Delete each assignment that belongs to the 'Assignments' group
                assignment.delete()
        print("All assignments in 'Assignments' group have been deleted.")
    else:
        print("No assignment group named 'Assignments' was found.")


def delete_groups_and_assignments(canvas_url, api_key, course_id):
    
    # Initialize the Canvas object
    canvas = Canvas(canvas_url, api_key)

    # Get the course
    course = canvas.get_course(course_id)

    # Get all assignment groups
    assignment_groups = course.get_assignment_groups()

    # Get all assignment groups
    assignment_groups = course.get_assignment_groups()

    for group in assignment_groups:
        if group.name != 'Assignments':
            # Delete all other assignment groups
            group.delete()
        # else:
        #     # For the "Assignments" group, delete all assignments
        #     assignments = group.get_assignments()
        #     for assignment in assignments:
        #         assignment.delete()

# Function to delete a module


def delete_module(module):
    try:
        module.delete()
        print(f"Module '{module.name}' deleted.")
    except CanvasException as e:
        print(f"Failed to delete module '{module.name}': {e}")

# Function to delete a page
def delete_page(page):
    try:
        page.delete()
        print(f"Page '{page.title}' deleted.")
    except CanvasException as e:
        print(f"Failed to delete page '{page.title}': {e}")
try:
    delete_assignments_in_group(COLLEGE_CANVAS_DOMAIN, API_TOKEN, COURSE_ID)
except CanvasException as e:
    print(f"Error fetching modules: {e}")

#Fetch all modules and attempt to delete them
try:
    for module in course.get_modules():
        delete_module(module)
except CanvasException as e:
    print(f"Error fetching modules: {e}")

# Fetch all pages and attempt to delete them
try:
    for page in course.get_pages():
        delete_page(page)
except CanvasException as e:
    print(f"Error fetching pages: {e}")

try:
    delete_groups_and_assignments(COLLEGE_CANVAS_DOMAIN, API_TOKEN, COURSE_ID)
except CanvasException as e:
    print(f"Error deleting assignment groups and assignments: {e}")



print("Module deletion process completed.")
