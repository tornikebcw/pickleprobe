FROM python:3.10
COPY . . 
RUN pip install -r requirements.txt
EXPOSE 3000
ARG env
ARG client
ENV env=${env}
ENV client=${client}
CMD [ "python","-u","main.py"]
