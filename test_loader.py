from matcher import load_student_data, load_universities_database, match
#--- load user profile from json
student_data = load_student_data()

#--- load universities data from json
universities_data, universities_names = load_universities_database()