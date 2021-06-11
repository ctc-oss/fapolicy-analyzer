FROM buildpack-deps:bionic-scm as tagger

RUN curl -so /usr/local/bin/git-rpm-version https://raw.githubusercontent.com/peterlundgren/git-rpm-version/master/git-rpm-version \
 && chmod +x /usr/local/bin/git-rpm-version

WORKDIR /tmp
COPY .git ./.git
RUN git-rpm-version -v HEAD > VERSION
RUN git-rpm-version -r HEAD > RELEASE

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
COPY src     ./src
COPY python  ./python
COPY Cargo.* ./

WORKDIR /opt/app-src/python
RUN pipenv install --system --deploy --dev
COPY --from=tagger /tmp/VERSION /tmp/RELEASE ./

WORKDIR /opt/app-src
COPY scripts ./scripts

VOLUME /output

WORKDIR /opt/app-src/python
ENTRYPOINT ["/opt/app-src/scripts/rpm/build.sh"]
