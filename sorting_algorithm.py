import numpy as np
import mysql.connector
from mysql.connector import Error

# GLOBAL VARIABLES: CHANGE ONLY THIS WHEN RUNNING THE PROGRAM UNLESS YOU
#ACTUALLY UNDERSTAND THIS CODE. ANYTHING CHANGED HERE WON'T BREAK THE CODE'

# NUMBER OF JOBS AVAILABLE FOR EACH COMPANY/POSITION:
#Please ensure these variables are in the same order as they are on the table

number_of_jobs = []

total_jobs = 56

job1 = 5
number_of_jobs.append(["job1", job1])

job2 = 5
number_of_jobs.append(["job2", job2])

job3 = 5
number_of_jobs.append(["job3", job3])

job4 = 10
number_of_jobs.append(["job4", job4])

job5 = 5
number_of_jobs.append(["job5", job5])

job6 = 5
number_of_jobs.append(["job6", job6])

job7 = 5
number_of_jobs.append(["job7", job7])

job8 = 8
number_of_jobs.append(["job8", job8])

job9 = 3
number_of_jobs.append(["job9", job9])

job10 = 3
number_of_jobs.append(["job10", job10])

job11 = 1
number_of_jobs.append(["job11", job11])

job12 = 1
number_of_jobs.append(["job12", job12])

#-----------------------------------------------------

# FOR WRITING TO CSV FILE AT END: DO NOT TOUCH
list_of_names = []
save_to_csv = []

#-----------------------------------------------------

def reduce_matrix(mat):

    '''
    Function reduces matrix, creating zeros used for assignments later:
    #1 Reduces rows by subtracting minimum value from each row from every element
    #2 Reduces columns the same way
    '''

    reduced_mat = mat
    
    #row reduction
    for row_num in range(mat.shape[0]):
        reduced_mat[row_num] = reduced_mat[row_num] - np.min(reduced_mat[row_num])
    
    #column reduction
    for col_num in range(mat.shape[1]):
        reduced_mat[:,col_num] = reduced_mat[:,col_num] - np.min(reduced_mat[:,col_num])

    return(reduced_mat)
    

def possible_assignment(zero_mat, mark_zero):
    
    '''
    Function finds row with min zeroes while there's still zeroes until there's a zero marked
    for every row/column combo. 
    
    Essentially, it finds a possible assignment, which will be 
    checked for validity while making a covering
    '''
    
    while (0 in zero_mat):
        
        min_row_index = -1
        min_row_zeroes = 99999
        
        
        for row_num in range(zero_mat.shape[0]): 
            if min_row_zeroes > np.sum(zero_mat[row_num] == 0):
                if np.sum(zero_mat[row_num] == 0) > 0:
                    min_row_index = row_num
                    min_row_zeroes = np.sum(zero_mat[row_num] == 0)
                
        
        if min_row_index > -1:
            column_index = np.where(zero_mat[min_row_index] == 0)[0][0]
            #marks where the chosen zero is as a possible assignment
            mark_zero.append((min_row_index, column_index))

            #an assignment(zero) for that row(student) and column(job) has been made
            #so even if there's another zero in that column, remove it by marking row+column as 1
            #symbolizes the row(student) and column(job) being "taken up"
            zero_mat[min_row_index, :] = 1
            zero_mat[:, column_index] = 1


def mark_matrix(cur_mat):

    '''
    Tests validity of possible_assignment(). Does this by finding the MINIMUM POSSIBLE COVERING
    made with rows+columns for all ASSIGNED/MARKED zeros.

    Minimum possible covering is found using the method explained in Hungarian Algorithm Wikepedia

    If number of rows+columns needed for minimum possible covering != dimensions of matrix
    (number of students), the assignment failed and we must retry. Will loop back to possible()
    '''

    temp_mat = cur_mat.copy() #possible_assignment() mutates the array so we give it a copy

    marked_zero = []
    possible_assignment(temp_mat, marked_zero)
    #marked_zero contains the results of possible_assignment()

    dim = cur_mat.shape[0] 
    
    #Begin finding min covering here
    marked_rows = []
    marked_cols = []

    #Step 1: mark all rows with no assignments
    #(by finding those with assignments and subtracting from total)
    for i in range(len(marked_zero)):
        marked_rows.append(marked_zero[i][0])
        
    temp1 = set(marked_rows)
    temp2 = list(range(0,dim))
    
    marked_rows = [x for x in temp2 if x not in temp1]


    #Step 2 and 3: Repeat and switch in a loop until no new rows and columns are being marked
    
    rowcolswitch = True
    check_assignment_is_made = 0
    
    while True:
        
        # Step 2: Mark all columns having zeros in newly marked rows
        if rowcolswitch == True:
            for i in marked_rows:
                for j in range(0,dim):
                    if cur_mat[i,j] == 0:
                        if j not in marked_cols:
                            check_assignment_is_made = check_assignment_is_made + 1
                            marked_cols.append(j)

            rowcolswitch = False
        
        # Step 3: Mark all rows having assignments in newly marked columns 
        else:
            for i in marked_cols:
                for j in range(len(marked_zero)):
                    if i == marked_zero[j][1]:
                        if marked_zero[j][0] not in marked_rows:
                            check_assignment_is_made = check_assignment_is_made + 1
                            marked_rows.append(marked_zero[j][0])

            rowcolswitch = True
    
        if (check_assignment_is_made < 2):
            break

        if rowcolswitch == True:
            check_assignment_is_made = 0
            
        
    #Step 4: Minimum covering made with marked columns and UNMARKED ROWS, so invert marked rows
    temp1 = set(marked_rows)
    temp2 = list(range(0,dim))
    marked_rows = [x for x in temp2 if x not in temp1]
    
    return(marked_zero, marked_rows, marked_cols)


def adjust_matrix(cur_mat, cover_rows, cover_cols):

    '''
    Only adjust the matrix if possible_assignment() failed as verified by mark_matrix()

    From the unmarked elements (not in min covering/marked rows/columns), find the min.  
    Subtract min from all unmarked elements and add it to all elements covered by both
    a marked column AND marked row
    '''

    dim = len(cur_mat)
        
    min_num = 99999

    

    #Find min from unmarked elements
    for row in range(0,dim):
        if row not in cover_rows:
            for i in range(0,dim):
                if i not in cover_cols and min_num > cur_mat[row,i]:
                    min_num = cur_mat[row,i]

    
    for row in range(0,dim):
        #Find unmarked elements, and subtract min
        if row not in cover_rows:
            for i in range(0,dim):
                if i not in cover_cols:
                    cur_mat[row,i] = cur_mat[row,i] - min_num

        #Find doubly marked elements, and add min
        else:
            for i in range(0,dim):
                if i in cover_cols:
                    cur_mat[row,i] = cur_mat[row,i] + min_num
                

    return cur_mat


def hungarian_algorithm(mat): 

    '''
    This function performs the actual algorithm, using the 4 functions defined above as 4 steps

    It will loop until the minimum possible covering == dimensions of matrix(number of students)
    as that means that the possible assignment is in fact THE BEST assignment
    '''

    dim = mat.shape[0]
    zero_count = 0

    # Step 1: reduce matrix
    cur_mat = reduce_matrix(mat)
    
    #while minimum possible covering != dimensions of matrix(number of students)
    while zero_count < dim:
        
        # Step 2: find a possible assignment, possible_assignment() called in mark_matrix
        # Step 3: find the min covering of all CURRENTLY assigned zeros of the matrix
        marked_zeros, marked_rows, marked_cols = mark_matrix(cur_mat)
                
        zero_count = len(marked_rows) + len(marked_cols)
        print("loading", zero_count, "/", dim)

        if zero_count < dim:
            #step 4: if assignment fails (min covering != dimensions), adjust matrix
            cur_mat = adjust_matrix(cur_mat, marked_rows, marked_cols)
            
    return marked_zeros


def save_final_assignment(mat, pos):

    total = 0 #Will give total number of points assigned.

    # for every assignment, this will convert numbers (x,y) to human readable assignment
    # x,y are converted to Name, Company, and Score    (score is mat[x,y])
    for i in range(0,len(pos)):
        total += mat[pos[i][0], pos[i][1]]

        company = "company"
        if pos[i][1] < total_jobs:
            col_shift = len(number_of_jobs)
            for j in range(0,len(number_of_jobs)):
                if pos[i][1] < len(number_of_jobs):
                    company = number_of_jobs[pos[i][1]][0]
                elif pos[i][1] < col_shift:
                    company = number_of_jobs[j-1][0]
                    break
                else:

                    # each job listing is given an id 0,1,2...

                    #col_shift is because of the weird format of the matrix, where multiple
                    #postings of a job are stored at the end of the matrix, so we need to convert
                    #coordinates > number_of_jobs to an actual job listing id
                    col_shift = col_shift + (number_of_jobs[j][1]-1)

            # THIS SAVES ASSIGNMENT TO AN ARRAY AND PRINTS TO CONSOLE. What's printed and what's saved is identical
            save_to_csv.append([list_of_names[pos[i][0]][0], list_of_names[pos[i][0]][1], company, mat[pos[i][0], pos[i][1]]])
            print("Name: ", list_of_names[pos[i][0]][0], list_of_names[pos[i][0]][1] , "Job:", company, "Score:", mat[pos[i][0], pos[i][1]])

    return total


def maximize_assignment(mat):
    #to get max assignment, make a new matrix from subtracting prev matrix values from the max in the matrix
    #The min assignment of this new matrix will have equivalent positions to the max assignment of the original matrix
    max_value = np.max(mat)
    equiv_mat = max_value - mat
    return(equiv_mat)

def main(mat):

    '''Hungarian Algorithm: 
    If you're really curious about the nitty gritty of how this works, look up some videos on the Hungarian Algorithm
    
    '''

    # The Hungarian Algorithm is meant to MINIMIZE things (like cost). 
    # However we want to MAXIMIZE the score to make the smartest assignment
    new_matrix = maximize_assignment(mat)
    
    ans_pos = hungarian_algorithm(new_matrix.copy())#Get all the assignments

    total_points = save_final_assignment(mat, ans_pos)#Save final assignments in a human readable way, and save total score

    print("\nMaximized Points: ", total_points)

    #The final assignments, saved in an array, are transferred to a csv that will show up in the SAME FOLDER you put this script
    np.savetxt('results.csv', (save_to_csv), delimiter=',', fmt='%s')


#--------------------------------------------------------------

#Connects to mySQL database

'''
IMPORTANT: 

Some things will need to be changed ( see notice! )

Where you see studentinfo3 needs to be a table in mySQL containing ONLY scores. No names/other info

Where you see studentinfo2 needs to be a table where firstName and lastName are given the headers with that exact name,
or you can go below and change the ("SELECT firstName, lastName FROM studentinfo2") to whatever you named the header

'''

try:
    connection = mysql.connector.connect(host='#########',
                                         database='#########',
                                         user='#########',
                                         password='#########')  #NOTICE! THIS NEEDS TO BE CHANGED TO MATCH YOUR OWN DATABASE
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)

        cursor.execute("SELECT * FROM #########") #NOTICE! THIS NEEDS TO BE CHANGED TO WHATEVER YOU NAME TABLE
        result = cursor.fetchall()

        cursor.execute("SELECT firstName, lastName FROM #########") #NOTICE! THIS NEEDS TO BE CHANGED TO WHATEVER YOU NAME TABLE
        names = cursor.fetchall()


        # Save names in array we can use!
        for x in names:
            list_of_names.append(x)


        #turn scores/numbers into a numpy matrix we can use!
        mylist = []
        for x in result:
            mylist.append(x)

        mat = np.array(mylist)
        num_of_types = mat.shape[1]

        #making repeat columns to simulate multiple offerings from same job
        for x in range(0,num_of_types):
            for y in range(0,number_of_jobs[x][1]-1):
                mat = np.c_[ mat, mat[:,x] ]

        #add dummy zero columns at the end since more students than jobs
        current_cols = mat.shape[1]
        for x in range(current_cols, mat.shape[0]):
            mat = np.c_[ mat, np.zeros(mat.shape[0]) ]

        #np.set_printoptions(threshold=np.inf)


        main(mat) #RUN THE CODE!

except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")