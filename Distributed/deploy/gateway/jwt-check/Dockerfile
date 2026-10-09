FROM python:3.12-slim

RUN pip install --no-cache-dir "pyjwt[crypto]==2.10.1"

COPY jwt_check.py /usr/local/bin/jwt_check.py

USER nobody
EXPOSE 8081

ENTRYPOINT ["python", "-u", "/usr/local/bin/jwt_check.py"]
