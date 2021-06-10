FROM fedora:32

WORKDIR /tmp
RUN curl -o rust.sh https://sh.rustup.rs -sSf \
 && chmod a+x rust.sh \
 && ./rust.sh -y -q --profile minimal \
 && rm rust.sh

RUN ln -s /root/.cargo/bin/* /usr/local/bin

RUN dnf install -y python38 python3-devel python3-pip dbus-devel cairo-devel pkg-config which \
                   gobject-introspection-devel cairo-gobject-devel fedora-packager fedora-review \
 && dnf groupinstall -y "Development Tools" \
 && dnf clean all

RUN pip3 install pipenv wheel

WORKDIR /opt/app-src
COPY . .

WORKDIR /opt/app-src/python
RUN pipenv install --system --deploy --dev

ENTRYPOINT ["/opt/app-src/scripts/rpm/build.sh"]
