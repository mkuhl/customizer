FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Install Python 3.12 and required packages + CLI tools for Claude Code
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    curl \
    wget \
    git \
    tree \
    jq \
    unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install modern CLI tools that Claude Code benefits from
RUN curl -LO https://github.com/BurntSushi/ripgrep/releases/download/14.1.1/ripgrep_14.1.1-1_amd64.deb \
    && dpkg -i ripgrep_14.1.1-1_amd64.deb \
    && rm ripgrep_14.1.1-1_amd64.deb

RUN curl -LO https://github.com/sharkdp/fd/releases/download/v10.2.0/fd_10.2.0_amd64.deb \
    && dpkg -i fd_10.2.0_amd64.deb \
    && rm fd_10.2.0_amd64.deb

RUN curl -LO https://github.com/sharkdp/bat/releases/download/v0.24.0/bat_0.24.0_amd64.deb \
    && dpkg -i bat_0.24.0_amd64.deb \
    && rm bat_0.24.0_amd64.deb

RUN curl -LO https://github.com/junegunn/fzf/releases/download/v0.55.0/fzf-0.55.0-linux_amd64.tar.gz \
    && tar -xzf fzf-0.55.0-linux_amd64.tar.gz \
    && mv fzf /usr/local/bin/ \
    && rm fzf-0.55.0-linux_amd64.tar.gz

# Create non-root user (if not exists)
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Check if user/group exists before creating
RUN (getent group $USER_GID || groupadd --gid $USER_GID $USERNAME) \
    && (id -u $USERNAME 2>/dev/null || useradd --uid $USER_UID --gid $USER_GID -m $USERNAME) \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Install uv for all users
RUN curl -LsSf https://astral.sh/uv/install.sh | sh -s -- --no-modify-path \
    && mv /root/.local/bin/uv /usr/local/bin/ \
    && chmod 755 /usr/local/bin/uv

# Set PATH for all users
ENV PATH="/usr/local/bin:${PATH}"

USER $USERNAME