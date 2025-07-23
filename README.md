# AI StoryWeaver 

AI StoryWeaver is a full-stack web application where users interact with an AI through a chat-like interface to generate a **10-page illustrated story**. The system intelligently asks follow-up questions based on missing story details and uses text and image generation models to craft an engaging, country-themed (Indian) story—streamed page by page.



## Folder Structure

```
AI STORY/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── db.sql
│   │   ├── extensions.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── story_generator.py
│   │   └── utils.py
│   ├── static/images
│   ├── .env
│   ├── requirements.txt
│   └── run.py
│
├── frontend/ai-story-weaver/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   │   ├── script.png
│   │   │   └── styles.css
│   │   ├── components/
│   │   │   ├── Auth/
│   │   │   ├── Chat/
│   │   │   ├── Dashboard/
│   │   │   └── StoryViewer/
│   │   ├── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── .gitignore
│   
```

## Screenshots
<img width="1915" height="1011" alt="Screenshot 2025-07-23 233615" src="https://github.com/user-attachments/assets/8f93ecd8-9ba7-40b9-ad08-374e5415fb34" />
<img width="1919" height="1014" alt="Screenshot 2025-07-23 233805" src="https://github.com/user-attachments/assets/c377da1e-b365-47ae-842e-778da7962c40" />
<img width="1919" height="1015" alt="Screenshot 2025-07-23 234134" src="https://github.com/user-attachments/assets/7eac0a35-2eff-4511-9f39-3aa95542e7c1" />
<img width="1919" height="1020" alt="Screenshot 2025-07-23 233909" src="https://github.com/user-attachments/assets/de96e00b-fa5a-493c-8f95-92582b46a906" />
<img width="1919" height="1023" alt="Screenshot 2025-07-23 233847" src="https://github.com/user-attachments/assets/b63a2554-ddc9-430b-9ab7-d36e19626343" />




## Features

- User authentication (register/login)
- Country theme: India
- Chat interface with smart AI-driven follow-up questions
- Automatically generates a 10-page story with images 
- Previous stories viewer with text & image layout
- Download full story as PDF




## Tech Stack

| Layer       | Technology          |
|-------------|---------------------|
| Frontend    | React.js, CSS |
| Backend     | Python Flask         |
| Database    | PostgreSQL           |
| LLM Models   | LLaMA 3 (via Groq API), Stable Diffusion XL (via Hugging Face API) |




## Database Schema (PostgreSQL)

```sql
-- users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- stories table
CREATE TABLE stories (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200),
    user_input TEXT NOT NULL,
    country_theme VARCHAR(100) DEFAULT 'India',
    status VARCHAR(50) DEFAULT 'gathering_info',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- story_pages table
CREATE TABLE story_pages (
    id SERIAL PRIMARY KEY,
    story_id INTEGER NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    page_no INTEGER NOT NULL,
    text TEXT NOT NULL,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```




##  Getting Started

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file inside `backend/`:

```env

DATABASE_URL=postgresql+pg8000://<username>:<password>@<host>:<port>/<database_name>
SECRET_KEY=<your_flask_secret_key>
JWT_SECRET_KEY=<your_jwt_secret_key>
GROQ_API_KEY=<your_groq_api_key>
HUGGINGFACE_API_KEY=<your_huggingface_api_key>
FRONTEND_URL=http://localhost:5173

```
```
Then run the backend:

```bash
python run.py
```



### Frontend Setup

```bash
cd frontend/ai-story-weaver
npm install
npm run dev
```



## API Endpoints

| Method | Endpoint                | Description                            |
|--------|-------------------------|----------------------------------------|
| POST   | `/api/auth/register`    | Register new user                      |
| POST   | `/api/auth/login`       | User login                             |
| POST   | `/api/chat`             | Accepts user message and responds      |
| POST   | `/api/story/generate`   | Trigger story and image generation     |
| GET    | `/api/story/<story_id>` | Fetch story and its pages              |





## Testing Tips

- Register and login through the frontend
- Try chatting with incomplete prompts — see AI follow-up
- Wait for full 10-page illustrated story to stream live
- Refresh or revisit Story Viewer for saved stories






