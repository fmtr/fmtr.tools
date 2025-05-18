ARG BASE

FROM fmtr/${BASE} AS dev

ARG ORG
ARG PACKAGE

USER user
WORKDIR /opt/dev/repo/${ORG}.${PACKAGE}

COPY --from=package --chown=user:user requirements.py .

ARG EXTRAS
RUN python requirements.py ${EXTRAS} > requirements.txt
RUN pip install -r requirements.txt --no-cache-dir
WORKDIR /

FROM base AS prod
COPY --from=package --chown=user:user  .. .
RUN pip install . --no-cache-dir
WORKDIR /