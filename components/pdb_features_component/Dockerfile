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

# Download MSMS
RUN wget https://ccsb.scripps.edu/msms/download/933/
RUN tar -xvf msms_i86_64Linux2_2.6.1.tar.gz
RUN mv msms_i86_64Linux2_2.6.1/msms /usr/local/bin

# Set the working directory to the component folder
WORKDIR /component/src

# Copy over src-files and spec of the component
COPY src/ .

ENTRYPOINT ["fondant", "execute", "main"]