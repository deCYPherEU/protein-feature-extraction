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

# Copy over src-files and spec of the component
COPY src/ .

# install the github repo of iFeatureOmega-CLI and rename it to iFeatureOmega_CLI
RUN git clone https://github.com/Superzchen/iFeatureOmega-CLI
RUN mv iFeatureOmega-CLI iFeatureOmega_CLI

ENTRYPOINT ["fondant", "execute", "main"]