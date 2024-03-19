FROM --platform=linux/amd64 python:3.11-slim

# System dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install git -y

# Install requirements
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Install fondant
RUN pip3 install fondant[component]==0.10.1

# Set the working directory to the component folder
WORKDIR /component/src

# Copy the .env file to the component folder
COPY .env .

# Copy the google_cloud_credentials.json file to the component folder
COPY google_cloud_credentials.json .

# Copy over src-files and spec of the component
COPY src/ .

ENTRYPOINT ["fondant", "execute", "main"]