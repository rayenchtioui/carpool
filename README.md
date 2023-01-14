# CarPool

Carpooling web server which manages and organizes carpools between Tunisian cities.

## Tech Stack

**Server:** Python, Fastapi, Postgresql

## Environment Variables

To run this project, you will need to add the following environment variables to your `.env` file

`database_hostname`

`database_port`

`database_password`

`database_name`

`database_username`

`secret_key`

`algorithm`

`access_token_expire_min`

`mail_username`

`mail_password`

`mail_from`

`mail_server`

## Run Locally

Clone the project

```bash
  git clone https://github.com/rayenchtioui/carpool.git
```

Go to the project directory

```bash
  cd my-project
```

Install dependencies

```bash
  pip install -r requirements.txt
```

set up the database

```bash
  alembic upgrade head
```

for the client endpoints run:

```bash
  uvicorn app.main:app
```

for the admin endpoints run:

```bash
  uvicorn app.main:app_admin
```

## Explanation of the Authentification Process:

1 / the user create an account via `/user/` endpoint

2 / an email will be sent to confirm the account

## Authorization Policies

### for User:

A user can access,modify, delete and update his informations

A user can apply for any pool he wants if the places are still available

A user cannot apply or write a review for himself

### for Pool:

A user can see all the pools available

A user can add, modify or delete his pool

A user must have add a car in order to create a pool

An admin can delete any pool

### for Car:

A user can see all his cars

A user can add, modify or delete any of his cars
