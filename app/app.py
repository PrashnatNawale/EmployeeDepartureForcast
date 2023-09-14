# Import necessary libraries
import streamlit as st
import pandas as pd 
import numpy as np 
import joblib
import matplotlib.pyplot as plt

import mysql.connector

page=st.sidebar.selectbox("Select the Page",("Departure Prediction","Departure Visualization","Employee Information","Employee Details","Employee Profile","Organization Analysis"))

# Import model 
model=joblib.load("../Model/algo.pkl")
data=pd.read_csv("../Data/employeeInfo.csv")

# Selection for Filtering 
def select_option(data,column_name):
    column_option=pd.unique(data[column_name])
    show_options=st.sidebar.checkbox(f"{column_name}:")
    selected_department=column_option
    if show_options:
        selected_department=[]
        for dept in column_option:
            select_dept=st.sidebar.checkbox(str(dept))
            if select_dept:
                selected_department.append(dept)
    return selected_department

# Filtering 
def filter_data(data,visualization_columns,select):
    for column in visualization_columns:
        data=data[data[column].isin(select[column])]
    return data

# Data visualizations 
def GroupBar_visualization(data,column_name):
    st.markdown("#### Group Bar Representation")
    # st.write(f"Following bar plot show how Decision of departure from organization of employee varies accoring to diffrent {column_name}")
    data_count=data.groupby([column_name,'left']).size().unstack()
    if(len(data_count)==0):
        data_count=pd.DataFrame({},columns=[column_name,0,1])
    fig,ax=plt.subplots(figsize=(8,4))
    n=range(len(data_count))
    width=0.3
    ax.bar(n,data_count[0],width=width,label='left')
    ax.bar([i+width for i in n],data_count[1],width=width,label='Non-left')
    ax.set_xlabel(column_name)
    ax.set_ylabel("Number of employees")
    ax.set_title("Departure of Employee Accoring to Department")
    ax.set_xticks([i+width/2 for i in n])
    ax.set_xticklabels(data_count.index,rotation=90)
    st.pyplot(fig)

# Function to establish a MySQL connection
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='PRASHANT70nawale38@',
            database='employeeDeparture'
        )
        if connection.is_connected():
            return connection
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# Modify database of employee
def update_dataset(data):
    edited_data = data.copy()
    columns=["Emails","Salary","Projects","Promotion"]
    
    col=list(st.columns(4))
    for i,j in zip(columns,col):
        j.markdown(f"**{i}**")
   
    for index, row in edited_data.iterrows():
        col1, col2, col3,col4 = st.columns(4)
        col1.markdown(f"**{row['emails']}**")
        edited_value1 = col2.text_input(label="", key=f"Salary {row['emails']}", value=row["Salary"])
        edited_value2 = col3.text_input(label="", key=f"Promotion {row['emails']}", value=row["Promotion"])
        edited_value3 = col4.text_input(label="", key=f"Projects {row['emails']}", value=row["Projects"])
        data.loc[index, "Salary"] = edited_value1
        data.loc[index, "Promotion"] = edited_value2
        data.loc[index, "Projects"] = edited_value3
    if st.button("submit"):
        return data 

if page=="Departure Prediction":
    # Heading 
    st.title("Departure Prediction of Employee")
    st.sidebar.header("User Input")
    # Accepting Data from HR for prediction
    satisfaction_level = st.sidebar.slider("Satisfaction Level (0.0 - 1.0):", 0.0, 1.0, 0.5)
    monthly_hours = st.sidebar.slider("Monthly Working Hours (min: 0, max: 310):", 50, 310, 160)
    daily_hours = st.sidebar.slider("Daily Working Hours (min: 2, max: 10):", 2, 10, 8)
    num_projects = st.sidebar.slider("Number of Projects (min: 2, max: 7):", 2, 7, 4)
    salary = st.sidebar.radio("Salary Level:", ("Low", "Medium", "High"))
    work_accident = st.sidebar.radio("Work Accident (Yes/No):", ("Yes", "No"))
    promotion_last_5_years = st.sidebar.radio("Promotion in Last 5 Years (Yes/No):", ("Yes", "No"))

    # Define a dictionary to map yes/no options to binary values
    binary_mapping = {"Yes": 1, "No": 0}

    # Create a button to perform analysis or predictions
    if st.sidebar.button("Predict"):
        # Data preprocessing and formation of dataframe 
        has_work_accident = binary_mapping[work_accident]
        has_promotion = binary_mapping[promotion_last_5_years]
        monthly_hours=monthly_hours/(31*10)
        daily_hours=daily_hours/10
        datalist=[satisfaction_level,num_projects,monthly_hours,daily_hours,has_work_accident,has_promotion,int(salary=='High'),int(salary=='Low'),int(salary=='Medium')]
        columnlist=['satisfaction_level', 'number_project', 'average_montly_hours',
           'time_spend_company', 'Work_accident', 'promotion_last_5years','salary_high','salary_low','salary_medium']
        test_data=pd.DataFrame({columnlist[i]:[datalist[i]] for i in range(len(columnlist))})
    
        # Example logic (replace with your model prediction)
        prediction_result = model.predict(test_data)  # Replace with your prediction logic
        decision_attribute=model.decision_path(test_data)
        # Display the result
        st.subheader("Prediction Result:")
        if prediction_result[0]:
            st.markdown(f"### Employee will Left the job.")
        else :
            st.markdown("### Employee will continue that job.")

elif page=="Departure Visualization":
    st.markdown("## Visualization")

    visualization_columns=["Department", "number_project", "time_spend_company","promotion_last_5years","salary"]
    # Selecting Department 
    column=st.sidebar.radio("Select Department:", tuple(visualization_columns))
   
    select=dict()
    st.sidebar.markdown("#### Filters")
    for column_name in visualization_columns:
        select[column_name]=select_option(data,column_name)
    dataset=filter_data(data,visualization_columns,select)
    GroupBar_visualization(dataset,column)

elif page=="Employee Information":
    options = ["Employee List", "Add Employee", "Update Details", "Remove Employee"]
    # Allow the user to select an option from the sidebar
    selected_option = st.sidebar.radio("Select an Option", options)
    
    connection=create_connection()
    cursor = connection.cursor()

    st.write(selected_option)

    if selected_option=="Employee List":
        cursor.execute("select * from employee")
        data=cursor.fetchall()
        df = pd.DataFrame(data, columns=["Email", "Name", "Phone", "Year", "Department"])
        # Display the DataFrame as a table
        st.dataframe(df, height=300)

    elif selected_option=="Add Employee":

        email = st.text_input("Email:")
        name = st.text_input("Name:")
        phone = st.text_input("Phone:")
        year = st.number_input("Year:", min_value=1900, max_value=2100)
        department_options = ['sales', 'accounting', 'hr', 'technical', 'support', 'management','IT', 'product_mng', 'marketing', 'RandD']
        department =st.selectbox("Department:", department_options)
        
        # Button to submit data
        if st.button("Submit"):
            sql = "INSERT INTO employee (email,empname,contact,joining, department) VALUES (%s, %s, %s, %s, %s)"
            values = (email, name, phone, year, department)
            cursor.execute(sql, values)
            connection.commit()
            st.write("Data inserted into the employee table.")

    elif selected_option=="Update Details":
        email = st.text_input("Employee Email:")
        phone = st.text_input("Updated Phone:")
        department_options = ['sales', 'accounting', 'hr', 'technical', 'support', 'management','IT', 'product_mng', 'marketing', 'RandD']
        department =st.selectbox("Updated Department:", department_options)
        if st.button("Update"):
            sql=f"UPDATE employee SET department='{department}', contact='{phone}' WHERE email='{email}'"
            cursor.execute(sql)
            connection.commit()
            st.write("Data might saved")

    elif selected_option=="Remove Employee":
        st.subheader("Removing Employee from organization")
        email = st.text_input("Employee Email:")
        if st.button("Delete"):
            sql=f"DELETE FROM employee WHERE email='{email}'"
            cursor.execute(sql)
            connection.commit()
            st.write("Employee Removed form database")

    

        # Perform SQL queries and display results using Streamlit
        # Example: cursor.execute("SELECT * FROM your_table")
        #         data = cursor.fetchall()
        #         st.write(data)

        # Close the cursor and connection when done
    cursor.close()
    connection.close()

elif page=="Employee Details":
    connection=create_connection()
    cursor = connection.cursor()
    options = ["Submit yearly Progress", "Update Employee Progress"]
    # Allow the user to select an option from the sidebar
    selected_option = st.sidebar.radio("Select an Option", options)

    if selected_option=="Submit yearly Progress":
        
        st.header(f"Upadation of the Employee Details")
        year=st.sidebar.number_input("Select the year:", min_value=1900, max_value=2100)
        cursor.execute(f"SELECT email FROM employee WHERE joining<={year}")
        existing_emails = [row[0] for row in cursor.fetchall()]
        emails_number=len(existing_emails)
        data = pd.DataFrame({
            "emails":existing_emails,
            "Salary": np.zeros(emails_number),
            "Promotion": np.zeros(emails_number),
            "Projects":np.zeros(emails_number)
            })

        history={}
        for mail in existing_emails:
            cursor.execute(f"SELECT email,salary,promotion,projects from employeeDetails where email='{mail}' and year={year}")
            values=cursor.fetchall()
            if len(values)>0:
                history[mail]=(values[0][1],values[0][2],values[0][3])


        for index, row in data.iterrows():
            email = row['emails']
            if email in history:
                salary,projects,promotion  = history[email]
                data.at[index, 'Salary'] = salary
                data.at[index, 'Promotion'] = promotion
                data.at[index, 'Projects'] = projects
        data=update_dataset(data)

        try:
            for i in range(len(data['emails'])):
                sql = f"INSERT INTO employeeDetails (email,year,salary,projects,promotion) VALUES ('{data.iloc[i,0]}',{year},{data.iloc[i,1]},{data.iloc[i,2]},{data.iloc[i,3]}) ON DUPLICATE KEY UPDATE salary ={data.iloc[i,1]},promotion ={data.iloc[i,3]}, projects ={data.iloc[i,2]}"
                cursor.execute(sql)            
            connection.commit()

            st.write("Data updated")

        except:
            st.write("Not updated")
    elif selected_option=="Update Employee Progress":
        
        email=st.sidebar.text_input("Enter the Email:")

        sql=f"Select * from employee where email='{email}'"

        
        cursor.execute(sql)
        data=cursor.fetchall()
        
        if(len(data)==0):
            st.subheader("Profile Does not found")
        else:
            st.subheader("Profile Found")
            st.write("Name        :",data[0][1])
            st.write("Contact     :",data[0][2])
            st.write("Joining     :",data[0][3])
            st.write("Department  :",data[0][4])

            sql=f"SELECT * FROM employeeDetails where email='{email}'"

            cursor.execute(sql)

            data=cursor.fetchall()
            year=[]
            salary=[]
            promotion=[]
            projects=[]
            for i in range(len(data)):
                year.append(data[i][1])
                salary.append(data[i][2])
                projects.append(data[i][3])
                promotion.append(data[i][4])


            data=pd.DataFrame({
                "Year":year,
                "Salary":salary,
                "Projects":projects,
                "Promotion":promotion
                })
            st.dataframe(data)

            st.markdown("**UPDATE DATA**")

            attribute=st.selectbox("Select attribute:",["salary","projects","promotion"])
            
            year=st.number_input("Select the year:", min_value=1900, max_value=2100)

            value=st.number_input("Enter the value:")

            if st.button("Apply Changes"):
                sql=f"update employeeDetails set {attribute}={value} where email='{email}' and year={year}"
                cursor.execute(sql)
                connection.commit()
                st.experimental_rerun()
    cursor.close()
    connection.close()

elif page=="Employee Profile":
    
    connection=create_connection()
    cursor=connection.cursor()
    email=st.sidebar.text_input("Enter the Email:")

    sql=f"Select * from employee where email='{email}'"

        
    cursor.execute(sql)
    data=cursor.fetchall()
        
    if(len(data)==0):
        st.subheader("Profile Does not found")
    else:
        st.subheader("Profile Found")
        st.write("Name        :",data[0][1])
        st.write("Contact     :",data[0][2])
        st.write("Joining     :",data[0][3])
        st.write("Department  :",data[0][4])

        sql=f"SELECT * FROM employeeDetails where email='{email}'"

        cursor.execute(sql)
        data=cursor.fetchall()
            
        year=[]
        salary=[]
        promotion=[]
        projects=[]
        for i in range(len(data)):
            year.append(data[i][1])
            salary.append(data[i][2])
            projects.append(data[i][3])
            promotion.append(data[i][4])


        data=pd.DataFrame({
            "Year":year,
            "Salary":salary,
            "Projects":projects,
            "Promotion":promotion
            })

        # Project of employee
        st.markdown("**Projects:**")
        fig, ax = plt.subplots(figsize=(10,4))
        ax.bar(data['Year'], data['Projects'],width=0.5)
        ax.set_xlabel('Year')
        ax.set_ylabel('Projects')
        ax.set_title('Projects Over the Years')
        st.pyplot(fig)

        

        # Salary of employee
        st.markdown("**Salary**")
        fig, ax = plt.subplots(figsize=(10,4))
        ax.bar(data['Year'], data['Salary'],width=0.5)
        ax.set_xlabel('Year')
        ax.set_ylabel('Salary')
        ax.set_title('Salary Over the Years')
        st.pyplot(fig)

        # Promotions Representation 
        st.markdown("**Promotions:**")
        fig, ax = plt.subplots(figsize=(10,4))
        ax.bar(data['Year'], data['Promotion'],width=0.5)
        ax.set_xlabel('Year')
        ax.set_ylabel('Promotions')
        ax.set_title('Promotions Over the Years')
        st.pyplot(fig)

    cursor.close()
    connection.close()

elif page=="Organization Analysis":
    connection=create_connection()
    cursor=connection.cursor()

    year=st.sidebar.number_input("Select the year:", min_value=1900, max_value=2100)
    
    st.header("Organization Report")

    # st.subheader(f"Year:{year}")

    
    st.subheader("Employees:")
    sql=f"SELECT  * FROM employee WHERE joining<={year}"
    cursor.execute(sql)
    data=cursor.fetchall()
    for i in range(len(data)):
        st.write(f"Employee {i+1}:",data[i][1])
    
    sql2=f"SELECT sum(Salary),sum(Projects),sum(Promotion) FROM employeeDetails WHERE year={year}"
    cursor.execute(sql2)
    data1=cursor.fetchall()

    st.subheader("Salary Expandature:")
    st.write(f"Total Salary of {year}:",data1[0][0])

    st.subheader("Projects:")
    st.write(f"Completed Projects of {year}:",data1[0][1])

    st.subheader("Promotions")
    st.write(f"Promotion of {year} :",data1[0][2])

    # st.write(data1)


    cursor.close()
    connection.close()
    

        





