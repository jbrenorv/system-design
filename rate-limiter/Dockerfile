FROM python:3.12

WORKDIR /code

COPY ./middleware /code/middleware
COPY ./* /code/

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

CMD ["fastapi", "run", "/code/main.py", "--port", "8000"]
