from ast import mod
import requests
from datetime import datetime, timedelta
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException

def update_module_publish_status(
    module_name,
    module_id,
    canvas_domain_url,
    course_id,
    access_token,
    unlock_date
):
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

def add_text_headers(
    course_id,
    access_token,
    canvas_domain_url,
    module_id,
    header_text,
    position
):
    try:
        # Initialize Canvas object
        canvas = Canvas(canvas_domain_url, access_token)
        
        # Get the course
        course = canvas.get_course(course_id)
        
        # Get the module using the module_id
        module = course.get_module(module_id)
        
        # Add the text header to the module
        module.create_module_item({
            'type': 'SubHeader',
            'title': header_text,
            'position': position  # The position of the subheader in the module
        })
        print(f"Text header '{header_text}' added to module {module_id} successfully.")
    
    except CanvasException as e:
        print(f"Failed to add text header: {e}")
        return None  # Optionally return None or something else to signify failure


    
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
        return module_id
    
    except requests.exceptions.RequestException as e:
        print(f"Error creating module {module_name}: {e}")
        return None

def create_multiple_modules(
    course_id, 
    access_token, 
    canvas_domain_url,
    MCC_CANVAS_DOMAIN,
    module_names
):
    created_modules = []

    for i, module_name in enumerate(module_names):
        # Determine unlock date (use None if not provided)
        module_name['unlock_date'] = datetime.fromisoformat(module_name['unlock_date'])

        module_id_result = create_canvas_module(
            course_id, 
            access_token, 
            canvas_domain_url,
            module_name['name'],
            module_name['unlock_date'],
        )

        #add module item if true
        if(module_name['addHomeworkSubHeader'] == True):
            add_text_headers(
                course_id,
                access_token, 
                MCC_CANVAS_DOMAIN,
                module_id_result,
                module_name['HomeworkSubHeaderText'],
                1
            )
        
        #add module item if true
        if(module_name['addQuizSubHeader'] == True):
            add_text_headers(
                course_id,
                access_token, 
                MCC_CANVAS_DOMAIN,
                module_id_result,
                module_name['QuizSubHeaderText'],
                2
            )
        
        if module_id_result:
            print("Module created successfully!")
            print(f"Module ID:" + str(module_id_result))
            created_modules.append(module_id_result)
        else:
            print(f"Failed to create module: {module_name}")
    
    # Print summary of created modules
    print("\nModule Creation Summary:")
    print(f"Total Modules Attempted: {len(module_names)}")
    print(f"Total Modules Created: {len(created_modules)}")
    
    return created_modules