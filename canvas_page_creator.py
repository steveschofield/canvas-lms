import requests
from datetime import datetime, timedelta
from canvas_api_utils import build_course_api_url

def create_canvas_page(
    course_id, 
    access_token, 
    canvas_domain_url,
    title,
    body
):
    base_url = build_course_api_url(canvas_domain_url, course_id, "pages")
    
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
            'published': True
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

def create_multiple_pages(
    course_id, 
    access_token, 
    canvas_domain_url,
    page_names
):

    created_pages= []

    for i, page_name in enumerate(page_names):

        result = create_canvas_page(
            course_id, 
            access_token, 
            canvas_domain_url,
            page_name['title'],
            page_name['body']
        )
        
        if result:
            print("Page created successfully!")
            print(f"Page ID: {result.get('id')}")
            print(f"Page Name: {result.get('name')}")
            created_pages.append(result)
        else:
            print(f"Failed to create module: {page_name}")
    
    # Print summary of created modules
    #print("\Page Creation Summary:")
    #print(f"Total Page Attempted: {len(page_names)}")
    #cleprint(f"Total Page Created: {len(created_pages)}")
    
    return created_pages
