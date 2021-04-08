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

WORKDIR /opt/app-src/python
RUN pipenv install --system --deploy --dev
RUN python3 setup.py install

FROM ctcoss/fapolicyd

COPY --from=build /usr/local/lib/python3.8/site-packages/ /usr/local/lib/python3.8/site-packages/
COPY --from=build /usr/local/lib64/python3.8/site-packages/ /usr/local/lib64/python3.8/site-packages/
COPY --from=build /opt/app-src/python /opt/app/

RUN dnf install -y dbus-libs \
 && dnf clean all

WORKDIR /opt/app
ENTRYPOINT ["python3"]
