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

It also provides the ability to run these queries:
Query 1. For a user, list all transaction details (asset name, price, unit, total amount, agent, etc) on a specific date (e.g. 02/15/2022).
Query 2. For a stock ticker, list its open/close/high/volume on a specific date. 
Query 3. For a property, list its address/price(s)/agent names. 
Query 4. For a bond, list its bond issuer name/yield/maturity date/rating
Query 5, List all assets that an agent manages.
Query 6. Rank loan/mortgage rates offered by banks.
Query 7. For a user, list the gain/loss over a period of time. 

It also meets these requirements
1. The user can post a memo/plan about income, cost, budget, and family members can comment on the post by the reply function. The receipts and documents can be uploaded to the website. (This requirement  should have been met in phase 1)
2. Record the user’s expenditures on food, health, entertainment, etc, into the system, and the user can search the record for a specific time.
3. Use a pie chart to display the user’s expenditures with the corresponding percentages. 
4. Periodically update financial data in the system. For example, stock market data are supposed to be updated on a daily base. 
5. Use bar charts to show the user expenditures, incomes, and other financial data on a month/year base. 
6. Show a red flag (some signals) when the user’s expenditure exceeds his/her income. 
7. Plot the simple moving average (SMA) curve for the expenditure and close stock price for a given period. 
8. Use a linear model (e.g., linear regression model) to predict the future (tomorrow/next month/year) expenditure and close stock price.   


In order to setup this repository, there are a couple of dependencies that need to install.
-       Install Python v 3.10.6 
            - Other versions will likely work but this is the version it was developed in
-       Install the Django package v 4.1
            - Other versions will likely work but this is the version it was developed in
            - This can be done through the pip package manager
-       Install these packages (preferably through pip):
            - Pillow
            - Pandas
            - Yfinance
            - Scikit Learn
            - Matplotlib
-       (Optional) Set up a virtual Python envionment for running this application

Steps to setup this repository:
    1) Download the codebase from https://github.com/carterww/CS396-Project1
    2) Ensure the dependencies listed in the previous section are downloaded
    3) Open the directory ./CS396-Project1-master/ in a terminal where the file manage.py can be seen
    4) Run the following command :
        Windows: "python manage.py runserver"
        Mac: "python3 manage.py runserver"
    5) This will run the application on the 8000 port by default and the website is running