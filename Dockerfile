FROM python:3.10
COPY . . 
RUN pip install -r requirements.txt
EXPOSE 3000
ARG env=local
ENV env=${env}
CMD [ "python","-u","main.py"]
