FROM whtsky/shapaozi_python_runtime

ENV PYTHONUNBUFFERED 1

COPY . /app/

WORKDIR /app/
