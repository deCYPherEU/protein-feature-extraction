FROM --platform=linux/amd64 python:3.11-slim

# System dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install git wget -y

# Install requirements
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Install fondant
RUN pip3 install fondant[component]==0.10.1

# Set the working directory to the component folder
WORKDIR /component/src

# Download the clustalo alignment tool
RUN wget http://www.clustal.org/omega/clustalo-1.2.4-Ubuntu-x86_64 && \
    mv clustalo-1.2.4-Ubuntu-x86_64 clustalo && \
	chmod +x clustalo && \
	mv clustalo /usr/local/bin/

# Copy over src-files and spec of the component
COPY src/ .

ENTRYPOINT ["fondant", "execute", "main"]