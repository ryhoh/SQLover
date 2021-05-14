# SQLabo

[![MIT License](readme_resources/license-mit-blue.svg?style=flat)](LICENSE)
![Heroku](https://heroku-badge.herokuapp.com/?app=sqlabo)

## Abstract
This is an application that allows you to practice SQL in a quiz format in your browser.

### Motivation
There are services that allow you to practice programming (algorithm implementation), but I couldn't find any that allow you to practice SQL, so I created my own.

### Usage
1. go to https://sqlabo.herokuapp.com/
2. Select a problem from the list
3. Read the provided tables, descriptions and example output, and write a SQL statement that meets the requirements. 
4. submit
5. Check the results

### Distinctive Features
- On an independent database, create tables, execute user queries, and check the results against a model answer to determine correct or incorrect
- There is a simple account function
    - When you log in, you will be able to see at a glance the problems you have completed in the past
        
        <img src="readme_resources/problem_list.png">

- Anyone can create and post a problem
    - All problems are written in JSON format following the given format
    - Posted problem will be accepted in a PR on GitHub, and the content will be checked before it is reflected
        - I deliberately chose not to manage it in a database
- Japanese and English are supported

## Thanks to ...
This software is using other libraries.

- natsort
    - https://github.com/SethMMorton/natsort
    - by SethMMorton et al.

---

Copyright (c) 2021 Tetsuya Hori a.k.a. ryhoh / shirosha2
