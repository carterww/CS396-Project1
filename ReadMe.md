This is a Web Application that implements a forum that fulfills the requirements:
1.     Create an administrator who can delete other users, delete/edit all posts, create new discussion topics
2.     Provide login function, and sign-up function for new users.
3.     Any user can create a new post, and reply to other users’ posts.
4.     Any user can upload files (could be multiple files).  
5.     Show the numbers of posts and visits, and keep these numbers updated. 
6.     You can store some files on your website
7.     Include a link to google calendar in a drop list.
8.     Show a warning a message/sign to remind users that there is an update or something interesting posted in the forum (words/content/…etc).
9.     Your Website interface should be friendly.

In order to setup this repository, there are a couple of dependencies that need to install.
-       Install Python v 3.10.6 
            - Other versions will likely work but this is the version it was developed in
-      Install the Django package v 4.1
            - Other versions will likely work but this is the version it was developed in
            - This can be done through the pip package manager
-       (Optional) Set up a virtual Python envionment for running this application

Steps to setup this repository:
    1) Download the codebase from https://github.com/carterww/CS396-Project1
    2) Ensure the dependencies listed in the previous section are downloaded
    3) Open the directory ./CS396-Project1-master/ in a terminal where the file manage.py can be seen
    4) Run the following command :
        Windows: "python manage.py runserver"
        Mac: "python3 manage.py runserver"
    5) This will run the application on the 8000 port by default and the website is running