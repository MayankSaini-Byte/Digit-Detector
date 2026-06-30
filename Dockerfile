FROM python:3.11-slim

# Hugging Face Spaces specific environment variables
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

# Create a non-root user 'user' with UID 1000 (Required by HF Spaces)
RUN useradd -m -u 1000 user

# Set the working directory to the user's home directory
WORKDIR $HOME/app

# Install dependencies first (leverage Docker cache)
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY --chown=user . .

# Switch to the non-root user
USER user

# Expose the port that Hugging Face Spaces expects
EXPOSE 7860

# Run the application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:app"]
