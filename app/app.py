import logging
logging.basicConfig(level=logging.DEBUG)

import streamlit as st
import os
import sys
from mysql.connector import Error
import pandas as pd

st.title("Student Placement Eligibility Dashboard")
st.subheader("Filter Students based on Placement Readiness")
logging.debug("Streamlit app started")


#Add database folder to the path so we can import db_manager
try:
    
    app_dir=os.path.dirname(os.path.abspath(__file__))
    db_dir=os.path.abspath(os.path.join(app_dir,"..","database"))
    if db_dir not in sys.path:
        sys.path.append(db_dir)
    logging.debug(f"Database directory added to path: {db_dir}")

except Error as e:
    st.error("Failed to add database folder to path.")
    logging.exception("Error setting import path:")
    st.stop()

# Import DatabaseManager
try:
    from db_manager import DatabaseManager
    logging.debug("Imported DatabaseManager successfully")
except Exception as e:
    st.error("Failed to import DatabaseManager.")
    logging.exception("Error importing:")
    st.stop()


#Connect to the database
try:
    
    db = DatabaseManager(
        host='localhost',
        user='root',
        password='Shubhi@28',
        database='placement_project'
        )

    #Toggle to show all the students without any filters
    show_all = st.sidebar.checkbox("Show all the students", value= False)

    
    #Streamlit Filter Widgets
    st.sidebar.header("Placement Eligibility Filters")

    min_programming_score=st.sidebar.slider(
        "Minimum Programming Score(Latest Project)", min_value=50, max_value=100, value=60
    )

    min_soft_skill_score=st.sidebar.slider(
        "Minimum Average Soft Skill Score", min_value=0, max_value=100, value=60
    )

    placement_status=st.sidebar.selectbox(
        "Placement Status", options=['All','Ready','Not Ready','Placed']
    )

    min_mock_score=st.sidebar.slider(
        "Minimum Mock Interview Score",min_value=0, max_value=100, value=60
    )

    minimum_internships=st.sidebar.slider(
        "Minimum Internships Completed",min_value=0, max_value=3, value=1
    )

    sort_by = st.sidebar.selectbox(
        "Sort Students By",
        options=["Programming Score", "Soft Skill Score", "Mock Interview Score", "Internships Completed"]
    )

    sort_order = st.sidebar.radio(
        "Sort Order",
        options=["Descending","Ascending"],
        horizontal=True
    )
    
    #----------FILTERED DATA QUERY-------------

    #SQL Query with joins and filters applied

    if show_all:
        #If checkbox is ticked, show all students without any filters
        query=f"""
        SELECT 
           s.student_id, s.full_name, s.email, s.phone, s.gender, s.city, s.state, s.enrollment_year, s.course_batch, s.graduation_year, 
           p.latest_project_score,
           ROUND((ss.communication+ss.teamwork+ss.presentation+ss.leadership+ss.critical_thinking+ss.interpersonal_skills)/6, 2) as avg_soft_skills,
           pl.mock_interview_score,
           pl.internships_completed,
           pl.placement_status
        FROM Students AS s
        JOIN Programming AS p ON s.student_id = p.student_id
        JOIN Soft_skills AS ss ON s.student_id = ss.student_id
        JOIN Placements AS pl ON s.student_id = pl.student_id
        """

    else:
        query=f"""
    SELECT s.student_id, s.full_name, s.email, s.phone, s.gender, s.city, s.state, s.enrollment_year, s.course_batch, s.graduation_year,
           p.latest_project_score,
           ROUND((ss.communication+ss.teamwork+ss.presentation+ss.leadership+ss.critical_thinking+ss.interpersonal_skills)/6, 2) as avg_soft_skills,
           pl.mock_interview_score,
           pl.internships_completed,
           pl.placement_status
    FROM Students AS s
    JOIN Programming AS p ON s.student_id = p.student_id
    JOIN Soft_skills AS ss ON s.student_id = ss.student_id
    JOIN Placements AS pl ON s.student_id = pl.student_id
    WHERE p.latest_project_score>={min_programming_score}
        AND ((ss.communication+ss.teamwork+ss.presentation+ss.leadership+ss.critical_thinking+ss.interpersonal_skills)/6) >= {min_soft_skill_score}
        AND pl.mock_interview_score>={min_mock_score}
        AND pl.internships_completed>={minimum_internships}
    """

    #Apply Placement status filter only if user did not select ALL
        if placement_status.lower() != 'all':
            query+=f" AND pl.placement_status = '{placement_status}'"
    

    #Fetching Filtered Data
    with st.spinner("Fetching Eligible Students"):
        filtered_students = db.fetch_query(query)

    #Displaying the results
    st.subheader("🎓 Eligible Students")
    if filtered_students:
        #Convert result to DataFrame
        columns=["ID","Name", "Email", "Phone", "Gender", "City", "State", "Enrollment Year", "Course Batch", "Graduation Year", "Programming Score", 
                 "Soft Skill Average", "Mock Score", "Internships", "Status"]
        df=pd.DataFrame(filtered_students, columns=columns)

        #Summary Metrics
        total_students = len(df)
        avg_programming = round(df["Programming Score"].mean(), 2)
        avg_soft_skills = round(df["Soft Skill Average"].mean(), 2)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total students", total_students)
        col2.metric("Average Programming Score", avg_programming)
        col3.metric("Average Soft Skill Score", avg_soft_skills)

        sort_column_map = {
            "Programming Score": "Programming Score",
            "Soft Skill Score": "Soft Skill Average",
            "Mock Interview Score": "Mock Score",
            "Internships Completed": "Internships"
        }

        sort_column=sort_column_map[sort_by]
        ascending_order = sort_order == "Ascending"
        df = df.sort_values(by=sort_column, ascending=ascending_order)


        st.dataframe(df, use_container_width=True, height=400)


        for index, row in df.iterrows():
            with st.expander(f"### View Details for {row['Name']}"):
                print("Fetching details for student ID:", row["ID"])

                student_details = db.get_student_details(row["ID"])

                
                st.markdown("### Student Information")
                st.write(f"Phone : {row['Phone']}")
                st.write(f"Gender : {row['Gender']}")
                st.write(f"Enrollment Year : {row['Enrollment Year']}")
                st.write(f"Course Batch : {row['Course Batch']}")
                st.write(f"Graduation Year : {row['Graduation Year']}")
                st.write(f"City : {row['City']}")
                st.write(f"State : {row['State']}")

                st.markdown("---")
                
                #Fetch Additional details from the database
                if student_details:
                    details=student_details[0]
                    print("Length of details:", len(details))

                    #Two columns for Programming and Soft Skills
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("Programming Skills")
                        st.write(f"Language : {details[0]}")
                        st.write(f"Problems Solved : {details[1]}")
                        st.write(f"Assessments Completed : {details[2]}")
                        st.write(f"Mini Projects : {details[3]}")
                        st.write(f"Certifications Earned : {details[4]}")
                        st.write(f"Latest Project Score : {details[5]}")

                    with col2:
                    
                        st.subheader("Soft Skills")
                        st.write(f"Communication : {details[6]}")
                        st.write(f"Teamwork : {details[7]}")
                        st.write(f"Presentation : {details[8]}")
                        st.write(f"Leadership : {details[9]}")
                        st.write(f"Critical Thinking : {details[10]}")
                        st.write(f"Interpersonal Skills : {details[11]}")

                    #Placement details below
                    st.markdown("---")
                    st.markdown("### Placement Details")
                    st.write(f"Mock Interview Score : {details[12]}")
                    st.write(f"Internships Completed : {details[13]}")
                    st.write(f"Placement Status : {details[14]}")

                    #Show Placement info only if placed
                    if details[14] and details[14].lower()=='placed':
                        st.write(f"Company Name : {details[15]}")
                        st.write(f"Placement Package : {details[16]}")
                        st.write(f"Interview Rounds Cleared : {details[17]}")
                        st.write(f"Placement Date : {details[18]}")
                    else: 
                        st.write("This student has not yet been placed")


    else: 
        st.info("No students found matching the criteria")


    #Optional toggle to show raw filtered data
    #if st.checkbox("Show Raw Filtered Data"):
        #st.dataframe(df)

    #SQL Insights Section
    st.markdown("### Insight From Student Data")

    #Dropdown to select insight
    insight_option = st.selectbox(
        "Select an Insight to display",
        options=[
            "Average Programming Score per Course Batch",
            "Top 5 students ready for Placement based on Mock Interview Score",
            "Distribution of Average Soft Skill Score",
            "Number of Students that are Placed/Ready/Not Ready",
            "Top 5 cities with Highest Number of Students",
            "Average Mock Interview Score by Graduation Year",
            "Most Commonly used Programming Language among Students",
            "Placed Students with more than two Internships",
            "Students clearing more than 3 Interview Rounds",
            "Students with more than 2 Programming Certificates",
        ]
    )

    #Mapping insights to SQL queries and display columns
    insight_queries={
         "Average Programming Score per Course Batch":{
             "query":"""
             SELECT course_batch, ROUND(AVG(P.latest_project_score),2)
             FROM Students AS S
             JOIN Programming AS P ON S.student_id = P.student_id
             GROUP BY course_batch;
             """,
             "columns":["Course Batch","Average Programming Score"]
         },
        "Top 5 students ready for Placement based on Mock Interview Score":{
             "query":"""
             SELECT s.full_name, pl.mock_interview_score, pl.placement_status
             FROM Students AS s
             JOIN Placements AS pl ON s.student_id = pl.student_id
             WHERE pl.placement_status = 'Ready'
             ORDER BY pl.mock_interview_score DESC
             LIMIT 5
             """,
             "columns":["Student Name","Mock Interview Score","Placement Status"]
         },
        "Distribution of Average Soft Skill Score":{
             "query":"""
         SELECT 
             CASE
                WHEN avg_score>=85 THEN 'Excellent'
                WHEN avg_score>=70  THEN 'Good'
                WHEN avg_score>=50 THEN 'Average'
                ELSE 'Needs Improvement'
             END AS category,
             COUNT(*) AS student_count
         FROM (
            SELECT
                (communication + teamwork + presentation + leadership + critical_thinking + interpersonal_skills) / 6 AS avg_score
            FROM Soft_skills
            ) AS derived
         GROUP BY category;
             """,
             "columns":["Category","Student Count"]
         },
        "Number of Students that are Placed/Ready/Not Ready":{
             "query":"""
             SELECT
             placement_status, 
             COUNT(*)
             FROM Placements
             GROUP BY placement_status;

             """,
             "columns":["Placement Status","Student Count"]
         },
        "Top 5 cities with Highest Number of Students":{
             "query":"""
             SELECT city, COUNT(*) AS student_count
             FROM students
             GROUP BY city
             ORDER BY student_count DESC
             LIMIT 5
             """,
             "columns":["City","Student Count"]
        },
        "Average Mock Interview Score by Graduation Year":{
             "query":"""
             SELECT s.graduation_year, ROUND(AVG(pl.mock_interview_score),2)
             FROM Students AS s
             JOIN Placements AS pl ON s.student_id=pl.student_id
             GROUP BY s.graduation_year
             ORDER BY s.graduation_year
             """,
             "columns":["Graduation Year", "Average Mock Interview Score"]
        },
        "Most Commonly used Programming Language among Students":{
             "query":"""
             SELECT language, COUNT(*) AS student_count
             FROM Programming
             GROUP BY language
             ORDER BY student_count DESC;
             """,
             "columns":["Language", "Student Count"]
        },
        "Placed Students with more than two Internships":{
             "query":"""
             SELECT s.full_name, pl.internships_completed, pl.placement_status
             FROM Students AS s
             JOIN Placements AS pl ON s.student_id = pl.student_id
             WHERE pl.internships_completed>=2 and pl.placement_status='Placed';
             """,
             "columns":["Student Name", "Internship Completed", "Placement Status"]
        },
        "Students clearing more than 3 Interview Rounds":{
             "query":"""
             SELECT s.full_name, pl.interview_rounds_cleared
             FROM Students AS s
             JOIN Placements AS pl ON s.student_id = pl.student_id
             WHERE pl.interview_rounds_cleared>=3
             ORDER BY pl.interview_rounds_cleared DESC;
             """,
             "columns":["Student Name", "Interview Rounds Cleared"]
        },
        "Students with more than 2 Programming Certificates":{
             "query":"""
             SELECT s.full_name, p.certifications_earned
             FROM Students AS s
             JOIN Programming AS p ON s.student_id = p.student_id
             WHERE p.certifications_earned>=2
             ORDER BY p.certifications_earned DESC;
             """,
             "columns":["Student Name", "Certifications Earned"]
        }
    }
    #Run the selected query
    selected = insight_queries[insight_option]
    
    try:
        with st.spinner("Loading Insight Data"):
            result=db.fetch_query(selected["query"])

            if result:
                df1=pd.DataFrame(result, columns=selected["columns"])
                st.dataframe(df1, use_container_width=True)

            else:
                st.info("No data found for this insight")

    except Exception as e:
        st.error("Error while fetching this insight")
        st.exception(e)

    db.disconnect()

except Exception as e:
    st.error(f"An error occured : {e}")
    st.stop() #stop the execution


