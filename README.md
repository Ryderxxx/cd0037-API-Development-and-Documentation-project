# Trivia - API Development and Documentation Final Project

## Introduction

Trivia is a simple web APP that you can use to share questions and its answers, and it also allows you to take quizzes which made up of questions uploaded by other users.

![Snipaste20220327220457png](https://raw.githubusercontent.com/Ryderxxx/ImageWarehouseofMarkText/main/2022/03/27-22-08-01-Snipaste_2022-03-27_22-04-57.png)

It contains branch of API that you can use to:

1. Fetch questions in json format.
  
2. Upload/Delete a question
  
3. Search for questions by text
  
4. Get a quiz question
  
<br>

## Getting Started

You may follow the steps below to run Trivia locally, the default base URLs are localhost:3000 (frontend) and localhost:5000 (backend), no authentication for using API.

1. Fetch this repository to your localhost.
  
2. Go to '/backend' and call 'pip install -r requirements.txt' to build dependencies.
  
3. Set up database by 'createdb trivia' and 'psql trivia < trivia.psql'.
  
4. Initialize with 'export FLASK_APP=trivia FLASK_ENV=development'.
  
5. Run the backend server by 'flask run --reload'.
  
6. Go to '/frontend' and call 'npm install' to build dependencies of frontend.
  
7. Call 'npm start' to start the frontend server.
  
8. OK, now you can view Trivia (localhost:3000) with your browser!
    
<br>

## Error

4 common types of HTTP errors are used in Trivia:

1. 400 Bad Request
  
2. 404 Resource Not Found
  
3. 422 Unprocessable
  
4. 500 Internal Server Error
    
<br>

## Resource Endpoint Library

### GET /categories

- Usage: get all available categories
  
- Request parameters: None
  
- Response body: {
  
  'categories': categories_dict
  
  }
    
<br>

### GET /questions?page=<int:page_number>

- Usage: get questions of a certain page
  
- Request parameters: page_number (int, default: 1)
  
- Response body: {
  
  'questions': questions_list,
  
  'total_questions': Question.query.count(),
  
  'categories': categories_dict,
  
  'current_category': None
  
  }
    
<br>

### DELETE /questions/<int:id>

- Usage: delete a question by its id
  
- Request parameters: question_id (int)
  
- Response body: {
  
  'id': id
  
  }
  
<br>

### POST /questions

- Usage: search questions by text
  
- Request parameters: searchTerm (str)
  
- Response body: {
  
  'questions': [question.format() for question in search_results],
  
  'total_questions': len(search_results)
  
  }
    
<br>

### POST /questions

- Usage: post a new question
  
- Request parameters: answer (str), question (str), category (str), difficulty (int)
  
- Response body: None
    
<br>

### GET /categories/<int:category_id>/questions

- Usage: get questions of a certain category
  
- Request parameters: category_id (int)
  
- Response body: {
  
  'questions': questions_list,
  
  'totalQuestions': len(questions_list),
  
  'currentCategory': category.type
  
  }
    
<br>

### POST /quizzes

- Usage: get a new quiz question
  
- Request parameters: quiz_category (int), previous_questions (list)
  
- Response body: {
  
  'questions': random.choice(questions).format()
  
  }
