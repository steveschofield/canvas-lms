import requests
from datetime import datetime, timedelta

def create_canvas_discussion_topic(
    course_id, 
    access_token, 
    canvas_domain_url,
    title,
    message,
    lock_at,
    published,
    pinned
):
    # Canvas API base URL
    base_url = f"https://{canvas_domain_url}/{course_id}/discussion_topics"
    
    # Headers for the API request
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Prepare module payload
    payload = {

        'title': title,
        'message': message,
        'discussion_type':"threaded",
        'lock_at': lock_at.isoformat(),
        'published':published,
        'pinned':pinned
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

def create_multiple_discussion_topics(
    course_id, 
    access_token, 
    canvas_domain_url,
    dicussion_topics
):

    created_discussion_topics = []

    for i, dicussion_topic in enumerate(dicussion_topics):
        
        dicussion_topic['lock_at'] = datetime.fromisoformat(dicussion_topic['lock_at'])

        result = create_canvas_discussion_topic(
            course_id, 
            access_token, 
            canvas_domain_url,
            dicussion_topic['title'],
            dicussion_topic['message'], 
            dicussion_topic['lock_at'],
            dicussion_topic['published'],
            dicussion_topic['pinned']
        )
        
        if result:
            print("Assignment created successfully!")
            print(f"Assignment ID: {result.get('id')}")
            print(f"Assignment Name: {result.get('name')}")
            created_discussion_topics.append(result)
        else:
            print(f"Failed to create assignment: {dicussion_topic}")
    
    # Print summary of created assignments
    print("\nAssignment Creation Summary:")
    print(f"Total dicussion_topics Attempted: {len(dicussion_topics)}")
    print(f"Total dicussion_topics Created: {len(dicussion_topic)}")
    
    return created_discussion_topics