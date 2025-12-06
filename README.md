# canvas-lms

Used for Canvas classroom automation

The codebase creates elements for Canvas courses using an online format.  The scripts are controlled by **main.py**. The elements are created in this order

* Modules
* Assignment Groups
* Assignments
* Pages
* Discussion Groups

Before running the scripts, there is prep work required to help organize data in the JSON files.   

1. Create an outline of how the course will be setup.
2. Update each JSON file with the specific data.

Here is a sample used for Cloud Essentials+, which is offered by CompTIA

| **Week**    | **Start Date**                           | **End Date**                   | **Chapter Covered**                                 | **Assignments**                                                                                                                                                                                           |
| ----------------- | ---------------------------------------------- | ------------------------------------ | --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Week 1**  | **2025-01-11 00:00:00.000000**           |                                      |                                                           |                                                                                                                                                                                                                 |
| **Week 2**  |                                                | **2025-01-19 23:59:59.000000** | **Module  1** **Introduction** **-**    | ***Post Introduction** * **Review Introduction to Course** * **Review Videos on grading, approach to study each week** * **Review Simple Syllabus**                                     |
| **Week 3**  | **2025-01-20** **00:00:00.000000** |                                      |                                                           |                                                                                                                                                                                                                 |
| **Week 4**  |                                                | **2025-02-02 23:59:59.000000** | **Module 2** <br />**Lesson 1: **                  | ***Online Work** * **Topics** * **Reviews** * **Flashcards – 48** * **Labs**  * **Lesson 1 –** **PBQ /** **Practice Questions**  * **Discussion Board** |
| **Week 5**  | **2025-02-03** **00:00:00.000000** |                                      |                                                           |                                                                                                                                                                                                                 |
| **Week 6**  |                                                | **2025-02-16 23:59:59.000000** | **Module 3** <br />**Lesson 2: **                  | ***Online Work** * **Topics** * **Reviews** * **Flashcards – 30** * **Labs**  * **Lesson 2 –** **PBQ /** **Practice Questions**  * **Discussion Board** |
| **Week 7**  | **2025-02-17** **00:00:00.000000** |                                      |                                                           |                                                                                                                                                                                                                 |
| **Week 8**  |                                                | **2025-03-02 23:59:59.000000** | **Module 4** <br />**Lesson 3: **                  | ***Online Work** * **Topics** * **Reviews** * **Flashcards – 40** * **Labs**  * **Lesson 3 –** **PBQ /** **Practice Questions**  * **Discussion Board** |
| **Week 9**  | **2025-03-03** **00:00:00.000000** |                                      |                                                           |                                                                                                                                                                                                                 |
| **Week 10** |                                                | **2025-03-16 23:59:59.000000** | **Ch4** **– Module 5** <br />**Lesson 4: ** | ***Online Work** * **Topics** * **Reviews** * **Flashcards – 45** * **Labs**  * **Lesson 4 –** **PBQ /** **Practice Questions**  * **Discussion Board** |
| **Week 11** | **2025-03-17** **00:00:00.000000** |                                      |                                                           | **Spring break 3/24 - 3/30**                                                                                                                                                                              |
| **Week 12** |                                                | **2025-04-06 23:59:59.000000** | **Ch5** **– Module 6** <br />**Lesson 5: ** | ***Online Work** * **Topics** * **Reviews** * **Flashcards – 18** * **Labs**  * **Lesson 5 –** **PBQ /** **Practice Questions**  * **Discussion Board** |
| **Week 13** | **2025-04-07** **00:00:00.000000** |                                      |                                                           |                                                                                                                                                                                                                 |
| **Week 14** |                                                | **2025-04-20 23:59:59.000000** | **Module 7**                                        | **Practice Assessment**                                                                                                                                                                                   |
| **Week 15** | **2025-04-21** **00:00:00.000000** | **2025-05-02 23:59:59.000000** | **Module 8**                                        | **Final Exam (**Schedule between 4/21 and 5/1)Required – email your results.  If you pass, include "PASS" from CompTIA.  If don't pass, please let me know otherwise no grade is earned for Final Exam (15%).  |

***Co-pilot generated documentation.***

# Canvas LMS Automation

This project automates the creation of common elements in Canvas courses offered in an online format. The Python scripts are controlled by [main.py](vscode-file://vscode-appDocuments/Apps/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) and create elements in the following order:

1. Modules
2. Assignment Groups
3. Assignments
4. Pages
5. Discussion Boards

## Prerequisites

Before running the scripts, ensure you have the following:

1. Canvas LMS token provided under your profile and access to Canvas courses
2. I'd recommend having a practice course to attempt, the COURSE_ID attribute is located in the config.ini
3. An outline of how the course will be set up.
4. Updated JSON files with the specific data for your course.

## Project Structure

**canvas-lms/**

**├── __pycache__/**

**├── .DS_Store**

**├── .gitignore**

**├── .python-version**

**├── .vscode/**

**│   └── settings.json**

**├── canvas_assignment_creator.py**

**├── canvas_assignment_groups_creator.py**

**├── canvas_discussion_board.py**

**├── canvas_module_creator.py**

**├── canvas_page_creator.py**

**├── datafiles/**

**│   ├── <CourseID>-assignment-data.json**

**│   ├── <CourseID>-assignment-groups-data.json**

**│   ├── <CourseID>-discussion-topic-data.json**

**│   ├── <CourseID>-module-data.json**

**│   └── <CourseID>-pages-data.json**

**├── delete-modules.py (MAKE SURE TO RUN ONLY WHEN REMOVING ALL ELEMENTS)**

**├── LICENSE**

**├── main.py**

**├── README.md**

**├── requirements.txt**

**├── sample-config.ini**

**└── sample-main.py**

## Configuration

Create a configuration file ([config.ini](vscode-file://vscode-appDocuments/Apps/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)) with the following structure:

**[**canvas_data**]**

**COURSE_ID** = <your_course_id>

**API_TOKEN** = <your_api_token>

**CANVAS_DOMAIN_URL** = <your_canvas_domain_url>

**COLLEGE_CANVAS_DOMAIN** = <your_college_canvas_domain>

## JSON Data Files

Update the JSON files in the [datafiles](vscode-file://vscode-appDocuments/Apps/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) directory with your specific course data. The schema for each file is as follows:

### [<CourseID>-module-data.json](vscode-file://vscode-appDocuments/Apps/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)

**{**

**  **"title"**: **"module_names"**,**

**  **"MODULE_NAMES"**: **[

**    **{

**      **"name"**: **"Module Name"**,**

**      **"unlock_date"**: **"YYYY-MM-DD HH:MM:SS.SSSSSS"**,**

**      **"addHomeworkSubHeader"**: **true**,**

**      **"HomeworkSubHeaderText"**: **"Homework SubHeader Text"**,**

**      **"addQuizSubHeader"**: **true**,**

**      **"QuizSubHeaderText"**: **"Quiz SubHeader Text"

**    **}

**  **]

**}**

### [<CourseID>-assignment-groups-data.json](vscode-file://vscode-appDocuments/Apps/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)

**{**

**  **"title"**: **"assignment_groups"**,**

**  **"ASSIGNMENT_GROUPS"**: **[

**    **{

**      **"name"**: **"Assignment Group Name"**,**

**      **"position"**: **1**,**

**      **"group_weight"**: **20

**    **}

**  **]

**}**

### [<CourseID>-assignment-data.json](vscode-file://vscode-appDocuments/Apps/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)

**{**

**  **"title"**: **"assignments"**,**

**  **"ASSIGNMENTS"**: **[

**    **{

**      **"name"**: **"Assignment Name"**,**

**      **"points_possible"**: **10**,**

**      **"due_at"**: **"YYYY-MM-DDTHH:MM:SS"**,**

**      **"lock_at"**: **"YYYY-MM-DDTHH:MM:SS"**,**

**      **"unlock_at"**: **"YYYY-MM-DDTHH:MM:SS"**,**

**      **"description"**: **"Assignment Description"**,**

**      **"published"**: **true**,**

**      **"assignment_group_name"**: **"Assignment Group Name"

**    **}

**  **]

**}**

### [<CourseID>-pages-data.json](vscode-file://vscode-appDocuments/Apps/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)

**{**

**  **"title"**: **"pages"**,**

**  **"PAGES"**: **[

**    **{

**      **"title"**: **"Page Title"**,**

**      **"body"**: **"Page Body"

**    **}

**  **]

**}**

### [<CourseID>-discussion-topic-data.json](vscode-file://vscode-appDocuments/Apps/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)

**{**

**  **"title"**: **"discussion_topics"**,**

**  **"DISCUSSION_TOPICS"**: **[

**    **{

**      **"title"**: **"Discussion Title"**,**

**      **"message"**: **"Discussion Message"**,**

**      **"lock_at"**: **"YYYY-MM-DDTHH:MM:SS"**,**

**      **"due_at"**: **"YYYY-MM-DDTHH:MM:SS"**,**

**      **"unlock_at"**: **"YYYY-MM-DDTHH:MM:SS"**,**

**      **"published"**: **true**,**

**      **"pinned"**: **true**,**

**      **"points_possible"**: **10

**    **}

**  **]

**}**

## Installation

1. Clone the repository.
2. Install the required packages:

**pip** **install** **-r** **requirements.txt**

## Usage

Run the [main.py](vscode-file://vscode-appDocuments/Apps/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) script to create the course elements:

**python** **main.py**

## License

This project is licensed under the MIT License. See the [LICENSE](vscode-file://vscode-appDocuments/Apps/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Contact

For any questions or issues, please contact Steve Schofield.

---

This documentation provides an overview of the project, configuration, JSON data files, installation, usage, license, and contribution guidelines.

## MANUAL STEPS

Setup the outline mentioned above helps me determine the outline of the course

Enable 35% percentage on Assignments Assignment Group

Add Orientation Pre-req to Module 1

Publish each module items added from automation

Add Assignments within each module

Content in all Pages to fit whatever course is offered

Other general formating within Modules with indents, Video placeholders.
