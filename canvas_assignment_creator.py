import requests
from datetime import datetime
import pytz


def create_canvas_assignment(
    course_id, 
    access_token, 
    canvas_domain_url,
    assignment_name,
    points_possible,
    due_at,
    lock_at,
    unlock_at,
    description,
    published
):

    # Canvas API base URL
    base_url = f"https://{canvas_domain_url}/{course_id}/assignments"
    
    # Headers for the API request
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Prepare module payload
    payload = {
        'assignment': {
            'name': assignment_name,
            'points_possible': points_possible,
            'due_at' : due_at.isoformat(),
            'lock_at': lock_at.isoformat(),
            'unlock_at': unlock_at.isoformat(),
            'description': description,
            'published':published
        }
    }
    
    try:
        # Send POST request to create the module
        response = requests.post(base_url, json=payload, headers=headers)
        
        # Raise an exception for HTTP errors
        response.raise_for_status()

        data = response.json()

        # Return the JSON response
        return data
    
    except requests.exceptions.RequestException as e:
        print(f"Error creating module {assignment_name}: {e}")
        return None


from datetime import datetime

def create_multiple_assignments(
    course_id, 
    access_token, 
    canvas_domain_url,
    assignments
):

    created_assignments = []

    for i, assignment in enumerate(assignments):
        
        assignment['due_at'] = datetime.fromisoformat(assignment['due_at'])
        assignment['lock_at'] = datetime.fromisoformat(assignment['lock_at'])
        assignment['unlock_at'] = datetime.fromisoformat(assignment['unlock_at'])

        result = create_canvas_assignment(
            course_id, 
            access_token, 
            canvas_domain_url,
            assignment['name'],
            assignment['points_possible'],
            assignment['due_at'],  # Handle case where date might not exist
            assignment['lock_at'],
            assignment['unlock_at'], 
            assignment['description'],
            assignment['published']  # Default to False if not specified
        )
        
        if result:
            print("Assignment created successfully!")
            print(f"Assignment ID: {result.get('id')}")
            print(f"Assignment Name: {result.get('name')}")
            created_assignments.append(result)
        else:
            print(f"Failed to create assignment: {assignment}")
    
    # Print summary of created assignments
    print("\nAssignment Creation Summary:")
    print(f"Total Assignments Attempted: {len(assignments)}")
    print(f"Total Assignments Created: {len(created_assignments)}")
    
    return created_assignments