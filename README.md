# SQLabo

[![MIT License](readme_resources/license-mit-blue.svg?style=flat)](LICENSE)
![Heroku](https://heroku-badge.herokuapp.com/?app=sqlabo)

## Abstract
This is an application that let you to practice SQL as a problem format on your browser.

### Motivation
There are some services that let you to practice programming (algorithm implementation).  
However, I couldn't find any services to practice SQL, so I created it.

### Usage
1. go to https://sqlabo.herokuapp.com/
2. Select a problem from the list
3. Read the provided tables, descriptions and example output, and write a SQL statement that meets the requirements.
4. Submit
5. Check the results

### Distinctive Features
- On a database (independent from service database!), this service can execute user queries, and check the results with true answer
- There is a simple account function
    - When you log in, you will be able to see at a glance the problems you have completed in the past

        <img src="readme_resources/problem_list.png">

- Anyone can create and post a problem
    - All problems are written in JSON format following the given format
    - User's problem will be accepted on GitHub (send me PR), and the content will be checked before it is registered
        - I deliberately chose not managing it in a database
- Japanese and English are supported

## Thanks to ...
This software is using other libraries.

- natsort
    - https://github.com/SethMMorton/natsort
    - by SethMMorton et al.

---

Copyright (c) 2021 ryhoh / shirosha2
