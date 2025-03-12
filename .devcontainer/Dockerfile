FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# Build arguments
ARG USERNAME=wizard
ARG USER_UID=1000
ARG USER_GID=$USER_UID

ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libgl1-mesa-glx \
    qtbase5-dev \
    qt5-qmake \
    qtbase5-dev-tools \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    xvfb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

# Create project directory and set user permissions
RUN mkdir -p /home/$USERNAME/app \
    && chown -R $USERNAME:$USERNAME /home/$USERNAME

# Switch to non-root user
USER $USERNAME
WORKDIR /home/$USERNAME/app

# Create a virtual environment instead of using the system Python
RUN uv venv /home/$USERNAME/.venv

# Configure environment to use the virtual environment
ENV PATH="/home/$USERNAME/.venv/bin:$PATH" \
    VIRTUAL_ENV="/home/$USERNAME/.venv"

# Install base packages in the virtual environment
RUN uv pip install black pytest pytest-cov
