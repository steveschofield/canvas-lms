import requests
from datetime import datetime

def get_assignment_groups(
    course_id, 
    access_token, 
    canvas_domain_url,
    group_name
):
    # Canvas API base URL for assignment groups
    base_url = f"https://{canvas_domain_url}/{course_id}/assignment_groups"
    
    # Headers for the API request
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Send GET request to retrieve assignment groups
        response = requests.get(base_url, headers=headers)
        
        # Raise an exception for HTTP errors
        response.raise_for_status()

        data = response.json()

        # Loop through assignment groups to find the matching group_name
        for group in data:
            if group['name'] == group_name:
                return group['id']  # Return the ID of the matching assignment group
        
        # If no matching group found, return None
        print(f"Assignment group '{group_name}' not found.")
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving assignment groups: {e}")
        return None

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
    published,
    assignment_group_id  # Now we pass the group ID instead of name
):

    # Canvas API base URL for creating assignments
    base_url = f"https://{canvas_domain_url}/{course_id}/assignments"
    
    # Headers for the API request
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Prepare payload with the assignment details
    payload = {
        'assignment': {
            'name': assignment_name,
            'points_possible': points_possible,
            'due_at': due_at.isoformat(),
            'lock_at': lock_at.isoformat(),
            'unlock_at': unlock_at.isoformat(),
            'description': description,
            'published': published,
            'assignment_group_id': assignment_group_id  # Use group ID here
        }
    }
    
    try:
        # Send POST request to create the assignment
        response = requests.post(base_url, json=payload, headers=headers)
        
        # Raise an exception for HTTP errors
        response.raise_for_status()

        data = response.json()

        # Return the JSON response
        return data
    
    except requests.exceptions.RequestException as e:
        print(f"Error creating assignment {assignment_name}: {e}")
        return None

def create_multiple_assignments(
    course_id, 
    access_token, 
    canvas_domain_url,
    assignments
):

    created_assignments = []

    for assignment in assignments:
        assignment_group_name = assignment.get('assignment_group_name')

        # Lookup the assignment group ID
        assignment_group_id = get_assignment_groups(
            course_id, 
            access_token, 
            canvas_domain_url,
            assignment_group_name
        )

        if not assignment_group_id:
            print(f"Skipping assignment '{assignment['name']}' due to missing group.")
            continue  # Skip this assignment if no matching group ID was found

        # Convert date strings to datetime objects
        assignment['due_at'] = datetime.fromisoformat(assignment['due_at'])
        assignment['lock_at'] = datetime.fromisoformat(assignment['lock_at'])
        assignment['unlock_at'] = datetime.fromisoformat(assignment['unlock_at'])

        # Create the assignment with the assignment group ID
        result = create_canvas_assignment(
            course_id, 
            access_token, 
            canvas_domain_url,
            assignment['name'],
            assignment['points_possible'],
            assignment['due_at'],
            assignment['lock_at'],
            assignment['unlock_at'], 
            assignment['description'],
            assignment['published'],
            assignment_group_id  # Pass the found group ID here
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
