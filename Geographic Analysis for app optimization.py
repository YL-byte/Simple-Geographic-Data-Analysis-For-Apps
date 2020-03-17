import math
from datetime import *
from operator import itemgetter
source = 'Source.txt'
destination = 'Results.txt'
min_time = 300 #Seconds
min_dis = 100 #Meters

def read_source_file():
    source_file = open(source, 'r')
    source_text = source_file.read()
    source_file.close()
    source_table = parse_text(source_text)
    return source_table
######################################################
def parse_text(source_text, new_line_char = '\n', new_cell_char = '\t', number_of_columns = 4):
    new_table = []
    cell_value = ''
    current_row = []
    illegal_cell_values = ['',' ',None,'\t','\n']
    for char in source_text:
        #New Row - Reset Cell and Row after append
        if char == new_line_char:
            #Check if new line is legal = Contains only two entities
            current_row.append(cell_value)
            if len(current_row) == number_of_columns and current_row[0] not in illegal_cell_values and current_row[1] not in illegal_cell_values:
                new_table.append(current_row)
            current_row = []
            cell_value = ''

        #New cell - Reset cell after append
        elif char == new_cell_char:
            current_row.append(cell_value)
            cell_value = ''

        #Add the char to current cell value
        else:
            cell_value += char
    #Append last cell to row and last row to table if legal
    if len(current_row) > 0:
        current_row.append(cell_value)
        new_table.append(current_row)
    return new_table
######################################################
def sort_by_time(table, time_index = 3):
    table = canonize_time(table, time_index)
    for row in table:
        #Add timestamp to each row for indexing
        timestamp = time_to_epoch(row[time_index], '01/01/1970 00:00:00')
        row.append(timestamp)
    table = sorted(table, key=itemgetter(-1))
    for row in table:
        #Remove timestamp
        del row[-1]
    return table
######################################################
def canonize_time(time, time_index):
    for row in table:
        if len(row[time_index]) == 16:
            row[time_index] = row[time_index] + ":00"
    return table
######################################################
def calc_distance(lat_a, long_a, lat_b, long_b):
    #Haversine formula
    long_a = float(long_a)
    lat_a = float(lat_a)
    long_b = float(long_b)
    lat_b = float(lat_b)
    R = 6371 #Earth's Radius
    d_lat = degreeToRadians(float(lat_a) - float(lat_b))
    d_long = degreeToRadians(float(long_a) - float(long_b))
    a = math.sin(d_lat / 2) ** 2 + math.cos(lat_a) * math.cos(lat_b) * math.sin(d_long / 2) ** 2
    b = 2 * math.asin(math.sqrt(a))
    return b * R * 1000 #Distance in meters
######################################################
def degreeToRadians(deg):
    return deg * math.pi / 180
######################################################
def time_to_epoch(date_a, date_b):
    date_a = datetime.strptime(date_a, '%d/%m/%Y %X')
    date_b = datetime.strptime(date_b, '%d/%m/%Y %X')
    return abs(int((date_a - date_b).total_seconds()))
######################################################
def is_small_list_in_large_list(small_list, large_list):
    value = True
    for row in small_list:
        if row not in large_list:
            value = False
    return value
######################################################
def remove_contained_groups(groups):
    new_table = []
    for current_group in sorted(groups, key = len):
        add_current_group = True
        for compared_group in sorted(groups, key = len):
            if len(compared_group) > len(current_group):
                if is_small_list_in_large_list(current_group, compared_group) == True:
                    add_current_group = False
        if add_current_group == True and current_group not in new_table:
            new_table.append(current_group)
    return new_table
######################################################
def create_groups(table):
    groups_table = []
    for current_row_index in range(0, len(table)):
        #Compare each row to all exceeding rows
        current_row = table[current_row_index]
        new_group = [current_row]
        distinct_clients_in_group = []
        client_a = current_row[0]
        distinct_clients_in_group.append(client_a)
        lat_a = current_row[1]
        long_a = current_row[2]
        date_a = current_row[3]
        for compared_row_index in range(current_row_index + 1, len(table)):
            compared_row = table[compared_row_index]
            date_b = compared_row[3]
            #because we indexed the table according to the timestamp - once time dif is larger than min we can break
            if time_to_epoch(date_a, date_b) > min_time:
                check_and_append(new_group, current_row, groups_table, distinct_clients_in_group)
                break
            elif compared_row != current_row:
                client_b = compared_row[0]
                if client_b not in distinct_clients_in_group:
                    distinct_clients_in_group.append(client_b)
                lat_b = compared_row[1]
                long_b = compared_row[2]
                if calc_distance(lat_a, long_a, lat_b, long_b) <= min_dis:
                    new_group.append(compared_row)
        check_and_append(new_group, current_row, groups_table, distinct_clients_in_group)
    return groups_table
######################################################
def check_and_append(new_group, current_row, groups_table, distinct_clients_in_group):
    if new_group != [current_row] and sorted(new_group) not in groups_table and len(distinct_clients_in_group) > 1:
        # Add the number of clients involved to each row
        for row in new_group:
            row.append(str(len(distinct_clients_in_group)))
        groups_table.append(sorted(new_group))
    return groups_table
######################################################
def add_additional_values_to_group(groups_table):
    new_table = []
    group_index = 1
    for group in groups_table:
        new_group = []
        avg_lat = 0
        avg_long = 0
        group_length = len(group)
        for row in group:
            #Calc AVG lat and long
            current_row_lat = float(row[1])
            current_row_long = float(row[2])
            avg_lat += current_row_lat
            avg_long += current_row_long
        avg_lat = avg_lat / group_length
        avg_long = avg_long / group_length
        for row in group:
            current_row_lat = float(row[1])
            current_row_long = float(row[2])
            row.append(str(avg_lat))
            row.append(str(avg_long))
            new_row = [str(group_index), row[0], current_row_lat, current_row_long, row[3], row[4], str(avg_lat), str(avg_long)]
            new_group.append(new_row)
        new_table.append(new_group)
        group_index += 1
    return new_table
######################################################
def write_to_results(groups_table):
    results_file = open(destination, 'w')
    results_file.write('Group Index\t')
    results_file.write('Client\t')
    results_file.write('Latitude\t')
    results_file.write('Longitude\t')
    results_file.write('Time\t')
    results_file.write('Number_of_Clients\t')
    results_file.write('Avg_Latitude\t')
    results_file.write('Avg_Longitude\n')
    for group in groups_table:
        for row in group:
            for cell in row:
                results_file.write(str(cell) + '\t')
            results_file.write('\n')
######################################################
print ('Geographic Analysis for app optimization')
print ('Min Time: ' + str(min_time) +' Seconds; Min Distance: ' + str(min_dis) +' Meters;')
table = read_source_file() #Read the Data from the source file
table = sort_by_time(table) #Sort the table according to timestamp - to significantly reduce runtime
groups_table = create_groups(table) #Create groups based on events
groups_table = remove_contained_groups(groups_table) #Remove groups which are contained in larger groups
groups_table = add_additional_values_to_group(groups_table) #Such as avg_lat, avg_long
write_to_results(groups_table)