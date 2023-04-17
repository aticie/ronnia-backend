FROM python:3.11-slim-bullseye

ARG PORT
ENV PORT=$PORT

# Set the working directory
WORKDIR /src

# Copy the requirements.txt
COPY requirements.txt ./

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of the files
COPY ./app ./app

ENV PYTHONPATH=/src;/src/app

WORKDIR /src
# Start the app
CMD uvicorn app.main:app --host :: --port ${PORT}
