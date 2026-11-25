FROM node:22-bookworm-slim AS node-runtime

FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        fontconfig \
        fonts-freefont-otf \
        fonts-noto-cjk \
        git \
        libasound2t64 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libcups2 \
        libdbus-1-3 \
        libdrm2 \
        libgbm1 \
        libgtk-3-0 \
        libnspr4 \
        libnss3 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libx11-xcb1 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
        latexmk \
        make \
        pandoc \
        poppler-utils \
        python3 \
        python3-pip \
        texlive-fonts-recommended \
        texlive-lang-chinese \
        texlive-latex-extra \
        texlive-latex-recommended \
        texlive-luatex \
        texlive-science \
        texlive-xetex \
    && fc-cache -f \
    && python3 -m pip install --break-system-packages --no-cache-dir \
        'git+https://github.com/ScottChiuNYC/codebinder.git@6c7070a25c50af52a2e751323aba92b231d8a411' \
        google-api-python-client \
        google-auth \
        google-auth-httplib2 \
        nbsphinx \
        sphinx \
        sphinx-copybutton \
        sphinx-rtd-theme \
    && rm -rf /var/lib/apt/lists/*

# Mermaid tooling belongs to the immutable PDF builder, not ephemeral CI downloads.
# Node is copied from the official Node image; Chrome for Testing is installed
# by Puppeteer and shared with unprivileged Docker workflow users.
COPY --from=node-runtime /usr/local/bin/node /usr/local/bin/node
COPY --from=node-runtime /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm
ENV PUPPETEER_CACHE_DIR=/opt/puppeteer-cache
RUN npm install -g --no-audit --no-fund @mermaid-js/mermaid-cli@11.9.0 \
    && chmod -R a+rX /opt/puppeteer-cache \
    && printf '{"args":["--no-sandbox","--disable-dev-shm-usage"]}\n' > /etc/mermaid-puppeteer.json

RUN ln -sf /usr/bin/python3 /usr/local/bin/python

WORKDIR /workspace

CMD ["bash"]
