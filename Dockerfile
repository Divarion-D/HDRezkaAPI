# first stage
FROM python:3.8 AS bilder
COPY requirements.txt .

# Install dependencies
RUN pip install --user -r requirements.txt

# second unnamed stage
FROM python:3.8-slim
WORKDIR /code

# Copy in the requirements from the 1st stage image
COPY --from=bilder /root/.local /root/.local
COPY . .

# update PATH environment variable
ENV PATH=/root/.local:$PATH

CMD ["python", "./api.py"]