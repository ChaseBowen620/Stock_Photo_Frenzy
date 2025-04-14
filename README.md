# Stock Photo Frenzy

A fun web game where players guess the titles of stock photos! Built with React (Vite) frontend and Django backend.

## Project Structure

- `Front_End_SPF/`: React frontend built with Vite
- `Back_End_SPF/`: Django backend API

## Setup Instructions

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd Front_End_SPF
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file with:
   ```
   VITE_API_URL=http://localhost:8000
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd Back_End_SPF
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with:
   ```
   DJANGO_SECRET_KEY=your-secret-key
   UNSPLASH_API_KEY=your-unsplash-api-key
   DEBUG=True
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Game Features

- Random stock photo selection
- Search-based photo selection
- Multiple difficulty levels
- Configurable time limits
- Point scoring system
- Word guessing mechanics

## Deployment

The frontend is deployed on Vercel and the backend on a suitable Python hosting platform. Make sure to:

1. Set up proper environment variables
2. Configure CORS settings
3. Set DEBUG=False in production
4. Use proper security measures

## Contributing

Feel free to submit issues and pull requests!

## License

MIT License