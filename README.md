# Waste Collection Bot for Calvenzano

This is a Telegram bot designed to provide information about the waste collection schedule for the municipality of Calvenzano (BG), Italy, for the year 2025. It helps residents stay informed about collection days for different types of waste and provides instructions for proper disposal.

## Features

  - **Daily and Next Day Collection Schedule:** Check which types of waste are collected today or tomorrow.
  - **Customizable Notifications:** Set a daily time to receive reminders for the next day's collection.
  - **Textile Collection Reminders:** Set your address to receive specific reminders and instructions when textile collection is scheduled (in progress).
  - **Disposal Instructions:** Get detailed information on how to properly dispose of different types of waste.
  - **Collection Center Hours:** View the opening hours of the municipal collection center.
  - **User Management:** The bot stores user preferences such as notification time and address.

## Architecture Overview

The bot is designed with a modular architecture and is intended to be deployed using Docker.

  - **`main.py`**: The main entry point for the Telegram bot. It initializes the application, sets up command handlers, and starts the bot.
  - **`docker-compose.yaml`**: Defines the services for the application, including the bot (`app`), a PostgreSQL database (`db`), and an Adminer instance for database management.
  - **`Dockerfile`**: Describes the steps to build the Docker image for the Python application, including installing dependencies from `requirements.txt`.
  - **`db_manager.py`**: Manages the connection to the PostgreSQL database using a connection pool. It handles all CRUD (Create, Read, Update, Delete) operations for user data.
  - **`config/waste_schedules.py`**: A configuration file containing the waste collection schedule, disposal instructions, and other constant data like month and day names in Italian.
  - **`commands/handlers.py`**: Contains the handler functions for all bot commands (e.g., `/start`, `/oggi`, `/domani`). These functions define the logic for how the bot responds to user interactions.
  - **`service/schedule.py`**: This module contains the logic for scheduling and sending daily notifications to users about upcoming waste collections.
  - **`tests/`**: This directory contains unit tests for various parts of the application, such as the database manager (`test_db_manager.py`), command handlers (`test_handlers.py`), and scheduling logic (`test_schedule.py`), ensuring the reliability of the bot's functionality.

## Bot Commands

  - `/start` - Starts the bot, displays a welcome message, and initiates the setup process (notification time and address). It also re-enables notifications if previously stopped.
  - `/oggi` - Shows the types of waste collected on the current day. (Today)
  - `/domani` - Shows the types of waste collected on the next day. (Tomorrow)
  - `/setNotifica` - Allows the user to set or change the time for daily notifications. (Set Notification)
  - `/setIndirizzo` - Allows the user to set or update their address for textile collection reminders. (Set Address)
  - `/info` - Displays detailed waste disposal instructions and collection center hours.
  - `/stop` - Disables daily notifications.

## Configuration

The bot relies on several configuration files and environment variables:

### 1\. Waste Collection Schedule (`config/waste_schedules.py`)

This file contains the core details for the bot's operation:

  - `WASTE_SCHEDULE`: A dictionary mapping waste types to specific collection days for each month of the year 2025.
  - `WASTE_INSTRUCTIONS`: A dictionary providing specific disposal instructions for each waste type.
  - `WASTE_EMOJI`: A dictionary associating emojis with each waste type for better visual representation.
  - `MONTH_NAMES`: Mapping of month numbers to Italian names.
  - `DAY_NAMES`: Mapping of weekday indices (0 for Monday) to Italian names.

### 2\. Environment Variables (`.env`)

You need to create a `.env` file in the root directory of the project with the following variables:

```env
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
DATABASE_URL=postgresql://POSTGRES_USER:POSTGRES_PASSWORD@db:5432/POSTGRES_DB
POSTGRES_USER=YOUR_POSTGRES_USER
POSTGRES_PASSWORD=YOUR_POSTGRES_PASSWORD
POSTGRES_DB=YOUR_POSTGRES_DB
```

Replace the placeholders with your actual values. These variables are used in `main.py`, `db_manager.py`, and `docker-compose.yaml`.

## Database

The bot uses a PostgreSQL database to store user information and preferences.

  - **Docker Image:** postgres:16
  - **Management:** Database connection and CRUD operations are handled by `db_manager.py`. It uses a connection pool for efficient management.

### `users` Table Structure:

  - `user_id` (BIGINT, PRIMARY KEY): User's Telegram ID.
  - `username` (VARCHAR(255)): User's Telegram username.
  - `first_name` (VARCHAR(255)): User's first name.
  - `last_name` (VARCHAR(255)): User's last name.
  - `address` (VARCHAR(255)): User's address (for textile collection).
  - `notification_time` (TIME, DEFAULT '20:00'): Preferred notification time.
  - `notifications_enabled` (BOOLEAN, DEFAULT TRUE): Flag to enable/disable notifications.
  - `created_at` (TIMESTAMP, DEFAULT NOW()): Record creation timestamp.
  - `updated_at` (TIMESTAMP, DEFAULT NOW()): Record last update timestamp.

## Installation and Running

This project is designed to be run using Docker and Docker Compose.

### Prerequisites

  - Docker
  - Docker Compose

### Steps

1.  **Clone the repository** (or download the files).

2.  **Ensure all provided files** are present in the correct directory structure.

3.  **Create the `.env` file:** Create a file named `.env` in the project's root directory and populate it with the necessary environment variables as described in the "Configuration" section.

4.  **Start the services using Docker Compose:** Open a terminal in the project's root directory and run:

    ```bash
    docker-compose up --build
    ```

    This command will:

      - Build the image for the bot application
      - Start the bot container
      - Start the PostgreSQL database container
      - Start an Adminer container for easy database management

### Service Access

  - The bot application will be accessible via Telegram.
  - The PostgreSQL database will be exposed on port 5432.
  - Adminer will be accessible at http://localhost:8080.

<!-- end list -->

5.  **Interact with the Bot:** Find your bot on Telegram (using the token you provided) and start interacting with the commands listed above.

## File Structure

```
.
├── config/
│   └── waste_schedules.py
├── commands/
│   └── handlers.py
├── service/
│   └── schedule.py
├── tests/
│   ├── test_db_manager.py
│   ├── test_handlers.py
│   └── test_schedule.py
├── .env
├── .gitignore
├── db_manager.py
├── docker-compose.yaml
├── Dockerfile
├── LICENSE
├── main.py
├── requirements.txt
└── README.md
```

## Dependencies

The main Python dependencies are listed in `requirements.txt` and include:

  - **python-telegram-bot:** To interact with the Telegram API.
  - **psycopg2-binary:** PostgreSQL adapter for Python.
  - **python-dotenv:** To load environment variables from a `.env` file.
  - **pytz:** For timezone handling.
  - **APScheduler:** For job scheduling (like notifications).
