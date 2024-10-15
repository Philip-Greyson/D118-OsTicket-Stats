# D118-OsTicket-Stats

## About

This is a script I put together to better visualize the ticket data we have in our self-hosted OsTicket solution.  

This script connects to the mariadb database, does queries on tickets between certain time periods, then takes that data and organizes it a number of ways. The data is then used with matplotlib to generate graphs for easy viewing and readability. It saves each graph to a local file, then combines all the individual pictures into a .pdf and emails it to an email destination.  

Most of it will "just work" for any installation assuming the requirements are met, but there are a few sections/graphs that I did not program generically enough to work with any OsTicket configuration, and will need to be edited for your specific situation. When I have more freetime I will likely revisit it and improve it, but it is working enough for our situation and I have other tasks to do at work.  

If you have questions, suggestions, or would like my assistance as a consultant to help set this up for your situation, please open an issue on this repository.

## Currently included

- Combined view of total # of tickets, and average close time, both per month
 ![Screenshot](https://github.com/Philip-Greyson/D118-OsTicket-Stats/blob/main/Examples/Combined%20Ticket%20Count%20and%20Avg%20Close%20Time.jpg?raw=true) 
- View total tickets per user in the last x days, broken down by status
 ![Screenshot](https://github.com/Philip-Greyson/D118-OsTicket-Stats/blob/main/Examples/Tickets%20Per%20Agent%20For%20Last%2014%20days.jpg?raw=true)
- Overall number of tickets opened and closed in the last x days or x months (months as both a line and bar graph)
 ![Screenshot](https://github.com/Philip-Greyson/D118-OsTicket-Stats/blob/main/Examples/Overall%20Tickets%20For%20Last%2018%20months%20Bar.jpg?raw=true)
- Bar graph of average hours it takes to close a ticket for each individual user in the last x days, as well as overall average
 ![Screenshot](https://github.com/Philip-Greyson/D118-OsTicket-Stats/blob/main/Examples/AvgCloseTimeByAgent-14.jpg?raw=true)
- Individual line graphs of each agent's average close time in hours, plotted in each month for last x months, along with comparison to overall average. [Example](https://github.com/Philip-Greyson/D118-OsTicket-Stats/blob/main/Examples/1-PhilipCloseTimePerMonth.jpg?raw=true)
- Similar to above, individual line graphs of each agent's average first response time in hours, for last x months. [Example](https://github.com/Philip-Greyson/D118-OsTicket-Stats/blob/main/Examples/1-PhilipResponseTimePerMonth.jpg?raw=true)
- Ticket breakdown by category within a topic for last x days. **This one is very specific to our district and will not work for others without editing the script**. [Example](https://github.com/Philip-Greyson/D118-OsTicket-Stats/blob/main/Examples/Student%20Tickets%20By%20Category%20For%20Last%2060%20days.jpg?raw=true)
- Pie chart breakdown of topic distribution in last x days [Example](https://github.com/Philip-Greyson/D118-OsTicket-Stats/blob/main/Examples/Tickets%20by%20Topic%20Breakdown%20For%20Last%2090%20days%20Pie.jpg?raw=true)

## Requirements/Usage

- You have access to an OsTicket installation (duh). Specifically, you need to be able to connect to the MariaDB database on port 3306 that holds all the information, and know the ip address of the host, the database name, username, and password.
  - The ip address will need to be stored as the environment variable 'OSTICKET_HOST'
  - The database name, username and password will need to be stored as 'OSTICKET_DB', 'OSTICKET_USERNAME', and 'OSTICKET_PASSWORD' respectively
- Have an overall directory/folder with the script inside it. Also needed inside that outer directory:
  - Directory/Folder named 'Graphs' for the output files to be placed in.
  - a credentials.json file that holds the Google client ID and secret for a Google API project. This is needed to send the email at the end
- Python (create and tested on Python 3.10.6 and known working on 3.11.1) installed on the machine that is running the script - [Download](https://www.python.org/downloads/release/python-3106/)
- A Gmail account that you wish to send emails from.
- The sender and recipient emails need to be stored as the environment variables 'EMAIL_SENDER' and 'EMAIL_RECEIVER' respectively
- **A number of Python libraries/packages:**
  - The Google API Python Client - Interfaces with Google to send email through Gmail account: [Info Link](https://googleapis.github.io/google-api-python-client/docs/start.html) - [Install Instructions](https://github.com/googleapis/google-api-python-client#installation)
    - This is what needs the credentials.json file is needed for, see the "Setup" section in the info link above to learn how to create a Google API Console project and generate the credentials file.
  - MariaDB Connector/Python - actually does the database connection and queries: [Info Link](https://mariadb.com/resources/blog/how-to-connect-python-programs-to-mariadb/) - `pip3 install mariadb`
    - Also need to install the MariaDB database development files on the computer for the connector to work
      - Ubuntu can use `apt install libmariadb-dev`
      - Windows should just work after library installation (at least it has for me)
  - NumPy - has a few useful math functions: [Info Link](https://numpy.org/install/) - `pip install numpy`
  - Matplotlib - Creates the graphs/plots: [Info Link](https://matplotlib.org/) - `pip install matplotlib`
  - Img2pdf - Creates the output .pdf from individual pictures: [Info Link](https://pypi.org/project/img2pdf/) - `pip3 install img2pdf`
  - ~~Yagmail - Sends the pdf in an email: [Info Link](https://pypi.org/project/yagmail/) - `pip3 install yagmail[all]`~~
