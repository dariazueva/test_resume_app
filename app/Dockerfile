FROM python:3.12.0

ENV HOME=/home/fast \
    APP_HOME=/home/fast/app \
    PYTHONPATH="$PYTHONPATH:/home/fast" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN mkdir -p $APP_HOME \
 && groupadd -r fast \
 && useradd -r -g fast fast

WORKDIR $APP_HOME

COPY app/requirements.txt .
COPY app/ .
COPY alembic.ini .
COPY migrations/ migrations/

RUN pip install --upgrade pip \
 && pip install -r requirements.txt \
 && chown -R fast:fast $HOME

USER fast