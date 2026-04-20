FROM postgres:18-alpine

COPY ./compose/production/postgres/maintenance /usr/local/bin/maintenance
RUN chmod +x /usr/local/bin/maintenance/* \
    && find /usr/local/bin/maintenance -maxdepth 1 -type f -exec mv {} /usr/local/bin/ \; \
    && rm -rf /usr/local/bin/maintenance
