# https://mariadb.com/resources/blog/how-to-connect-python-programs-to-mariadb/
# https://www.geeksforgeeks.org/bar-plot-in-matplotlib/
# https://datatofish.com/bar-chart-python-matplotlib/
# https://pypi.org/project/img2pdf/


# Get the last 2 weeks of tickets, plot how many open and closed per day
# Get the last week of tickets, plot how mnay open/closed per agent
# Get the last 12 months of tickets, plot how many open/closed per month
# Get the last fiscal year (july 1), plot how many open/closed per week?
# Get the breakdown of student/parent/staff tickets in last month?

# Module Imports
import numpy as np
import matplotlib.pyplot as plt
import mariadb # needed to connect to OsTicket database
import datetime  # used to get current date for historical data
from datetime import *
import os  # needed to get environement variables
import sys

#set up database login info, stored as environment variables on system
un= os.environ.get('OSTICKET_USERNAME')
pw = os.environ.get('OSTICKET_PASSWORD')
host = os.environ.get('OSTICKET_HOST')
db = os.environ.get('OSTICKET_DB')

print("Username: " + str(un) + " |Password: " + str(pw) + " |Server: " + str(host) + " |Database: " + str(db)) #debug so we can see where mariadb is trying to connect to/with

names = [] # list of staff names
openedByName = [] # list for count of opened tickets by agent
openByName = []
closedByName = []
waitingByName = []

days = 365

# Connect to MariaDB Platform
with mariadb.connect(user=un, password=pw, host=host, port=3306, database=db) as con:
    with con.cursor() as cur:  # start an entry cursor

        today = datetime.now()  # get todays date and store it for finding the correct term later

        cur.execute('SELECT ost_ticket.ticket_id, ost_staff.firstname, ost_staff.lastname, ost_ticket_status.name, ost_help_topic.topic, ost_ticket__cdata.subject, ost_ticket.isoverdue, ost_ticket.created, ost_ticket.lastupdate, ost_ticket.closed FROM ost_ticket INNER JOIN ost_staff ON ost_ticket.staff_id = ost_staff.staff_id INNER JOIN ost_ticket_status ON ost_ticket.status_id = ost_ticket_status.id INNER JOIN ost_help_topic ON ost_ticket.topic_id = ost_help_topic.topic_id INNER JOIN ost_ticket__cdata ON ost_ticket.ticket_id = ost_ticket__cdata.ticket_id ORDER BY lastname, ticket_id')
        for entry in cur: # go through each result from the query above
                ticketNum = int(entry[0])
                agentFirst = str(entry[1])
                agentLast = str(entry[2])
                status = str(entry[3])
                topic = str(entry[4])
                subject = str(entry[5])
                overdue = bool(entry[6])
                opened = entry[7]
                lastUpdate = entry[8]
                closed = entry[9]
                if opened > (today - timedelta(days=days)):
                        if not agentFirst in names: # if we havent already had a entry for them, we need to create an entry in each list
                                names.append(agentFirst)
                                openedByName.append(0)
                                openByName.append(0)
                                closedByName.append(0)
                                waitingByName.append(0)
                        index = names.index(agentFirst)
                        openedByName[index] += 1# increment the current value in the count list by 1 for that user
                        if status == 'Closed':
                                closedByName[index] += 1
                        elif status == 'Open':
                                openByName[index] += 1
                        elif status == 'Waiting on User':
                                waitingByName[index] += 1
                        print(entry)
        print(names)
        print(openedByName)
        print(openByName)
        print(closedByName)
        print(waitingByName)

# plt.bar(names, openedByName)
# plt.title('Tickets Opened in the Last 2 Weeks by Agent')
# plt.show()


# set width of bar
barWidth = 0.2125
fig = plt.subplots(figsize=(20, 10))

# Set position of bar on X axis
br1 = np.arange(len(names))
br2 = [x + barWidth for x in br1]
br3 = [x + barWidth for x in br2]
br4 = [x + barWidth for x in br3]

# Make the plot
plt.title('Tickets Opened in the last ' + str(days) + ' days by Agent')
total_bar = plt.bar(br1, openedByName, color='y', width=barWidth, edgecolor='grey', label='Total')
open_bar = plt.bar(br2, openByName, color='r', width=barWidth, edgecolor='grey', label='Open')
closed_bar = plt.bar(br3, closedByName, color='g', width=barWidth, edgecolor='grey', label='Closed')
waiting_bar = plt.bar(br4, waitingByName, color='b', width=barWidth, edgecolor='grey', label='Waiting')
plt.bar_label(total_bar, label_type='center')
plt.bar_label(open_bar)

# Adding Xticks
plt.xlabel('User', fontweight='bold', fontsize=15)
plt.ylabel('Tickets', fontweight='bold', fontsize=15)
plt.xticks([r + barWidth for r in range(len(names))],names)

plt.legend()
plt.show()
