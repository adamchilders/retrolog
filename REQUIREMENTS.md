# RetroLog Application Requirements

## Software Requirements

*   **Docker**: The application is fully containerized using Docker and Docker Compose. You must have Docker installed on your system to run it.
*   **Web Browser**: A modern web browser is required to access the application's frontend.

## API Keys

*   **Google Gemini API Key**: To power the AI insights and adaptive questioning, you must provide a Google Gemini API key.

## Running the Application

1.  **Clone the Repository**: `git clone <repository_url>`
2.  **Environment Variables**: Create a `.env` file in the `retrolog/backend` directory. Add your Gemini API key to this file:
    ```
    GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    ```
3.  **Build and Run**: Navigate to the root `retrolog` directory and run the following command:
    ```bash
    docker-compose up --build
    ```
4.  **Access**:
    *   Frontend will be available at `http://localhost:3000`.
    *   Backend API will be available at `http://localhost:8000`.

## Hardware Recommendations

*   **CPU**: 2 cores or more.
*   **RAM**: A minimum of 4GB of RAM is recommended to run the Docker containers smoothly.
