#!/bin/bash
# Install required packages
pip install pandas

# Run database migrations
airflow db upgrade

# Create an admin user
airflow users create \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com

# Sleep for a bit before finishing
sleep 10
