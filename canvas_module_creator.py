import requests
from datetime import datetime, timedelta

def update_module_publish_status(
    module_name,
    module_id,
    canvas_domain_url,
    course_id,
    access_token,
    unlock_date
):
    '''enter code here'''
      # Canvas API base URL
    try:
        base_url = f"https://{canvas_domain_url}/{course_id}/modules/" + str(module_id)

    except requests.exceptions.RequestException as e:
        print(f"Error updating module: {e}")
        return None
    
    # Headers for the API request
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    payload = {
        'module': {
            'name': module_name,
            'unlock_at': unlock_date.isoformat(),
            'published': True
        }
    }
    
    try:
        # Send POST request to create the module
        response = requests.put(base_url, json=payload, headers=headers)
        
        # Raise an exception for HTTP errors
        response.raise_for_status()
        
        # Return the JSON response
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error updating module: {e}")
        return None

def create_canvas_module(
    course_id, 
    access_token, 
    canvas_domain_url, 
    module_name, 
    unlock_date

):

    # Canvas API base URL
    base_url = f"https://{canvas_domain_url}/{course_id}/modules"
    
    # Headers for the API request
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Prepare module payload
    payload = {
        'module': {
            'name': module_name
        }
    }
    
    try:
        # Send POST request to create the module
        response = requests.post(base_url, json=payload, headers=headers)
        
        # Raise an exception for HTTP errors
        response.raise_for_status()

        data = response.json()
        
        module_id = data["id"]
        
        updateresults = update_module_publish_status(module_name,module_id,canvas_domain_url,course_id,access_token,unlock_date)

        # Return the JSON response
        return data
    
    except requests.exceptions.RequestException as e:
        print(f"Error creating module {module_name}: {e}")
        return None

def create_multiple_modules(
    course_id, 
    access_token, 
    canvas_domain_url,
    module_names
):
    created_modules = []

    for i, module_name in enumerate(module_names):
        # Determine unlock date (use None if not provided)
        module_name['unlock_date'] = datetime.fromisoformat(module_name['unlock_date'])

        result = create_canvas_module(
            course_id, 
            access_token, 
            canvas_domain_url,
            module_name['name'],
            module_name['unlock_date']
        )
        
        if result:
            print("Module created successfully!")
            print(f"Module ID: {result.get('id')}")
            print(f"Module Name: {result.get('name')}")
            created_modules.append(result)
        else:
            print(f"Failed to create module: {module_name}")
    
    # Print summary of created modules
    print("\nModule Creation Summary:")
    print(f"Total Modules Attempted: {len(module_names)}")
    print(f"Total Modules Created: {len(created_modules)}")
    
    return created_modules