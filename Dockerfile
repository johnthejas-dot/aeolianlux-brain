# Use the official lightweight Python image.
FROM python:3.9-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Set up the working directory
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy local code to the container image
COPY . ./

# Install production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Streamlit runs on
EXPOSE 8080

# Run the web service on container startup
CMD streamlit run app.py --server.port=8080 --server.address=0.0.0.0
