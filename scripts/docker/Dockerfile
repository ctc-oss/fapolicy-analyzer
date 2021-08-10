FROM ctcoss/fapolicyd as build

WORKDIR /tmp
RUN curl -o rust.sh https://sh.rustup.rs -sSf \
 && chmod a+x rust.sh \
 && ./rust.sh -y -q --profile minimal \
 && rm rust.sh

RUN ln -s /root/.cargo/bin/* /usr/local/bin

RUN dnf install -y python39 python3-devel python3-pip dbus-devel cairo-devel pkg-config which \
                   gobject-introspection-devel cairo-gobject-devel \
 && dnf groupinstall -y "Development Tools" \
 && dnf clean all

RUN pip3 install pipenv

WORKDIR /opt/app-src
COPY . .

RUN cargo build --examples

WORKDIR /opt/app-src/python
RUN pipenv install --system --deploy --dev
RUN python3 setup.py install

# ----------------------------------------------

FROM ctcoss/fapolicyd as main

RUN dnf install -y python39 python3-pip dbus-libs pkg-config which \
                   gtk3 xorg-x11-server-Xvfb nano \
 && dnf clean all

COPY --from=build /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=build /usr/local/lib64/python3.9/site-packages/ /usr/local/lib64/python3.9/site-packages/
COPY --from=build /opt/app-src/python /opt/app/
COPY --from=build /opt/app-src/target/debug/examples /usr/local/bin

RUN mkdir -p /var/lib/fapolicyd \
 && trustdb_init /var/lib/fapolicyd

WORKDIR /opt/app
ENTRYPOINT ["python3"]
