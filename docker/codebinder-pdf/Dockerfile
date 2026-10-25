FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        fontconfig \
        fonts-freefont-otf \
        fonts-noto-cjk \
        git \
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

RUN ln -sf /usr/bin/python3 /usr/local/bin/python

WORKDIR /workspace

CMD ["bash"]
