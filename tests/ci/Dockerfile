FROM base/archlinux:latest

RUN pacman -Syuq --noconfirm \
    gcc \
    libx11 \
    make \
    pkg-config \
    postgresql-libs \
    python \
    python-pip \
    qt5-base \
    redis \
    rustup \
    xorg-server-xvfb \
    mpfr

RUN rustup override set nightly-2018-05-15

RUN pip install \
    PyQt5 \
    Quamash==0.6.0 \
    aiohttp==2.3.6 \
    aioredis==1.0.0 \
    coverage \
    freezegun \
    hiredis==0.2.0 \
    mock \
    nose \
    pycodestyle \
    redis==2.10.6 \
    requests==2.18.4 \
    sqlparse==0.2.4

ENV TZ=Europe/Paris
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
