# 📈 FinTech Stock Forecasting Dashboard

A full-stack **financial analytics and forecasting platform** built using **React + TypeScript**, **FastAPI**, **Docker**, and **Render**.  
The dashboard provides ARIMA forecasting, ACF/PACF analysis, historical charts, and statistical diagnostics for any publicly traded stock.

---

## 🚀 Live Demo

### **Frontend:** https://fintech-43ngfa730-tush05tgsinghs-projects.vercel.app/
### **Backend API:** https://fintech-rf8s.onrender.com/api/health

---

## 🧠 Features

### 📊 Stock Forecasting
- ARIMA-based future price prediction  
- Prices & returns ACF/PACF  
- Stationarity test (ADF)  
- Forecast with confidence intervals  
- Historical stock analysis using Yahoo Finance  

### 🖥️ Frontend (React + TS)
- Vite development environment  
- Recharts for interactive data visualization  
- Dropdown-based UI for Forecast / Prices / ACF-PACF  
- API-integrated modular components  
- Fully typed data models (TypeScript)

### ⚙️ Backend (FastAPI)
- Endpoints:
  - `/api/forecast`
  - `/api/prices`
  - `/api/acf-pacf`
  - `/api/health`
- Uses:
  - Pandas  
  - NumPy  
  - Statsmodels (ARIMA, ACF, PACF, ADF)  
  - yfinance  
- Dockerized and deployed on Render

---

## 🛠️ Tech Stack

### **Frontend**
- React  
- TypeScript  
- Vite  
- Recharts  
- Axios  

### **Backend**
- FastAPI  
- Uvicorn  
- Python 3.11  
- Statsmodels  
- Pandas / NumPy  
- yfinance  

### **Infrastructure**
- Docker  
- Render (Backend)  
- Vercel or Render (Frontend)

---

## 📁 Project Structure

Fintech/
│
├── Phase_1/
│ ├── projects/
│ │ ├── week_2/
│ │ │ ├── ts-stock-dashboard/
│ │ │ │ ├── ts-stock-dashboard/
│ │ │ │ │ ├── frontend/
│ │ │ │ │ ├── backend/
│ │ │ │ │ │ ├── app/
│ │ │ │ │ │ │ └── main.py
│ │ │ │ │ │ ├── requirements.txt
│ │ │ │ │ │ └── Dockerfile


---

## 📡 API Endpoints

### 🟢 Health Check  
https://fintech-1-dygz.onrender.com/api/health

### Stock Forecast
https://fintech-1-dygz.onrender.com/api/data?ticker=${ticker}&start=${start}&end=${end}

## Running Locally

#### Clone the repository
```
git clone https://github.com/tush05tgsingh/Fintech
```
#### Backend Setup (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend Setup (React + TypeScript)
```bash
cd frontend
npm install
npm run dev
```


# 👩‍💻 Author

Tushita Singh
ML + Software Engineer
GitHub: https://github.com/tush05tgsingh

LinkedIn: https://www.linkedin.com/in/tushita-singh/