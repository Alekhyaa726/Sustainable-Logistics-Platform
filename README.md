# Sustainable Logistics Platform

## 📌 Project Overview
The logistics industry significantly contributes to global carbon emissions. This project introduces a **dual-objective routing engine** that calculates both the **'Fastest Route'** (Red) and a fuel-efficient **'Green Route'** (Green).

By quantifying the trade-off between time and CO2 emissions, this system empowers logistics managers to optimize their supply chains for sustainability without compromising delivery efficiency.

## 🚀 Key Features
* **Dual-Objective Routing:** Dijkstra/A* algorithms for Time vs. Emissions.
* **Real-World Data:** Uses **OpenStreetMap (OSMnx)** for accurate road networks.
* **Sustainability Metrics:** Calculates **CO2 savings** and **Fuel Costs** per trip.
* **Interactive Dashboard:** Live map visualization using React & Leaflet.

## 🛠️ Tech Stack
* **Frontend:** React.js, Leaflet Maps
* **Backend:** Python (FastAPI), NetworkX, OSMnx
* **Database:** PostgreSQL
* **Deployment:** Docker & Docker Compose

## ⚙️ How to Run
1.  **Clone the repo:**
    ```bash
    git clone [https://github.com/Alekhyaa726/Sustainable-Logistics-Platform.git](https://github.com/Alekhyaa726/Sustainable-Logistics-Platform.git)
    cd Sustainable-Logistics-Platform
    ```
2.  **Run with Docker:**
    ```bash
    docker-compose up --build
    ```
3.  **Access:**
    * Frontend: http://localhost:3000
    * Backend: http://localhost:8000/docs

---
