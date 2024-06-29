# Realtime Election Data Project

## Overview

This is a side project focused on working with modern big data technologies to build a real-time election end-to-end system. The aim is to broaden knowledge in data engineering by using technologies like Apache Kafka and Apache Spark.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Acknowledgements](#acknowledgements)

## Features
- Real-time data streaming with Apache Kafka.
- Data processing and analysis using Apache Spark.
- Dockerized deployment for easy setup and scaling.
- Python-based application with PostgreSQL integration.
- Real-time data visualization with Streamlit.

## Technologies Used
- **Apache Kafka**: For real-time data streaming.
- **Apache Spark**: For data processing and analysis.
- **Docker**: For containerization.
- **PostgreSQL**: As the database.
- **Python**: The main programming language used.

## Prerequisites

- **Java Development Kit (JDK)**: Ensure you have Java 8 or later installed, which is required for PySpark.
- **Python**: Make sure Python 3.9 or later is installed.
- **Docker**: Docker and Docker Compose need to be installed on your machine.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/sallahda/realtime-election-data-project.git
    cd realtime-election-data-project
    ```

2. Set up the environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Build and run the Docker containers:
    ```bash
    docker-compose up --build
    ```

## Usage

1. Ensure all services are running:
    ```bash
    docker-compose ps
    ```

2. Run the application to create the database, tables, and generate mock data:
    ```bash
    python app.py
    ```

3. In different terminals, run the following commands simultaneously:
    ```bash
    python voting-system.py
    python spark-streaming.py
    ```

4. To visualize all the processed data in real-time, run:
    ```bash
    streamlit run streamlit-dashboard.py
    ```

## Acknowledgements

Thanks to Yusuf Ganiyu for the knowledge shared through his tutorial.
