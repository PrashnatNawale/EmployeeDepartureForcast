# Import necessary libraries
import streamlit as st
import pandas as pd 
import joblib
import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

page=st.sidebar.selectbox("Select the Page",("Departure Prediction","Departure Visualization"))



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