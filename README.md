# 🛡️ TruthLens – Fake News Detection System

# PROJECT OVERVIEW
TruthLens is an AI-powered web application that analyzes news articles and headlines to determine whether they are Real or Fake using a trained Machine Learning model. It combines a modern frontend interface with a FastAPI backend to deliver real-time predictions.

# LIVE DEMO
Frontend (GitHub Pages):  
https://thamindu16.github.io/Fake-News-Detetction-System-Project/ 

Backend API (Render):  
https://fake-news-api-5lv4.onrender.com  

API Docs (Swagger):  
https://fake-news-api-5lv4.onrender.com/docs  

# FEATURES 
- Analyze news text or headlines instantly  
- Machine Learning-based classification (Real vs Fake)  
- Confidence score visualization  
- Linguistic indicators (sensationalism, objectivity, emotional tone)  
- FastAPI backend for real-time predictions  
- Fully deployed frontend + backend  

# TECH STACK
Frontend: HTML5, CSS3, JavaScript  
Backend: FastAPI, Scikit-learn, Pickle  
Deployment: GitHub Pages (frontend), Render (backend)  

# PROJECT STRUCTURE
Fake-News-Detection-System-Project/  
│  
├── index.html  
├── static/  
│   ├── styles.css  
│   └── script.js  
│  
├── app.py  
├── model.pkl  
├── vectorizer.pkl  
├── requirements.txt  
└── README.md  

# HOW IT WORKS
User enters news text → Frontend sends POST request → Backend processes text using TF-IDF vectorizer → ML model predicts → Backend returns prediction + confidence → Frontend displays result visually  

# API 
POST /predict  

Request:
{
  "text": "Your news article here"
}

Response:
{
  "prediction": "fake",
  "confidence": 0.87
}
 
# DEPLOYMENT
Frontend hosted on GitHub Pages  
Backend hosted on Render with CORS enabled  

# CHALLENGES 
Handled CORS issues between frontend and backend  
Fixed static file serving in FastAPI  
Resolved API endpoint mismatches  
Debugged deployment issues on Render and GitHub Pages  

# AUTHOR
Thamindu Kavinda  
https://github.com/Thamindu16  

# SUPPORT 
If you like this project, consider starring the repository and sharing it  

# LICENSE 
This project is created for educational purposes
