import requests
from datetime import datetime
import pytz


def create_assignment_group(
    course_id, 
    access_token, 
    canvas_domain_url,
    name,
    position,
    group_weight
 
):

    # Canvas API base URL
    base_url = f"https://{canvas_domain_url}/{course_id}/assignment_groups"
    
    # Headers for the API request
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Prepare module payload
    payload = {
            'name': name,
            'position': position,
            'group_weight' : group_weight
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
        print(f"Error creating assignment_group {name}: {e}")
        return None


def create_multiple_assignment_groups(
    course_id, 
    access_token, 
    canvas_domain_url,
    assignment_groups
):

    created_assignments_groups = []

    for i, assignment_group in enumerate(assignment_groups):

        result = create_assignment_group(
            course_id, 
            access_token, 
            canvas_domain_url,
            assignment_group['name'],
            assignment_group['position'],
            assignment_group['group_weight'],  # Handle case where date might not exist
        )
        
        if result:
            print("Assignment created successfully!")
            print(f"Assignment ID: {result.get('id')}")
            print(f"Assignment Name: {result.get('name')}")
            created_assignments_groups.append(result)
        else:
            print(f"Failed to create assignment_group: {assignment_group}")
    
    # Print summary of created assignments
    print("\nAssignment Creation Summary:")
    print(f"Total Assignments Attempted: {len(assignment_groups)}")
    print(f"Total Assignments Created: {len(assignment_groups)}")
    
    return created_assignments_groups