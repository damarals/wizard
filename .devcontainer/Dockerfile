FROM sunpeek/poetry:py3.11-slim

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Build arguments
ARG USERNAME=wizard
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Install required packages for Qt/PySide6
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

# Add Poetry to PATH for the user
ENV PATH=/root/.local/bin:/home/$USERNAME/.local/bin:$PATH

# Switch to non-root user
USER $USERNAME
WORKDIR /home/$USERNAME/app

# Configure Poetry
RUN poetry config virtualenvs.in-project true \
    && poetry config virtualenvs.prompt "venv"