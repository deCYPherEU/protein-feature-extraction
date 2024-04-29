FROM --platform=linux/amd64 fndnt/fondant:0.11.dev5-py3.10

# System dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install git -y

# Install requirements
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Set the working directory to the component folder
WORKDIR /component/src

# Clone the DeepTMpred repository
RUN git clone https://github.com/ISYSLAB-HUST/DeepTMpred.git .

# Copy the model_files directory
COPY /src/model_files/deepTMpred-b.pth ./model_files/
COPY /src/model_files/orientaion-b.pth ./model_files/

# Copy over src-files and spec of the component
COPY src/ .

ENTRYPOINT ["fondant", "execute", "main"]