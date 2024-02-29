FROM python:3.9.13-alpine3.16

# py3-netaddr is required for ansible ipaddr
RUN apk add tini tar curl bash openssh sshpass 'ansible==5.8.0-r0' 'py3-netaddr==0.8.0-r2' zip

WORKDIR /usr/app

COPY backend/ /usr/app
RUN pip install --no-cache-dir -r src/requirements.txt

#RUN chmod 755 /usr/app/conf/playbookrun.sh

# Copy built application files
COPY frontend/dist/index.html /usr/app/src/static_root/
COPY frontend/dist/static /usr/app/src/static_root/static

# Copy ansible conf & common-roles
COPY ansible-common /ansible-common
ENV ANSIBLE_CONFIG /ansible-common/ansible.cfg

# Copy PCD_PACKAGES
RUN mkdir -p /usr/app/installation
RUN mkdir -p /var/lib/pcd/available_packages
COPY built_packages /var/lib/pcd/available_packages

# Init Mocking config
COPY backend/conf/mocking-dist.json /usr/app/installation/mocking.json

# Add Tini (init process that clean Zombies) https://github.com/ansible/ansible/issues/49270
ENTRYPOINT [ "/sbin/tini", "--" ]
CMD [ "/usr/local/bin/python", "/usr/app/src/api.py", "&", "echo $! > api.pid" ]