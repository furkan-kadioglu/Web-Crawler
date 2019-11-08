
# coding: utf-8

# In[1]:


import pandas as pd 
import numpy as np 
import sys 


# In[2]:


#makes course code without sections 
def de_section(x):
    return x[:-3]


# # Url

# In[3]:


#makes url by using short name, term, department name
def make_url(term,short,long):
    init = 'https://registration.boun.edu.tr/scripts/sch.asp?donem='
    init2 = '&kisaadi='
    init3 = '&bolum='
    return init + year_format(term) + init2 + short + init3 + make_long(long)


# ## Short & Long Name 

# In[4]:


short =['ASIA','ASIA','ATA','AUTO','BM','BIS','CHE',
        'CHEM','CE','COGS','CSE','CET','CMPE','INT',
        'CEM','CCS','EQE','EC','EF','ED','CET','EE',
        'ETM','ENV','ENVT','XMBE','FE','PA','FLED',
        'GED','GPH','GUID','HIST','HUM','IE','INCT',
        'MIR','MIR','INTT','INTT','LS','LING','AD',
        'MIS','MATH','SCED','ME','MECA','BIO','PHIL',
        'PE','PHYS','POLS','PRED','PSY','YADYOK','SCED',
        'SPL','SOC','SWE','SWE','TRM','SCO','TRM','WTR',
        'TR','TK','TKL','LL']


# In[5]:


long = ['ASIAN STUDIES','ASIAN STUDIES WITH THESIS',
        'ATATURK INSTITUTE FOR MODERN TURKISH HISTORY',
        'AUTOMOTIVE ENGINEERING','BIOMEDICAL ENGINEERING',
        'BUSINESS INFORMATION SYSTEMS','CHEMICAL ENGINEERING',
        'CHEMISTRY','CIVIL ENGINEERING','COGNITIVE SCIENCE',
        'COMPUTATIONAL SCIENCE & ENGINEERING',
        'COMPUTER EDUCATION & EDUCATIONAL TECHNOLOGY',
        'COMPUTER ENGINEERING','CONFERENCE INTERPRETING',
        'CONSTRUCTION ENGINEERING AND MANAGEMENT',
        'CRITICAL AND CULTURAL STUDIES','EARTHQUAKE ENGINEERING',
        'ECONOMICS','ECONOMICS AND FINANCE','EDUCATIONAL SCIENCES',
        'EDUCATIONAL TECHNOLOGY','ELECTRICAL & ELECTRONICS ENGINEERING',
        'ENGINEERING AND TECHNOLOGY MANAGEMENT','ENVIRONMENTAL SCIENCES',
        'ENVIRONMENTAL TECHNOLOGY','EXECUTIVE MBA',
        'FINANCIAL ENGINEERING','FINE ARTS','FOREIGN LANGUAGE EDUCATION',
        'GEODESY','GEOPHYSICS','GUIDANCE & PSYCHOLOGICAL COUNSELING',
        'HISTORY','HUMANITIES COURSES COORDINATOR',
        'INDUSTRIAL ENGINEERING','INTERNATIONAL COMPETITION AND TRADE',
        'INTERNATIONAL RELATIONS:TURKEY;EUROPE AND THE MIDDLE EAST',
        'INTERNATIONAL RELATIONS:TURKEY;EUROPE AND THE MIDDLE EAST WITH THESIS',
        'INTERNATIONAL TRADE','INTERNATIONAL TRADE MANAGEMENT',
        'LEARNING SCIENCES','LINGUISTICS','MANAGEMENT',
        'MANAGEMENT INFORMATION SYSTEMS','MATHEMATICS',
        'MATHEMATICS AND SCIENCE EDUCATION','MECHANICAL ENGINEERING',
        'MECHATRONICS ENGINEERING','MOLECULAR BIOLOGY & GENETICS',
        'PHILOSOPHY','PHYSICAL EDUCATION','PHYSICS',
        'POLITICAL SCIENCE&INTERNATIONAL RELATIONS',
        'PRIMARY EDUCATION','PSYCHOLOGY','SCHOOL OF FOREIGN LANGUAGES',
        'SECONDARY SCHOOL SCIENCE AND MATHEMATICS EDUCATION',
        'SOCIAL POLICY WITH THESIS','SOCIOLOGY','SOFTWARE ENGINEERING',
        'SOFTWARE ENGINEERING WITH THESIS','SUSTAINABLE TOURISM MANAGEMENT',
        'SYSTEMS & CONTROL ENGINEERING','TOURISM ADMINISTRATION',
        'TRANSLATION','TRANSLATION AND INTERPRETING STUDIES',
        'TURKISH COURSES COORDINATOR','TURKISH LANGUAGE & LITERATURE',
        'WESTERN LANGUAGES & LITERATURES']


# ### Sorting Departments' Abbreviation 

# In[6]:


short_long_df = pd.DataFrame([long,short])
short_long_df.sort_values(1,axis=1,inplace=True)
long = np.array(short_long_df.T[0])
short = np.array(short_long_df.T[1])


# In[7]:


#transforms department names to proper long format for url 
def make_long(x):
    x = x.replace('&','%26')
    x = x.replace(':','%3a')
    x = x.replace(',','%2c')
    x = x.replace(' ','+')
    return x


# ## Year

# In[8]:


# encodes input terms to integer
def year_encoder(x):
    year = (int(x[:4])-1000)*3
    season = x[5:]
    if season == 'Fall':
        return year + 2
    if season == 'Spring':
        return year 
    if season == 'Summer':
        return year + 1
    
#decodes term & generates links 
def year_format(x):
    term = int(((x+1) % 3) + 1)
    year = int(((x-2) / 3) + 1000)
    return str(year) + '/' + str(year+1) + '-' + str(term)

#decodes term to original form
def year_original(x):
    term = int(((x+1) % 3) + 1)
    year = int(((x-2) / 3) + 1000)
    if(term == 1):
        return str(year) + '-' + 'Fall'
    if(term == 2):
        return str(year + 1) + '-' + 'Spring'
    if(term == 3):
        return str(year + 1) + '-' + 'Summer' 


# # Input

# In[9]:


#start_term = sys.argv[1]
#end_term = sys.argv[2]
start_term = '2017-Fall' 
end_term = '2018-Spring'
start_date = year_encoder(start_term)
end_date = year_encoder(end_term)


# # Crawling
# Crawles http://registration.boun.edu.tr/ and deducts dataframes

# In[10]:


mask = ['Code.Sec',
        'Name',
        'Instr.']
info = pd.DataFrame(columns=['Term',
                             'Short',
                             'Long',
                             'Name',
                             'Code.Sec',
                             'Instr.'])
for term in np.arange(start_date,end_date+1):
    for i in range(len(short)):
        url = make_url(term,
                       short[i],
                       long[i])
        try:
            temp_df = pd.read_html(url)
            temp_df = temp_df[3]
            t = temp_df
            t.rename(columns=t.loc[0],
                     inplace=True)
            t.drop(index=0,
                   inplace=True)
            t = t[mask]
            t = t.dropna()
            t.reset_index(inplace=True)
            new = pd.DataFrame(columns=['Term',
                                        'Short',
                                        'Long'])
            new = new.reindex(index=np.arange(len(t)))
            new[['Term',
                 'Short',
                 'Long']] = [term,
                             short[i],
                             long[i]]
            new[['Name',
                 'Code.Sec',
                 'Instr.']] = t[['Name',
                                 'Code.Sec',
                                 'Instr.']]
            info = pd.concat([new,
                              info])
        except:
            pass
info.reset_index(inplace=True)
info.drop(columns='index',
          inplace=True)
info['Code.Sec'] = (info['Code.Sec']
                    .apply(lambda x:de_section(x)))


# # Information Retrieval From Each Department

# In[11]:


final = pd.DataFrame()
for i in range(len(short)):
    
    #department dataframe from crawled data  
    dept = info[info['Short'] == short[i]]
    dept = dept.reset_index(drop=True)

    #title row for the department 
    title = pd.DataFrame(columns=['Dept./Prog.(name)',
                                  'Course Code',
                                  'Course Name'])
    
    #department courses' information 
    G = dept[dept['Code.Sec'].str[-3] > '4']
    G = G[G['Code.Sec'].str[-3] < '9']['Code.Sec'].nunique()
    total_course = dept['Code.Sec'].nunique()
    U = total_course - G
    title.loc[len(title)] = [short[i] + '(' + long[i] + ')',
                             'U' + str(U) + ' G' + str(G),
                             '']

    #table format for csv file 
    main = pd.DataFrame(columns=['Dept./Prog.(name)','Course Code','Course Name'])
    main[['Course Code','Course Name']] = dept[['Code.Sec','Name']]
    main = main.drop_duplicates(subset='Course Code',keep='first',inplace=False)
    main = main.sort_values('Course Code')
    main = main.reset_index(drop=True)

    res = pd.DataFrame(columns=['Dept./Prog.(name)','Course Code','Course Name'])
    res = pd.concat([title,main])
    res = res.replace(np.nan, '', regex=True)
    res = res.reset_index(drop=True)
    
    
    #Retrieves number of Grad and Undergrad courses
    total_U = 0
    total_G = 0
    total_I = (dept[dept['Instr.'] != 'STAFF STAFF']
               .nunique()['Instr.'])
    
    for term in np.arange(start_date,end_date+1):
        
        term_name = year_original(term)
        term_info = dept[dept['Term'] == term]

        
        #terms' courses information 
        term_title = pd.DataFrame(columns=[term_name])
        
        term_I = (term_info[term_info['Instr.'] != 'STAFF STAFF']
                  .nunique()['Instr.'])
        
        term_G = term_info[term_info['Code.Sec']
                           .str[-3] > '4']
        
        term_G = (term_G[term_G['Code.Sec']
                        .str[-3] < '9']
                  ['Code.Sec']
                  .nunique())
        
        term_Tot = (term_info
                    ['Code.Sec']
                    .nunique())
        
        term_U = term_Tot - term_G
        
        (term_title
         .loc[len(term_title)]) = ['U' +
                                   str(term_U) +
                                   ' G' +
                                   str(term_G) +
                                   ' I' +
                                   str(term_I)]
        
        
        term_main = pd.DataFrame(columns=[term_name])
        term_main[term_name] = main['Course Code']
        
        term_courses = pd.DataFrame(columns=[term_name])
        term_courses[term_name] = term_info['Code.Sec']
        term_courses = term_courses.drop_duplicates(subset=term_name,
                                                    keep='first',
                                                    inplace=False)
        term_courses = term_courses.reset_index(drop=True)
        
        #Indicates whether course opened or not in this semester
        term_main[term_name] = (np.where
                                ((term_main
                                  [term_name]
                                  .isin(term_courses[term_name]))
                                 ,'x',''))

        #calculates total number of grads and undergrads courses
        total_U = total_U + term_U
        total_G = total_G + term_G
        
        term_res = pd.DataFrame(columns=[term_name])
        term_res = pd.concat([term_title,
                              term_main])

        res[term_name] = term_res[term_name].values
        
        
    #Total Offering Information Retrieval 
    total_title = pd.DataFrame(columns=['Total Offerings'])
    total_title.loc[len(total_title)] = ['U' +
                                         str(total_U) +
                                         ' G' +
                                         str(total_G) +
                                         ' I' +
                                         str(total_I)]
    
    total_main = pd.DataFrame(columns=['Total Offerings'])
    total_main['Total Offerings'] = main['Course Code']
    (total_main['Total Offerings']) = (total_main['Total Offerings']
                                       .apply(lambda x:
                                              str(dept[dept['Code.Sec'] == x]
                                                  ['Term']
                                                  .nunique()) +
                                              '/' +
                                              str(dept[dept['Code.Sec'] == x]
                                                  ['Instr.']
                                                  .nunique())))
    
    total_res = pd.concat([total_title,
                           total_main])
    res['Total Offerings'] = (total_res['Total Offerings']
                              .values)
    
    final = pd.concat([final,
                       res])


# In[12]:


#Last modification to write csv file.
final = final.reset_index(drop=True)
final = '"'+ final +'"'
final.set_index('Dept./Prog.(name)',inplace=True)
final.to_csv(sys.stdout)

