ARG BASE

FROM fmtr/${BASE} AS base

ARG ORG
ARG PACKAGE
WORKDIR /opt/dev/repo/${ORG}.${PACKAGE}

COPY --from=package requirements.py .
RUN python requirements.py pdf,logging,debug,ai.client,sets > requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

FROM base AS dev

FROM base AS prod
COPY --from=package .. .
RUN pip install . --no-cache-dir