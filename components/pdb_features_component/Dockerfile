FROM --platform=linux/amd64 python:3.10-slim

# System dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install git -y && \
    apt-get install wget -y && \
    apt-get install build-essential -y

# Install requirements
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Download and extract MSMS
RUN wget https://ccsb.scripps.edu/msms/download/933/msms_i86_64Linux2_2.6.1.tar.gz && \
    tar -xvf msms_i86_64Linux2_2.6.1.tar.gz && \
    ls -l && \
    mv msms.x86_64Linux2.2.6.1 /usr/local/bin/msms

# Set the working directory to the component folder
WORKDIR /component/src

# Copy over src-files and spec of the component
COPY src/ .

ENTRYPOINT ["fondant", "execute", "main"]