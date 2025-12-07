# Coding Exercise: Production Plan Parser

## Goal

The goal of this coding exercise is to write an AI-based parser that can

1. Extract data from unstructured production planning sheets
2. Store the extracted data in MongoDB
3. Display the data on a dashboard as production line items

The extraction needs to be generic because the production sheets can be generic in real life.

## Data Files

The sample Excel files in `data` directory (`tna-uno.xlsx`, `tna-dos.xlsx`, `tna-tres.xlsx`) contain production planning and tracking data.

- **Sheets contain**: Production order information with timeline tracking across different manufacturing stages
- **Rows represent**: Individual production orders or order line items, with some files grouping multiple color variants under the same style
- **Columns represent**: Order attributes (identifiers, specifications, quantities) and milestone dates for different production stages (fabric, cutting, processing, finishing etc.)

Each file tracks the progression of orders through various manufacturing checkpoints with planned dates and quantities at each stage.

## Project Setup

### Prerequisites
- Docker and Docker Compose installed
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd coding-exercise-dos
   ```

2. **Start all services with Docker Compose**
   ```bash
   docker-compose up --build
   ```

   This will start:
   - MongoDB on port 27017
   - FastAPI backend on http://localhost:8000
   - React frontend on http://localhost:3000

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Development

> **Note**: The Docker setup has been tested and should work out of the box. If you encounter any issues, please ensure Docker and Docker Compose are properly installed and configured on your system.

#### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### Frontend (React)
```bash
cd frontend
npm install
npm start
```

#### MongoDB
MongoDB runs in Docker with:
- Username: `admin`
- Password: `pass1234`
- Database: `production`
- Connection string: `mongodb://admin:pass1234@localhost:27017/production?authSource=admin`

### Project Structure

```
coding-exercise-dos/
├── backend/              # FastAPI backend
│   ├── main.py           # Main application file
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUploader.js
│   │   │   ├── ProductionCard.js
│   │   │   └── ProductionDashboard.js
│   │   ├── App.js
│   │   └── index.js
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── data/
│   ├── tna-uno.xlsx      # Sample data file 1
│   ├── tna-dos.xlsx      # Sample data file 2
│   └── tna-tres.xlsx     # Sample data file 3
├── docker-compose.yml
└── README.md
```

### API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/upload` - Upload Excel file
- `GET /api/production-items` - Get all production items
- `GET /api/production-items/{id}` - Get specific item
- `DELETE /api/production-items/{id}` - Delete item

## Your Mission

1. Implement AI-based parser logic in backend
2. Add data models and MongoDB schemas
3. Connect file upload to parsing pipeline

A set of 3 more Excel sheets have been reserved as a test set on which the evaluation will be performed.

## Submission Guidelines

Please follow these guidelines for submitting your solution:

1. Clone the repository to your local machine
2. Work on the assignment in your personal GitHub account - create a new repository in your account
3. Submit the link to your public repository for evaluation

### Important Notes

- ❌ DO NOT raise any Pull Requests to the original repository
- ❌ DO NOT FORK the repository - clone and create a new repo instead
- ✅ COMMIT periodically to show your progress and thought process
- ✅ Keep your repository PUBLIC for evaluation

### Why These Guidelines?

- Creating your own repository maintains fairness in evaluation across all submissions
- Regular commits help us understand your development approach and problem-solving process
- Public repositories ensure transparent and consistent evaluation
