import json
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
from datetime import datetime

def get_or_create_assignment_group(course, group_name):
    """
    Get an existing assignment group by name or create one if it doesn't exist.
    
    :param course: Canvas course object
    :param group_name: Name of the assignment group
    :return: Assignment group object
    """
    for group in course.get_assignment_groups():
        if group.name.lower() == group_name.lower():
            return group
    # If no group found, create one
    new_group = course.create_assignment_group(name=group_name)
    return new_group

def create_discussion_assignment(course, discussion):
    """
    Create a discussion topic as an assignment and assign it to the "Discussion Boards" group.
    
    :param course: Canvas course object
    :param discussion: Dictionary containing discussion details
    """
    try:
        # Get or create the "Discussion Boards" assignment group
        discussion_group = get_or_create_assignment_group(course, "Discussion Boards")

        # Create the discussion topic (which will be our assignment)
        discussion_topic = course.create_discussion_topic(
            title=discussion["title"],
            message=discussion["message"],
            published=discussion["published"],
            is_announcement=False,
            pinned=discussion["pinned"],
            unlock_at=discussion["unlock_at"],
            due_at=discussion["due_at"],
            points_possible=discussion["points_possible"],
            assignment={
                "name": discussion["title"],
                "points_possible": discussion["points_possible"],  # Adjust points if needed
                "grading_type": "points",
                "submission_types": ["discussion_topic"],
                "published": discussion["published"],
                "pinned": discussion["pinned"],
                "assignment_group_id": discussion_group.id,
                "lock_at": discussion["lock_at"],  # Using the lock_at from JSON
                "due_at": discussion["due_at"],
                "unlock_at":discussion["unlock_at"]
            }
        )
        print(f"Discussion topic '{discussion['title']}' created with ID: {discussion_topic.id}")
    except CanvasException as e:
        print(f"Failed to create discussion assignment '{discussion['title']}': {e}")

def create_discussion_boards(
    course_id,
    access_token,
    canvas_domain_url,
    json_file_path
):
    
    canvas = Canvas(canvas_domain_url, access_token)
    try:
        course = canvas.get_course(course_id)
    except CanvasException as e:
        print(f"Failed to get course: {e}")
        exit(1)

    # Read the JSON file
    if isinstance(json_file_path, (list, tuple)):
        # Allow callers to pass (path, key) style tuples; we just need the path.
        json_file_path = json_file_path[0]

    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Loop through the discussions and create them
    for discussion in data["DISCUSSION_TOPICS"]:
        create_discussion_assignment(course, discussion)
