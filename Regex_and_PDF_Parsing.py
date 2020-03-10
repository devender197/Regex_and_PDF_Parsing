# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 12:35:04 2020

@author: HOME
"""
import PyPDF2 as pdf
import re as reg
import os
import pandas as pd
import numpy as np

InstReg = reg.compile(r'(Instructor|INSTRUCTOR|PROFESSOR|Professor|Prof|Dr)[#\s\w]*[:.]?[#\s]*(([\w\.])*[\s]?(\w+)?)')
EmailReg  = reg.compile(r'([\w\.\+\_0-9]+)@(\w+).(\w+).(\w\w\w?)?\s?')
CourseReg = reg.compile(r'([A-Z]+)[#\s]?([0-9]+\w+?)')
SemReg    = reg.compile(r'(Winter|Fall|Summer|Spring|Autumn)\s?(\d\d\d\d)')
officeHourReg = reg.compile(r'[Oo]ffice\s*.+\s*[Hh]our[s]??')
PreReg = reg.compile(r'[P|p]rerequisite[s]?')
TimeDuration = reg.compile(r'(\d\d?:?\d?\d?\s*([a|A|p|P][m|M])?)\s*(.|\w\w)?\s*(\d\d?:?\d?\d?\s*([a|A|p|P][m|M]))')
PreCourseReg = reg.compile(r'([A-Z]+)\s?([0-9]+\w+?)')
WeekDayReg = reg.compile(r'Tue(sdays?)?|Mon(days?)?|Wed(nesdays?)?|Thu(rsdays?)?|Sat(urdays?)?|Fri(days?)?')
GradingReg = reg.compile(r'[A-Z][\w\s]*[\d\s:]+%')
GradingKWReg = reg.compile(r'Grading|Grade')
WebsiteReg = reg.compile(r'https?://(www/.)?[.a-z/]+')
PhoneReg = reg.compile(r'([P|p]hone|[C|c]ontact|Tel)[\s|A-Z|a-z|:]*([\d|-|\s|)|\-|\(|\.]*)\s')
FaxReg = reg.compile(r'([F|f]ax)[\s|A-Z|a-z|:]*([\d|-|)|\-|\(|\.]*)\s')

def searchPDF(fileName,df):
    pdfObj = open(fileName,'rb')
    pdfReader = pdf.PdfFileReader(pdfObj)
    pageNum = pdfReader.numPages
    page = 0
    isInstructorFound = False
    isInstructorEmail = False
    isCourseFound = False
    isSemFound = False
    isOfficeHourFound = False
    isOfficeDurFound = False
    isPreReqFound = False
    isWeekDayFound = False
    isGradeFound = False
    isWebsiteFound = False
    isPhoneNoFound  = False
    isFaxNoFound = False
    dur_min = 0
    dur_max = 0
    PreRequistes = []
    Grading = []
    Instructor_Name = ''
    Instructor_Email = ''
    Course_Name  = ''
    semester = ''
    weekday = ''
    duration = ''
    website = ''
    phoneNo = ''
    faxNo = ''
    ls = df.get('FileName')
    ls.append(fileName)
    df.update({'FileName':ls})
    #print(fileName)
    
    # iterating throught the loop
    while(page < pageNum):
        print('.')
        fileContent = pdfReader.getPage(page).extractText()
        if('\n' in fileContent):
            fileContent = fileContent.replace('\n',' ')
        Instr_min = 0
        Instr_max = 0
        dur_min = 0
        dur_max = 0
        matches_Instructor = InstReg.finditer(fileContent)
        for match in matches_Instructor:
            Instr_min,Instr_max = match.span()
            Instructor_Name = match.group(2)
            isInstructorFound = True
        
            
        phoneMatch = PhoneReg.search(fileContent)
        if(phoneMatch is not None and isPhoneNoFound == False and isInstructorFound == True):
            phoneNo = phoneMatch.group(2)
            isPhoneNoFound = True
        
        faxMatch = FaxReg.search(fileContent)
        if(faxMatch is not None and isFaxNoFound == False and isInstructorFound == True):
            faxNo = faxMatch.group(2)
            isFaxNoFound = True
        
        matches_email = EmailReg.finditer(fileContent)
        for match_email in matches_email:
            min,max = match_email.span()
            if(min > Instr_max and  isInstructorFound == True and isInstructorEmail == False):
                #print(f'Instructor email is {match_email.group(0)}')
                isInstructorEmail = True
                Instructor_Email = match_email.group(0)
        
        matches_course = CourseReg.finditer(fileContent)
        for match_course in matches_course:
            if(isCourseFound == False):
                #print(f'course is {match_course.group(0)}')
                isCourseFound = True
                Course_Name = match_course.group(0)
        
        matches_sem = SemReg.finditer(fileContent)
        for match_sem in matches_sem:
            if(isSemFound == False):
                #print(f'sem is {match_sem.group(0)} and year is {match_sem.group(2)}')
                isSemFound = True
                semester = match_sem.group(0)
                
        matches_off = officeHourReg.finditer(fileContent)
        for match_off in matches_off:
            if(isOfficeHourFound == False):
                dur_min,dur_max = match_off.span()
                #print(match_off)
                isOfficeHourFound = True
               
                
        matches_Duration = TimeDuration.finditer(fileContent)
        for match_Duration in matches_Duration:
            min,max = match_Duration.span()
            if(min > dur_max and  isOfficeHourFound == True and isOfficeDurFound == False):
                duration = match_Duration.group(0)
                #print(duration)
                isOfficeDurFound = True
                
        matches_week_reg = WeekDayReg.finditer(fileContent)
        for match_week_reg in matches_week_reg:
            min,max = match_week_reg.span()
            if(min > dur_max and  isOfficeHourFound == True and isWeekDayFound == False):
                #print(match_week_reg)
                weekday = match_week_reg.group(0)
                #print(weekday)
                isWeekDayFound = True
                
        
        matches_pre = PreReg.finditer(fileContent)
        for match_pre in matches_pre:
            if(isPreReqFound == False):
                pre_min,pre_max = match_pre.span()
                #print(match_pre)
                isPreReqFound = True
                
        
        matches_pre_course = PreCourseReg.finditer(fileContent)
        for match_pre_course in matches_pre_course:
            min,max = match_pre_course.span()
            if(isPreReqFound == True and min > pre_max):
                #print(f'course is {match_pre_course.group(0)}')
                PreRequistes.append(match_pre_course.group(0))
                
        grades_pre = GradingKWReg.finditer(fileContent)
        for match_grade in grades_pre:
            if(isGradeFound == False):
                grade_min,grade_max = match_grade.span()
                #print(match_grade)
                isGradeFound = True
                
        grades = GradingReg.finditer(fileContent)
        for grade in grades:
            min,max = grade.span()
            if(isGradeFound == True and min > grade_max):
                grade_min,grade_max = grade.span()
                #print(grade.group(0))
                Grading.append(grade.group(0))
        
        websiteMatch = WebsiteReg.search(fileContent)
        if(websiteMatch is not None and isWebsiteFound == False):
            website = websiteMatch.group(0)
            isWebsiteFound = True
            #print('------------')
            #print(website)
            
        websiteMatch = WebsiteReg.search(fileContent)
        if(websiteMatch is not None and isWebsiteFound == False):
            website = websiteMatch.group(0)
            isWebsiteFound = True
            #print('------------')
            #print(website)
            
        page+=1
        
    if(len(PreRequistes) > 0):
        ls = df.get('PreRequistes')
        ls.append(PreRequistes)
        df.update({'PreRequistes':ls})
    else:
        ls = df.get('PreRequistes')
        ls.append(np.nan)
        df.update({'PreRequistes':ls})
        
    if(Instructor_Name and isInstructorFound):
        ls = df.get('Instructor Name')
        ls.append(Instructor_Name)
        df.update({'Instructor Name':ls})
        Instructor_Name = ''
    else:
        ls = df.get('Instructor Name')
        ls.append(np.nan)
        df.update({'Instructor Name':ls})
        
    if(Instructor_Email and isInstructorEmail):
        ls = df.get('Instructor Email')
        ls.append(Instructor_Email)
        df.update({'Instructor Email':ls})
        Instructor_Email = ''
    else:
        ls = df.get('Instructor Email')
        ls.append(np.nan)
        df.update({'Instructor Email':ls})
        
    if(Course_Name and isCourseFound):
        ls = df.get('Course Name')
        ls.append(Course_Name)
        df.update({'Course Name':ls})
        Course_Name = ''
    else:
        ls = df.get('Course Name')
        ls.append(np.nan)
        df.update({'Course Name':ls})
        
    if(semester and isSemFound):
        ls = df.get('semester')
        ls.append(semester)
        df.update({'semester':ls})
    else:
        ls = df.get('semester')
        ls.append(np.nan)
        df.update({'semester':ls})
        
    if(weekday and duration and isOfficeHourFound == True and isWeekDayFound == True):
        ls = df.get('Office Hours')
        ls.append(f'{weekday} - {duration}')
        df.update({'Office Hours':ls})
    else:
        ls = df.get('Office Hours')
        ls.append(np.nan)
        df.update({'Office Hours':ls})
        
    if(isGradeFound and len(Grading)):
        ls = df.get('Grading')
        ls.append(Grading)
        df.update({'Grading':ls})
    else:
        ls = df.get('Grading')
        ls.append(np.nan)
        df.update({'Grading':ls})
    
    if(website and isWebsiteFound == True):
        ls = df.get('Website')
        ls.append(website)
        df.update({'Website':ls})
    else:
        ls = df.get('Website')
        ls.append(np.nan)
        df.update({'Website':ls})
     
    if(phoneNo and isPhoneNoFound == True):
        ls = df.get('Phone')
        ls.append(phoneNo)
        df.update({'Phone':ls})
    else:
        ls = df.get('Phone')
        ls.append(np.nan)
        df.update({'Phone':ls})
    
    if(faxNo and isFaxNoFound == True):
        ls = df.get('Fax')
        ls.append(faxNo)
        df.update({'Fax':ls})
    else:
        ls = df.get('Fax')
        ls.append(np.nan)
        df.update({'Fax':ls})
    
    #print('\n')
    return df

# reading files and extracting information
data = {'FileName' : [],'Instructor Name' : [],'Instructor Email': [],
                 'Course Name': [],'Office Hours': [],'PreRequistes': [],'semester': [],'Grading':[], 'Website':[], 'Phone':[], 'Fax':[]}
for file in os.listdir("syllabi"):
    if file.endswith(".pdf"):
        try:
           data = searchPDF(os.path.join("syllabi", file),data) 
        except :
            #print("*",file)
            continue
         
# creatign data frame and writing csv output file      
final_data = pd.DataFrame(data)
final_data.to_csv('features-retrieved-by-Devender Singh Parihar.csv', sep=',', encoding='utf-8')

        