FROM python:3.8
WORKDIR /app
COPY ./config/requirements.txt ./config/requirements.txt
RUN pip install -r ./config/requirements.txt
COPY . .
CMD ["python", "bot.py"]