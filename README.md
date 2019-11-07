# Web-Crawler
Crawls courses' data from Bogazici University registration web site
### Intro 
Pandas library is used to manage and manipulate the data. There are two arrays contains short and long names of the departments.
### Inputs

First takes the argumnets and converts them into encoded format.

```python
start_term = sys.argv[1]
end_term = sys.argv[2]
start_date = year_encoder(start_term)
end_date = year_encoder(end_term)
```
***
### Encoding and Decoding of Terms

In order to ease the use of for loop there is a function that transforms given date formats into numerical correspondings. Also there is a decoder function that prepares proper time substring for the url.

```python
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
```
***
### Derivation of the URL

This function takes short and long name of the deparment and the term information to derive URL with basic string manipulations.

```python
#makes url by using short name, term, department name
def make_url(term,short,long):
    init = 'https://registration.boun.edu.tr/scripts/sch.asp?donem='
    init2 = '&kisaadi='
    init3 = '&bolum='
    return init + year_format(term) + init2 + short + init3 + make_long(long)
```
Prepares long name of the department to use in the URL.
```python
#transforms department names to proper long format for url 
def make_long(x):
    x = x.replace('&','%26')
    x = x.replace(':','%3a')
    x = x.replace(',','%2c')
    x = x.replace(' ','+')
    return x
```
***
### Crawling

In this section I crawl all the urls of the each department between given terms to create an dataframe to derive the data expected from me.
* Firstly, creates the particular URL.
* Then starts a try block if any thing causes an exception just skips that iteration.
    * Reads the html file of the URL.
    * Accesses the third table which holds the valueable informations.
    * Get rids of the colums other than Code.Sec, Name, and Instr.
    * Clears the unneccesary rows which are belong to PS and Labs.
    * Creates a new dataframe that holds the information of term, and long and short name.
    * Then adds colums of this data frame to the other list.
    * Finally concatenates the current dataframe with the info dataframe.
* When all the iterations are finished I have the info data frame which holds the Section Code, Name of the Course, Instructor, Term, Short Department Name, Long Department Name informations.
* At the end clears the section part of the course codes.
```python
mask = ['Code.Sec','Name','Instr.']
info = pd.DataFrame(columns=['Term','Short','Long','Name','Code.Sec','Instr.'])
for term in np.arange(start_date,end_date+1):
    for i in range(len(short)):
        url = make_url(term,short[i],long[i])
        try:
            temp_df = pd.read_html(url)
            temp_df = temp_df[3]
            t = temp_df
            t.rename(columns=t.loc[0],inplace=True)
            t.drop(index=0,inplace=True)
            t = t[mask]
            t = t.dropna()
            t.reset_index(inplace=True)
            new = pd.DataFrame(columns=['Term','Short','Long'])
            new = new.reindex(index=np.arange(len(t)))
            new[['Term','Short','Long']] = [term,short[i],long[i]]
            new[['Name','Code.Sec','Instr.']] = t[['Name','Code.Sec','Instr.']]
            info = pd.concat([new,info])
        except:
            pass
info.reset_index(inplace=True)
info.drop(columns='index',inplace=True)
info['Code.Sec'] = info['Code.Sec'].apply(lambda x:de_section(x))
```
***
### Information Retrieval From Each Department

Consequent processes are applied for each departments with a for loop

* Extracts department information from the info dataframe
```python
 #department dataframe from crawled data  
    dept = info[info['Short'] == short[i]]
    dept = dept.reset_index(drop=True)
```
* Prepares title and main parts for the first three columns of the table and concatenates them
```python
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
```
* First, gathers term info from the department dataframe. Then, creates a corresponding column for eac term. In order to do that creates a title part and main part for the column and concatenates with the previous dataframe.
```python
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
```
* Creates 'Total Offerings' columns (which is th last one) and concatenates with previous dataframe to create the final dataframe.
```python
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
```
***
### Last Touch
Makes final adjustifications and creates csv format and writes to standart output.
```python
#Last modification to write csv file.
final = final.reset_index(drop=True)
final = '"'+ final +'"'
final.set_index('Dept./Prog.(name)',inplace=True)
final.to_csv(sys.stdout)
```
