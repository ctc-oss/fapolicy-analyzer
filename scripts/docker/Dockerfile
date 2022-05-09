# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

FROM ctcoss/fapolicyd as build

WORKDIR /tmp
RUN curl -o rust.sh https://sh.rustup.rs -sSf \
 && chmod a+x rust.sh \
 && ./rust.sh -y -q --profile minimal \
 && rm rust.sh

RUN ln -s /root/.cargo/bin/* /usr/local/bin

RUN dnf install -y python3 python3-devel python3-pip dbus-devel cairo-devel pkg-config which \
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

RUN dnf install -y python3 python3-pip dbus-libs pkg-config which \
                   gtk3 xorg-x11-server-Xvfb nano \
 && dnf clean all

COPY --from=build /usr/local/lib/python3.6/site-packages/ /usr/local/lib/python3.6/site-packages/
COPY --from=build /usr/local/lib64/python3.6/site-packages/ /usr/local/lib64/python3.6/site-packages/
COPY --from=build /opt/app-src/python /opt/app/
COPY --from=build /opt/app-src/target/debug/examples /usr/local/bin

RUN mkdir -p /var/lib/fapolicyd \
 && trustdb_init /var/lib/fapolicyd

WORKDIR /opt/app
ENTRYPOINT ["python3"]
