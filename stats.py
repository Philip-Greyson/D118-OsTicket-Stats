# https://mariadb.com/resources/blog/how-to-connect-python-programs-to-mariadb/
# https://www.geeksforgeeks.org/bar-plot-in-matplotlib/
# https://datatofish.com/bar-chart-python-matplotlib/
# https://pypi.org/project/img2pdf/


# ----- Done -----
# Get the last x days of tickets, plot how many open/closed/waiting per agent
# Get the last x days of tickets, plot how many per help category

# ---- TO-DO -----
# Get the last 2 weeks of tickets, plot how many open and closed per day
# Get the last 12 months of tickets, plot how many open/closed per month
# Get the last fiscal year (july 1), plot how many open/closed per week?
# Get the breakdown of student/parent/staff tickets in last month?
# Average close time by user, overall, 
# For single agent, look at average ticket closing time per month/week/etc

# Save all plots to files
# Take all plot files and put them together with img2pdf


# Module Imports
import numpy as np
import matplotlib.pyplot as plt
import mariadb # needed to connect to OsTicket database
import datetime  # used to get current date for historical data
from datetime import *
from itertools import cycle # needed to cycle through a list one at a time, looping
import os  # needed to get environement variables
import sys

#set up database login info, stored as environment variables on system
un= os.environ.get('OSTICKET_USERNAME')
pw = os.environ.get('OSTICKET_PASSWORD')
host = os.environ.get('OSTICKET_HOST')
db = os.environ.get('OSTICKET_DB')

print("Username: " + str(un) + " |Password: " + str(pw) + " |Server: " + str(host) + " |Database: " + str(db)) #debug so we can see where mariadb is trying to connect to/with

def ticketsPerAgent(days):
    names = []  # list of staff names
    openedByName = []  # list for count of opened tickets by agent
    openByName = []
    closedByName = []
    waitingByName = []

    # Connect to MariaDB Platform
    with mariadb.connect(user=un, password=pw, host=host, port=3306, database=db) as con:
        with con.cursor() as cur:  # start an entry cursor
            today = datetime.now()  # get todays date and store it for finding the correct term later

            cur.execute('SELECT ost_ticket.ticket_id, ost_staff.firstname, ost_staff.lastname, ost_ticket_status.name, ost_help_topic.topic, ost_ticket__cdata.subject, ost_ticket.isoverdue, ost_ticket.created, ost_ticket.lastupdate, ost_ticket.closed FROM ost_ticket INNER JOIN ost_staff ON ost_ticket.staff_id = ost_staff.staff_id INNER JOIN ost_ticket_status ON ost_ticket.status_id = ost_ticket_status.id INNER JOIN ost_help_topic ON ost_ticket.topic_id = ost_help_topic.topic_id INNER JOIN ost_ticket__cdata ON ost_ticket.ticket_id = ost_ticket__cdata.ticket_id ORDER BY lastname, ticket_id')
            for entry in cur:  # go through each result from the query above
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
                    if not agentFirst in names:  # if we havent already had a entry for them, we need to create an entry in each list
                        names.append(agentFirst)
                        openedByName.append(0)
                        openByName.append(0)
                        closedByName.append(0)
                        waitingByName.append(0)

                    index = names.index(agentFirst)
                    openedByName[index] += 1  # increment the current value in the count list by 1 for that user
                    if status == 'Closed':
                            closedByName[index] += 1
                    elif status == 'Open':
                            openByName[index] += 1
                    elif status == 'Waiting on User':
                            waitingByName[index] += 1
                    print(entry)
            print(names) # debug
            print(openedByName) # debug
            print(openByName) # debug
            print(closedByName) # debug
            print(waitingByName) # debug

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
    plt.xticks([r + barWidth for r in range(len(names))], names)

    plt.legend()
    plt.show()

def TicketsByCategory(days, topic):
    categories = [] # empty list to hold the names of the categories. x-axis
    counts = [] # empty list to hold the counts of how many times each ticket has appeared. y-axis
    colorPallette = cycle(['palegreen', 'peachpuff', 'firebrick', 'gold', 'seagreen', 'turquoise', 'deepskyblue', 'slateblue', 'plum', 'darkorchid', 'hotpink']) # make a list of possible colors the the bars can be
    colors = [] # empty list of the colors of each bar

    if topic == 'Staff':
        formField = 50 # 50 is the value for our Staff category picker, will be different for other implementations
    elif topic == 'Student':
        formField = 48 # 50 is the value for our Student category picker, will be different for other implementations
    elif topic == 'Parent':
        formField = 42 # 42 is the value for our Parent category picker, will be different for other implementations

    with mariadb.connect(user=un, password=pw, host=host, port=3306, database=db) as con:
        with con.cursor() as cur:  # start an entry cursor
            today = datetime.now()  # get todays date and store it for finding the correct term later
            cur.execute('SELECT ost_ticket.ticket_id, ost_form_entry.id, ost_form_entry.form_id, ost_form_entry.object_id, ost_form_entry_values.field_id, ost_form_entry_values.value, ost_ticket.created FROM ost_ticket INNER JOIN ost_form_entry ON ost_ticket.ticket_id = ost_form_entry.object_id INNER JOIN ost_form_entry_values ON ost_form_entry.id = ost_form_entry_values.entry_id')
            for entry in cur:
                if entry[6] > (today - timedelta(days=days)):
                    # print(entry)
                    if int(entry[4]) == formField: # look at the value of the form_entry_values.field_id and see if it matches the current topic form. 48 is student issue category, 42 is parent, 50 is staff
                        cat = str(entry[5]).split(':') # the query result gives the internal name and then the standard string name separated by a colon, so split them apart
                        categoryName = cat[0].split('"')[1] # just take the internal name of the category and split it by the returned double quotes again to get just the string with no quotes or bracket
                        print("Teacher category: " + categoryName)
                        if not categoryName in categories: # if we havent tracked this category yet, we want to append it to the category list and 'initialize' the count list with a 0 for that slot
                            categories.append(categoryName)
                            counts.append(0)
                            colors.append(next(colorPallette)) # do a cycle through the color pallette and put the next color into the matching color list
                        counts[categories.index(categoryName)] += 1 # find the index of the current category and increment the count for that one by 1

    categories, counts = zip(*sorted(zip(categories, counts))) # zip the categories together into one nice linked list, sort the list, then separate them
    print(categories)
    print(counts)

    # plt.subplots(figsize=(20, 10))
    
    plt.figure(figsize=(8.5,5), dpi=200) # set the size of the figure before we plot anything to it or it will not work
    x = plt.bar(categories, counts, color=colors)

    plt.title(topic + ' Tickets Opened by Category for the Last ' + str(days) + ' days')
    
    plt.xticks(categories, rotation='vertical') # set the printing of the x-axis labels to be vertical so we can actually read them
    
    plt.subplots_adjust(top=.95, bottom=0.35, left=.1, right=.95, hspace=.2) # Tweak spacing to prevent clipping of tick-labels, space everything better
    plt.bar_label(x)
    plt.show()

TicketsByCategory(14, 'Staff') # get the amount of tickets per category from staff for the last 2 weeks
TicketsByCategory(60, 'Staff') # get the amount of tickets per category from staff for the last 2 months
TicketsByCategory(14, 'Parent') # get the amount of tickets per category from parents for the last 2 weeks
TicketsByCategory(60, 'Parent') # get the amount of tickets per category from parents for the last 2 months
TicketsByCategory(14, 'Student') # get the amount of tickets per category from students for the last 2 weeks
TicketsByCategory(60, 'Student') # get the amount of tickets per category from students for the last 2 months
ticketsPerAgent(14) # call the tickets per agent for the last 2 weeks
ticketsPerAgent(60) # do the last 2 months
