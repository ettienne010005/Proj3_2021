import sqlite3
import re
import plotly.graph_objects as go 

# proj3_choc.py
# You can change anything in this file you want as long as you pass the tests
# and meet the project requirements! You will need to implement several new
# functions.

# Part 1: Read data from a database called choc.db
DBNAME = 'choc.sqlite'
connection = sqlite3.connect(DBNAME)
cursor = connection.cursor()

# Part 1: Implement logic to process user commands
def process_command(command):
    cmd_list = command.split()
    if len(cmd_list) == 0:
        return 'Command not recognized:'

    #default variables for parsing cmd
    cmd_type = 'none'
    country_region = [] #default is empty 
    sell_source = 'none'
    sort_by = 'Rating'
    top_bottom = 'DESC' #default is top which is DESC 
    num_results = 10
    barplot = 'N'

    #parsing differnt types of cmd
    if cmd_list[0] == "bars":    
        cmd_type = 'bars'
    elif cmd_list[0] == "companies":
        cmd_type = 'companies' 
    elif cmd_list[0] == "countries":
        cmd_type = 'countries' 
    elif cmd_list[0] == "regions":
        cmd_type = 'regions' 
    else:
        return 'Command not recognized:' + command

    for i in range(1,len(cmd_list)):
        if cmd_list[i][0:7] == "country":
            #return wrong cmd if not match the expression 
            if not bool(re.match(r"^country=\D\D$",cmd_list[i])):
                return 'Command not recognized:' + command
            else:
                country_region = ['Alpha2',cmd_list[i][-2:]]

        elif cmd_list[i][0:6] == "region":
            #return wrong cmd if not match the expression 
            if not bool(re.match(r"^region=.*\D",cmd_list[i])):
                return 'Command not recognized:' + command
            country_region = ['Region',cmd_list[i][7:]]     

        elif cmd_list[i] == "sell":
            sell_source = "sell"
            
        elif cmd_list[i] == "source":
            sell_source = "source"

        elif cmd_list[i] == "ratings":
            sort_by = 'Rating'

        elif cmd_list[i] == "cocoa":
            sort_by = 'CocoaPercent'

        elif cmd_list[i] == "number_of_bars":
            sort_by = 'COUNT(*)' #query string for num of bars
            
        elif cmd_list[i] == "top":
            top_bottom = 'DESC'

        elif cmd_list[i] == "bottom":
            top_bottom = 'ASC'
            
        elif cmd_list[i].isnumeric():
            num_results = cmd_list[i]

        elif cmd_list[i] == 'barplot':
            barplot = 'Y'
   
        else: #wrong command
            return 'Command not recognized:' + command

    #error handling for invalid option combinations 
    if (cmd_type == 'bars' and sort_by == 'COUNT(*)') or (cmd_type == 'companies' and sell_source != 'none') or (cmd_type == 'countries' and ((len(country_region)!=0) and (country_region[0] == 'Alpha2'))) or (cmd_type == 'regions' and len(country_region) != 0):
        return 'Command with invalid option:' + command

    query = query_string(cmd_type,country_region,sell_source,sort_by,top_bottom,num_results)
    result = cursor.execute(query).fetchall()

    if barplot == 'Y':
        plot_bar(result,cmd_type,sort_by)

    return result

#new function for ploting query results
def plot_bar(result,cmd_type,sort_by):
    ''' plot the barplot based on the query result

    Parameters
    ----------
    list
        a list of tuples that represent the query result
    string
        command type to determine the values to plot in x axis
    string
        sorted type to determine the values to plot in y axis
        
    Returns
    -------
    None
       
    '''
    x_axis = []
    y_axis = []

    if cmd_type == 'bars':
        for row in result:
            x_axis.append(row[0])
            if sort_by == 'Rating':
                y_axis.append(row[3])
            else:
                y_axis.append(row[4]) 

    elif cmd_type == 'regions':
        for row in result:
            x_axis.append(row[0])
            y_axis.append(row[1]) 
    
    else:
        for row in result:
            x_axis.append(row[0])
            y_axis.append(row[2])   

    bar_data = go.Bar(x=x_axis, y=y_axis)
    if sort_by == "COUNT(*)":
        basic_layout = go.Layout(title=f"{cmd_type} sorted by num of bars")
    else:    
        basic_layout = go.Layout(title=f"{cmd_type} sorted by {sort_by}")
    fig = go.Figure(data=bar_data, layout=basic_layout)  

    fig.show()    
            

#new function for constructing query string 
def query_string(cmd_type,country_region,sell_source,sort_by,top_bottom,num_results):
    ''' Constructs the query sting based on the given variable values
    
    Parameters
    ----------
    variables  
        cmd_type: what type of command is it e.g. bars
        country_region: a list of storing country/region and its name
        sell_source: filtered by source or sell
        sort_by: sorted by what number e.g. ratings
        top_bottom: displace from the top or bottom
        num_results: displace how many results 
        barplot: diplace barplot or not 
    
    Returns
    -------
    string 
        a query string for query the SQL database
    '''

    query_string = ''' '''
    #bars
    if cmd_type == 'bars':
        if sell_source == 'source':
            query_string = query_string + ('''SELECT B.SpecificBeanBarName, B.Company, C2.EnglishName, B.Rating, B.CocoaPercent, C1.EnglishName\nFROM Bars B, Countries C1, Countries C2 ''')
        else:
            query_string = query_string + ('''SELECT B.SpecificBeanBarName, B.Company, C1.EnglishName, B.Rating, B.CocoaPercent, C2.EnglishName\nFROM Bars B, Countries C1, Countries C2 ''')

        if len(country_region) == 0:
            query_string = query_string + ('''\nWHERE B.BroadBeanOriginId = C1.Id AND B.CompanyLocationId = C2.Id''')
        else:
            query_string = query_string + (f'''\nWHERE C1.{country_region[0]} = "{country_region[1]}" ''')
            if sell_source == 'source':
                query_string = query_string + ('''AND B.BroadBeanOriginId = C1.Id AND B.CompanyLocationId = C2.Id''')
            else:
                query_string = query_string + ('''AND B.BroadBeanOriginId = C2.Id AND B.CompanyLocationId = C1.Id''')
        
        query_string = query_string + (f'''\nORDER BY B.{sort_by} {top_bottom}''')
        query_string = query_string + (f'''\nLIMIT {num_results}''')

    #companies
    elif cmd_type == 'companies':
        query_string = '''SELECT DISTINCT B.Company, C1.EnglishName, '''
        if sort_by == 'Rating':
            query_string = query_string + f'''AVG(B.{sort_by})\nFROM Bars B, Countries C1 '''
        elif sort_by == 'CocoaPercent':
            query_string = query_string + f'''AVG(B.{sort_by})\nFROM Bars B, Countries C1 '''
        else:
            query_string = query_string + f'''{sort_by}\nFROM Bars B, Countries C1 '''
        if len(country_region) == 0:
            query_string = query_string + ('''\nWHERE B.CompanyLocationId = C1.Id ''')
        else:
            query_string = query_string + (f'''\nWHERE C1.{country_region[0]} = "{country_region[1]}" AND B.CompanyLocationId = C1.Id ''')

        query_string = query_string + ('''\nGROUP BY B.Company\nHAVING COUNT(*) > 4''')

        if sort_by == 'Rating':
            query_string = query_string + (f'''\nORDER BY AVG(B.{sort_by}) {top_bottom}''')
        elif sort_by == 'CocoaPercent':
            query_string = query_string + (f'''\nORDER BY AVG(B.{sort_by}) {top_bottom}''')
        else:
            query_string = query_string + (f'''\nORDER BY {sort_by} {top_bottom}''')
        query_string = query_string + (f'''\nLIMIT {num_results}''')

    #countries
    elif cmd_type == 'countries':
        query_string = '''SELECT DISTINCT C1.EnglishName, C1.Region, '''
        if sort_by == 'Rating':
            query_string = query_string + f'''AVG(B.{sort_by})\nFROM Bars B, Countries C1 '''
        elif sort_by == 'CocoaPercent':
            query_string = query_string + f'''AVG(B.{sort_by})\nFROM Bars B, Countries C1 '''
        else:
            query_string = query_string + f'''{sort_by}\nFROM Bars B, Countries C1 '''
        
        if len(country_region) != 0:
            query_string = query_string + (f'''\nWHERE C1.{country_region[0]} = "{country_region[1]}" ''')
            if sell_source == 'source':
                query_string = query_string + ('''AND B.BroadBeanOriginId = C1.Id ''')
            else:
                query_string = query_string + ('''AND B.CompanyLocationId = C1.Id ''')
        else:
            query_string = query_string + (f'''\nWHERE  ''')
            if sell_source == 'source':
                query_string = query_string + ('''B.BroadBeanOriginId = C1.Id ''')
            else:
                query_string = query_string + ('''B.CompanyLocationId = C1.Id ''')

        query_string = query_string + ('''\nGROUP BY C1.EnglishName\nHAVING COUNT(*) > 4''')
        if sort_by == 'Rating':
            query_string = query_string + (f'''\nORDER BY AVG(B.{sort_by}) {top_bottom}''')
        elif sort_by == 'CocoaPercent':
            query_string = query_string + (f'''\nORDER BY AVG(B.{sort_by}) {top_bottom}''')
        else:
            query_string = query_string + (f'''\nORDER BY {sort_by} {top_bottom}''')
        query_string = query_string + (f'''\nLIMIT {num_results}''')


    #regions
    elif cmd_type == 'regions':
        query_string = '''SELECT DISTINCT C1.Region, '''
        if sort_by == 'Rating':
            query_string = query_string + f'''AVG(B.{sort_by})\nFROM Bars B, Countries C1 '''
        elif sort_by == 'CocoaPercent':
            query_string = query_string + f'''AVG(B.{sort_by})\nFROM Bars B, Countries C1 '''
        else:
            query_string = query_string + f'''{sort_by}\nFROM Bars B, Countries C1 '''

        if sell_source == 'source':
            query_string = query_string + ('''\nWHERE B.BroadBeanOriginId = C1.Id ''')
        else:
            query_string = query_string + ('''\nWHERE B.CompanyLocationId = C1.Id ''')

        query_string = query_string + ('''\nGROUP BY C1.Region\nHAVING COUNT(*) > 4''')
        if sort_by == 'Rating':
            query_string = query_string + (f'''\nORDER BY AVG(B.{sort_by}) {top_bottom}''')
        elif sort_by == 'CocoaPercent':
            query_string = query_string + (f'''\nORDER BY AVG(B.{sort_by}) {top_bottom}''')
        else:
            query_string = query_string + (f'''\nORDER BY {sort_by} {top_bottom}''')
        query_string = query_string + (f'''\nLIMIT {num_results}''')

    return query_string


def load_help_text():
    with open('Proj3Help.txt') as f:
        return f.read()

# Part 2 & 3: Implement interactive prompt and plotting. We've started for you!
def interactive_prompt():
    help_text = load_help_text()
    response = ''
    while response != 'exit':
        print('\n')
        response = input('Enter a command: ')
        if response == 'exit':
            break
        if response == 'help':
            print(help_text)
            continue
        result = process_command(response)
        # print(result)
        if ('Command not recognized:' in result) or ('Command with invalid option:' in result):
            print(result)
        else:
            for row in result:
                for i in range(len(row)):
                    if type(row[i]) == str and len(row[i]) > 12:
                        if i == len(row) - 1:
                            print('{:<13}...  '.format(row[i][0:12]))
                        else:
                            print('{:<13}...  '.format(row[i][0:12]), end="")
                    else:
                        if i == len(row) - 1:
                            print('{:<18}'.format(row[i]),)
                        else:
                            print('{:<18}'.format(row[i]), end="")
            
    
    print('Bye')


# Make sure nothing runs or prints out when this file is run as a module/library
if __name__=="__main__":

    interactive_prompt()
