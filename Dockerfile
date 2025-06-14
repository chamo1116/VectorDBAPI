# Use a multi-stage build to optimize image size
# Builder stage
FROM python:3.9-slim AS builder

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /vectorapi

# Copy project files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --locked

# Copy the rest of the application code
COPY . .

# Final stage
FROM python:3.9-slim

# Set working directory
WORKDIR /vectorapi

# Copy the virtual environment and application code from the builder stage
COPY --from=builder /vectorapi /vectorapi

# Set the path to include the virtual environment's bin directory
ENV PATH="/vectorapi/.venv/bin:$PATH"
ENV PYTHONPATH="/vectorapi"

RUN pip install uv

# Command to run the application
CMD ["uv", "run", "uvicorn", "app.core.main:app", "--host", "0.0.0.0", "--port", "8000"]
