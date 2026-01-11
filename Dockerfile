FROM python:3.13-slim

COPY ./pyproject.toml .
RUN pip install uv 
RUN uv pip install --system -r pyproject.toml 
RUN pip cache purge && uv cache clean

WORKDIR /code
COPY . /code

CMD ["/code/teachio.sh", "--dev", "run"]