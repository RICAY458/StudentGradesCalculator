import streamlit as st
import sqlite3
import pandas as pd

# --- CALCULATIONS LOGIC ---
def calculate_final_grade(row):
    # Attendance (15%) - Target: 40
    attn_weight = (min(row['attendance'], 40) / 40) * 15
    # Quiz (15%) - Target: 60
    quiz_weight = (min(row['quiz'], 60) / 60) * 15
    # Exam (50%) - Target: 60 
    exam_weight = (min(row['exam'], 60) / 60) * 50
    # Project (20%) - Target: 100
    proj_weight = (min(row['project'], 100) / 100) * 20
    
    final_grade = attn_weight + quiz_weight + exam_weight + proj_weight
    return round(final_grade, 2)

# --- DASHBOARD PAGE ---
def show_dashboard():
    col_title, col_user = st.columns([3, 1])
    with col_title:
        st.title(" Student Grades Calculator Dashboard")
    with col_user:
        st.write(f"Logged in: **{st.session_state.get('user_name', 'User')}**")
        if st.button("Log out"):
            st.session_state.page = 'login'
            st.rerun()

    tab1, tab2 = st.tabs([" Students List", " Add New Student"])

    with tab2:
        st.subheader("Register Student")
        with st.form("add_student_form"):
            s_sn = st.text_input("Surname")
            s_fn = st.text_input("First Name")
            s_cy = st.text_input("Course")
            s_sec = st.text_input("Section & Yr")
            s_sub = st.text_input("Subject")
            submitted = st.form_submit_button("Save Student")
            
            if submitted:
                if s_sn and s_fn:
                    conn = sqlite3.connect('users.db')
                    c = conn.cursor()
                    c.execute("""INSERT INTO students 
                              (surname, firstname, course_yr, section, subject, attendance, quiz, exam, project, grade) 
                              VALUES (?,?,?,?,?,0,0,0,0,0)""", (s_sn, s_fn, s_cy, s_sec, s_sub))
                    conn.commit()
                    conn.close()
                    st.success("Student saved to list!")
                    st.rerun()
                else:
                    st.error("Please provide at least a Surname and First Name.")

    with tab1:
        conn = sqlite3.connect('users.db')
        df = pd.read_sql_query("SELECT * FROM students", conn)
        conn.close()

        if not df.empty:
            # --- AUTO-CALCULATE REMARKS FOR DISPLAY ---
            df['REMARKS'] = df['grade'].apply(lambda x: " PASSED" if x >= 75 else " FAILED")

            st.write("Edit scores below and click **Save** to update Grades and Remarks:")
            
            # The Editable Table
            edited_df = st.data_editor(
                df, 
                num_rows="dynamic", 
                key="editor", 
                hide_index=True,
                column_config={
                    "id": None, # Hide the ID column from the user
                    "attendance": st.column_config.NumberColumn("Attendance (Max 40)"),
                    "quiz": st.column_config.NumberColumn("Quiz (Max 60)"),
                    "exam": st.column_config.NumberColumn("Exam (Max 60)"),
                    "project": st.column_config.NumberColumn("Project (Max 100)"),
                    "grade": st.column_config.NumberColumn("Final Grade", format="%.2f", disabled=True),
                    "REMARKS": st.column_config.TextColumn("REMARKS", disabled=True)
                },
                use_container_width=True
            )
            
            if st.button("Save & Update Grades", type="primary"):
                conn = sqlite3.connect('users.db')
                for _, row in edited_df.iterrows():
                    final_g = calculate_final_grade(row)
                    conn.execute("""UPDATE students SET 
                        surname=?, firstname=?, course_yr=?, section=?, subject=?, 
                        attendance=?, quiz=?, exam=?, project=?, grade=? WHERE id=?""",
                        (row['surname'], row['firstname'], row['course_yr'], row['section'], 
                         row['subject'], row['attendance'], row['quiz'], row['exam'], 
                         row['project'], final_g, row['id']))
                conn.commit()
                conn.close()
                st.success("Database updated successfully!")
                st.rerun()
        else:
            st.info("No student records found. Use the 'Add New Student' tab to begin.")

if __name__ == "__main__":
    show_dashboard()