# Welcome to the Better Billing Project

## What is Better Billing?
Better Billing a demo app which is built for Legal Billing. The app focuses on the time entry, billing and invoicing side of legal billing and works off a simple database framework. 

## How Better Billing works 
Lawyers (fee earners) input their time worked with a description of the work performed submitted against a client, matter and activiy code. The administrator, in this scenario the Partners, can then pick up and review the time entries then push them to an randomly generated invoice number. 

The user interactions create data that is pushed into the database via the Record Time interface, data is then fed through to WIP and eventually onto the Invoice/Ledger tables. In line with CRUD principles the user can create, read, update and entries based on permissions. 

## Dependencies
The app relies on Django & Python alongside various imports and supporting packages to manage AJAX, SQL queries, date/time widgets, authentication, validation errors and messages. 

HTML5 is used in conjunction with the Django template format. The base template holds all the HTML document syntax alongside the load static command to globally apply the favicons, custom CSS3, Bootstrap CSS and Javascript.

## Set & Up and Installations

[Click here to read through installation and deployment steps for Github, Django and Heroku](/readme_docs/deploy_install.md)

## NB:
This version of the application works well in a small law firm scenario. It can be scaled or linked to APIs and additional features can be added to handle matter maintainance and rates, for example. Currently, the app relies on the business user having applications and/or databases that could handle the matter, personnel, rates, roles databases. 


## Project Documentation

Click the links below to view each section 

### [User Stories](/readme_docs/user_story.md)
This document outlines the key user stories defined for the **Better Billing** application.  
Each story details a specific feature from the end-user perspective, highlighting the goals, motivations, and acceptance criteria that guided the development process.

---

### [UX](/readme_docs/ux.md)
This document explains how user experience (UX) principles were applied throughout the development of the **Better Billing** application.  
It covers the design rationale, information architecture, accessibility considerations, and visual hierarchy that guided the interface design.  
The section also highlights how Bootstrap and custom CSS were used to create a consistent, responsive, and professional layout, supported by user feedback and iterative refinement.


---

### [Testing](/readme_docs/testing.md)
The testing documentation provides an overview of all testing methodologies used throughout the project, including **manual, functional, and unit testing**.  
It explains how the system was validated to ensure reliability, usability, and compliance with the project’s requirements.

---

### [Bugs](/readme_docs/bugs.md)
This section records all major bugs identified during development, alongside their root causes and resolutions.  
It demonstrates the debugging strategies, tools, and good practices applied to ensure a robust and maintainable codebase.

# Sources

View all reading materials and sources [here](/readme_docs/sources.md)


