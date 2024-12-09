import requests
from datetime import datetime, timedelta

def create_canvas_page(
    course_id, 
    access_token, 
    canvas_domain_url,
    title,
    body
):
    """
    Create a new module in a Canvas course
    
    :param course_id: The ID of the course
    :param module_name: Name of the module to create
    :param access_token: Canvas API access token
    :param unlock_at: Optional date when the module will become available
    :param publish: Whether to publish the module immediately
    :return: Response from the Canvas API
    """
    # Canvas API base URL
    base_url = f"https://{canvas_domain_url}/{course_id}/pages"
    
    # Headers for the API request
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Prepare module payload
    payload = {
        'wiki_page': {
            'title': title,
            'body': body,
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
        print(f"Error creating module {title}: {e}")
        return None
