FROM ctcoss/fapolicyd as build

WORKDIR /tmp
RUN curl -o rust.sh https://sh.rustup.rs -sSf \
 && chmod a+x rust.sh \
 && ./rust.sh -yq --profile minimal \
 && rm rust.sh

RUN ln -s /root/.cargo/bin/* /usr/local/bin

RUN dnf install -y python38 python3-devel python3-pip dbus-devel cairo-devel pkg-config which \
 && dnf groupinstall -y "Development Tools" \
 && dnf clean all

RUN pip3 install pipenv

WORKDIR /opt/app-src
COPY . .

WORKDIR /opt/app-src/py
RUN pipenv install --system --deploy --dev
RUN python3 setup.py install

ENTRYPOINT ["python3"]
