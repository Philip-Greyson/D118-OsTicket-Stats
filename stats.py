# https://mariadb.com/resources/blog/how-to-connect-python-programs-to-mariadb/
# https://www.geeksforgeeks.org/bar-plot-in-matplotlib/
# https://datatofish.com/bar-chart-python-matplotlib/
# https://pypi.org/project/img2pdf/


# ----- Done -----
# Get the last x days of tickets, plot how many open/closed/waiting per agent
# Get the last x days of tickets, plot how many per help category

# Get the last x days of tickets, plot how many open and closed per day
# Get the last x months of tickets, plot how many open/closed per month

# Get last x days of tickets, plot average close time by agent and overall in district

# ---- TO-DO -----
# Get the last fiscal year (july 1), plot how many open/closed per week? have to use relative time delta for week additions, and use the weekday function to find the mondays https://dateutil.readthedocs.io/en/stable/relativedelta.html
# Get the breakdown of student/parent/staff tickets in last month?

# For single agent, look at average ticket closing time per month/week/etc
# For single agent, look at average first response time per month/week/etc

# Save all plots to files
# Take all plot files and put them together with img2pdf


# Module Imports
from audioop import avg
import numpy as np
import matplotlib.pyplot as plt
import mariadb # needed to connect to OsTicket database
import datetime  # used to get current date for historical data
from datetime import * # needed to do addition/subtraction of days from a datetime value
from dateutil.relativedelta import * # neeeded to do addition/subtraction of months, weeks, years, etc from a datetime value
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
    total_bar = plt.bar(br1, openedByName, color='gold', width=barWidth, edgecolor='grey', label='Total')
    open_bar = plt.bar(br2, openByName, color='firebrick', width=barWidth, edgecolor='grey', label='Open')
    closed_bar = plt.bar(br3, closedByName, color='limegreen', width=barWidth, edgecolor='grey', label='Closed')
    waiting_bar = plt.bar(br4, waitingByName, color='deepskyblue', width=barWidth, edgecolor='grey', label='Waiting')
    plt.bar_label(total_bar, label_type='center')
    plt.bar_label(open_bar)

    # Adding Xticks
    plt.xlabel('User', fontweight='bold', fontsize=15)
    plt.ylabel('Tickets', fontweight='bold', fontsize=15)
    plt.xticks([r + barWidth for r in range(len(names))], names)

    plt.legend()
    plt.show()

def ticketsByCategory(days, topic):
    categories = [] # empty list to hold the names of the categories. x-axis
    counts = [] # empty list to hold the counts of how many times each ticket has appeared. y-axis
    colorPallette = cycle(['firebrick', 'chocolate', 'peachpuff', 'gold', 'palegreen', 'seagreen', 'turquoise', 'deepskyblue', 'slateblue', 'plum', 'darkorchid', 'hotpink']) # make a list of possible colors the the bars can be
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

def overallTicketsByDay(amount):
    dates = []
    opened = []
    closed = []
    with mariadb.connect(user=un, password=pw, host=host, port=3306, database=db) as con:
        with con.cursor() as cur:  # start an entry cursor
            today = datetime.now()  # get todays date and store it for finding the correct term later
            targetStart = today - timedelta(days=int(amount)) # find the target start date from 
            targetStart = targetStart.strftime('%Y%m%d') # convert to the proper format of YYYYMMDD for sql query
            print(targetStart) # debug
            cur.execute("SELECT created FROM ost_ticket WHERE created >= '" + targetStart + "'") # do just the created part since the close date may be in the last 2 weeks but opened way earlier
            for entry in cur:
                day = entry[0].strftime('%-m/%-d')
                if not day in dates:
                    dates.append(day)
                    opened.append(0)
                    closed.append(0)
                opened[dates.index(day)] += 1 # add 1 count to the current day index on the oepened list
            cur.execute("SELECT closed FROM ost_ticket WHERE closed >= '" + targetStart + "'") # do just the created part since the close date may be in the last 2 weeks but opened way earlier
            for entry in cur:
                # print(entry)
                if entry[0]:
                    day = entry[0].strftime('%-m/%-d')
                    if not day in dates: # this probably wont be used since usually it will be populated by the created query, but have it just in case
                        dates.append(day)
                        opened.append(0)
                        closed.append(0)
                    closed[dates.index(day)] += 1 # add 1 count to the current day index on the oepened list
            print(dates)
            print(opened)
            print(closed)

    plt.figure(figsize=(8.5,5), dpi=200) # set the size of the figure before we plot anything to it or it will not work
    plt.plot(dates, opened, 'bo', linewidth=.5, linestyle='--', label='Opened')
    plt.plot(dates, closed, 'go', linewidth=.5, linestyle='--', label='Closed')
    plt.title('Tickets Opened/Closed in the last ' + str(amount) + ' days')
    plt.xticks(dates, rotation='vertical') # set the printing of the x-axis labels to be vertical so we can actually read them
    plt.grid(True)
    plt.legend() # show the legend in the top right corner
    plt.show()

def overallTicketsByMonth(amount):
    months = []
    opened = []
    closed = []
    with mariadb.connect(user=un, password=pw, host=host, port=3306, database=db) as con:
        with con.cursor() as cur:  # start an entry cursor
            today = datetime.now()  # get todays date and store it for finding the correct term later
            targetStart = today - relativedelta(months=int(amount)) # find the target start date from 
            targetStart = targetStart.strftime('%Y%m%d') # convert to the proper format of YYYYMMDD for sql query
            print(targetStart) # debug
            cur.execute("SELECT created FROM ost_ticket WHERE created >= '" + targetStart + "'") # do just the created part since the close date may be in the last 2 weeks but opened way earlier
            for entry in cur:
                month = entry[0].strftime('%m/%y') # get the created date as mm/yy
                if not month in months:
                    months.append(month)
                    opened.append(0)
                    closed.append(0)
                opened[months.index(month)] += 1 # add 1 count to the current day index on the oepened list
            cur.execute("SELECT closed FROM ost_ticket WHERE closed >= '" + targetStart + "'") # do just the created part since the close date may be in the last 2 weeks but opened way earlier
            for entry in cur:
                # print(entry)
                if entry[0]:
                    month = entry[0].strftime('%m/%y') # get the closed date as mm/yy
                    if not month in months: # this probably wont be used since usually it will be populated by the created query, but have it just in case
                        months.append(month)
                        opened.append(0)
                        closed.append(0)
                    closed[months.index(month)] += 1 # add 1 count to the current day index on the oepened list
            print(months)
            print(opened)
            print(closed)

    plt.figure(figsize=(8.5,5), dpi=200) # set the size of the figure before we plot anything to it or it will not work
    plt.plot(months, opened, 'bo', linewidth=.5, linestyle='--', label='Opened')
    plt.plot(months, closed, 'go', linewidth=.5, linestyle='--', label='Closed')
    plt.title('Tickets Opened/Closed in the last ' + str(amount) + ' months')
    plt.xticks(months, rotation='vertical') # set the printing of the x-axis labels to be vertical so we can actually read them
    plt.grid(True)
    plt.legend() # show the legend
    plt.show()

def closeTimePerAgentByDays(amount):
    agents = {} # create dictionary for ids, names
    avgCloseTimeDeltas = [] # empty list to store the close time deltas (days, seconds, microseconds) in
    allCloseTimeDeltas = [] # empty list to store the total (not per agent) time deltas in
    avgCloseTimeHours = [] # list to store the close time in hours in

    colorPallette = cycle(['firebrick', 'chocolate', 'peachpuff', 'gold', 'palegreen', 'seagreen', 'turquoise', 'deepskyblue', 'slateblue', 'plum', 'darkorchid', 'hotpink']) # make a list of possible colors the the bars can be
    colors = [] # empty list of the colors of each bar

    today = datetime.now()  # get todays date and store it for finding the correct term later
    targetStart = today - timedelta(days=int(amount)) # find the target start date
    targetStart = targetStart.strftime('%Y%m%d') # convert to the proper format of YYYYMMDD for sql query

    # Connect to MariaDB Platform
    with mariadb.connect(user=un, password=pw, host=host, port=3306, database=db) as con:
        with con.cursor() as cur:  # start an entry cursor
            cur.execute('SELECT staff_id, firstname FROM ost_staff WHERE isactive = 1') # just get all staff_id for active agents, store them in another list
            for agent in cur:
                if not agent[0] in agents: # if they dont exist in the dict then we want to add them to it
                    agents[str(agent[0])] = str(agent[1]) # append the id, name pair to the agent dictionary
            for ID in agents.copy(): # go through the keys (ids) in a copy of the agents dict, so we can make changes to the original one at the same time
                agentCloseTimes = [] # empty list to sotre all the individual close times in before averaging them
                # print(ID) # debug
                cur.execute("SELECT ost_ticket.created, ost_ticket.closed, ost_staff.firstname FROM ost_ticket INNER JOIN ost_staff ON ost_ticket.staff_id = ost_staff.staff_id WHERE ost_ticket.staff_id = " + ID + " AND ost_ticket.created >= '" + targetStart + "'")
                results = cur.fetchall() # do a fetchall and store the output in results so we can see how many we have
                if results and (len(results) > 4): # we want to skip any user who only have 4 or fewer tickets in the time period as they might skew things
                    for entry in results:
                        # print(entry) # debug
                        if entry[1]: # if there is a close time
                            closeTime = entry[1] - entry[0]
                            agentCloseTimes.append(closeTime) # put the close time in the per-agent list
                            allCloseTimeDeltas.append(closeTime) # put the close time in the overall district list
                            # print(closeTime)
                    if len(agentCloseTimes) != 0: # we want to ignore any agents without any actual close times (they had tickets but did not close them)
                        # print(allCloseTimes)
                        avgCloseTime = sum(agentCloseTimes, timedelta(0)) / len(agentCloseTimes) # get the average by adding up all the time deltas and dividing by instances
                        avgCloseTimeDeltas.append(avgCloseTime) # put the avg close time in the list for graph
                        print(agents[ID] + ' Average Close Time for last ' + str(amount) + ' days: ' + str(avgCloseTime))
                        colors.append(next(colorPallette)) # do a cycle through the color pallette and put the next color into the matching color list
                    else:
                        print('Removing agent due to no close times')
                        agents.pop(ID)
                else:
                    print('Removing agent due to low ticket count')
                    agents.pop(ID) # remove the ID/name pair from the main dict

    names = list(agents.values()) # get the names from the values of the agents dict for plotting on the x-axis

    # Add in the district average value
    names.append("District") # add a district name to the end of the name list
    colors.append('black') # set the color for the average to be gray
    totalAvgCloseTime = sum(allCloseTimeDeltas, timedelta(0)) / len(allCloseTimeDeltas) # get the total average by adding up all the time deltas and dividing by entries
    avgCloseTimeDeltas.append(totalAvgCloseTime) # add the overall average to the end of the per-agent deltas list
    

     # convert the time detlas to hours so we can graph them
    for delta in avgCloseTimeDeltas:
        hours = (delta.days * 24) + delta.seconds / 3600
        avgCloseTimeHours.append(hours)

    print(names)
    print(avgCloseTimeDeltas)
    print(avgCloseTimeHours)
    

    # Make the plot
    plt.figure(figsize=(8.5,5), dpi=200) # set the size of the figure before we plot anything to it or it will not work
    plt.title('Average Close Time in Hours for the last ' + str(amount) + ' days by Agent')
    graph = plt.bar(names, avgCloseTimeHours, color=colors)
    plt.ylabel('Hours to Close')
    plt.bar_label(graph, fmt='%i') # put a label on each bar
    # plt.xticks(names, rotation='vertical') # set the printing of the x-axis labels to be vertical so we can actually read them
    plt.grid(axis='y') # only show the horizontal lines on the grid
    plt.show()


# ticketsByCategory(14, 'Staff') # get the amount of tickets per category from staff for the last 2 weeks
# ticketsByCategory(60, 'Staff') # get the amount of tickets per category from staff for the last 2 months
# ticketsByCategory(14, 'Parent') # get the amount of tickets per category from parents for the last 2 weeks
# ticketsByCategory(60, 'Parent') # get the amount of tickets per category from parents for the last 2 months
# ticketsByCategory(14, 'Student') # get the amount of tickets per category from students for the last 2 weeks
# ticketsByCategory(60, 'Student') # get the amount of tickets per category from students for the last 2 months
# ticketsPerAgent(14) # call the tickets per agent for the last 2 weeks
# ticketsPerAgent(60) # do the last 2 months
# overallTicketsByDay(14) # get the overall ticket opened/closed stats for the last 2 weeks by day
# overallTicketsByDay(30) # get the overall ticket opened/closed stats for the last month by day
# overallTicketsByMonth(18) # get the overall ticket opened/closed stats for the 18 months by month
closeTimePerAgentByDays(14)
closeTimePerAgentByDays(90)