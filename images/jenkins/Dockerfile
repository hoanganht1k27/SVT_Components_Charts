FROM jenkins/jenkins:lts-jdk11
USER root

RUN apt update -y && \
    apt -y -qq --no-install-recommends install iputils-ping sshpass openssl lsb-release net-tools vim python3-pip ca-certificates curl gnupg lsb-release jq && \
    apt autoclean && \
    apt autoremove -y
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

RUN apt update -y && \
    apt -y -qq --no-install-recommends install docker-ce-cli && \
    apt autoclean && \
    apt autoremove -y

# Install semetic-release
RUN apt update -y && \
    curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt -y -qq --no-install-recommends install nodejs && \
    apt autoclean && \
    apt autoremove -y && \
    npm install semantic-release -g && \
    npm install @semantic-release/github -g && \
    npm install @semantic-release/commit-analyzer -g && \
    npm install @semantic-release/release-notes-generator -g

RUN apt-get install  -y -qq --no-install-recommends wget -y  && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | tee /etc/apt/sources.list.d/google-chrome.list && \
    apt update -y   && \
    apt-get  install -y gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 libfontconfig1 \
                        libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 fonts-liberation \
                        libnss3 lsb-release xdg-utils    && \
    apt-get install -y google-chrome-stable  && \
    apt autoclean

RUN pip install webdrivermanager --no-cache-dir && \
    webdrivermanager chrome --linkpath /usr/local/bin

COPY ./requirements.txt /tmp/requirements.txt
RUN yes | pip install -r /tmp/requirements.txt --no-cache-dir
