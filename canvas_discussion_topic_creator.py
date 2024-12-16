import requests
from datetime import datetime, timedelta

def create_canvas_discussion_topic(
    course_id, 
    access_token, 
    canvas_domain_url,
    title,
    message,
    lock_at,
    published
):
    """
    Create a new module in a Canvas course
    
    :param course_id: The ID of the course
    :param module_name: Name of the module to create
    :param access_token: Canvas API access token
    :param unlock_at: Optional date when the module will become available
    :param publish: Whether to publish the module immediately
    :return: Response from the Canvas API

        "title":"topic2",
        "message":"<p>topic2</p>",
        "podcastEnabled":false,
        "discussionType":"threaded",
        "podcastHasStudentPosts":false,
        "published":true,
        "isAnnouncement":false,
        "delayedPostAt":null,"
        lockAt":null,
        "assignment":null,
        "checkpoints":[],
        "groupCategoryId":null,
        "locked":false,"
        requireInitialPost":false,
        "todoDate":null,
        "allowRating":false,
        "onlyGradersCanRate":false,
        "dueAt":null,
        "onlyVisibleToOverrides":false,
        "ungradedDiscussionOverrides":null,
        "contextId":"14022",
        "contextType":
        "Course",
        "isAnonymousAuthor":false,
        "anonymousState":"off"},
    """
    # Canvas API base URL
    base_url = f"https://{canvas_domain_url}/{course_id}/discussion_topics"
    
    # Headers for the API request
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Prepare module payload
    payload = {
        'discussion_topics': {
            'title': title,
            'message': message,
            'discussion_type':"threaded",
            'published':published,
            'lock_at': lock_at.isoformat(),
            "is_announcement":"false"

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

def create_multiple_discussion_topics(
    course_id, 
    access_token, 
    canvas_domain_url,
    dicussion_topics
):
    """
    Create multiple assignments in a Canvas course
    
    :param course_id: The ID of the course
    :param assignments: List of dictionaries containing assignment data
    :param access_token: Canvas API access token
    :param canvas_domain_url: Base URL for Canvas API
    :return: List of successfully created assignments
    """

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
            dicussion_topic['published']
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