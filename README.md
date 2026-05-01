# MediTrack — Hospital Patient Records API

A lightweight REST API for managing hospital patient records, built with Python and Flask.
Uses in-memory storage (no database required) — ideal for DevOps training and containerisation exercises.

**Hospital:** Meridian Health Systems

---

## Running Locally

**1. Install dependencies**

```bash
pip install -r requirements.txt
```

**2. Start the server**

```bash
python app.py
```

The API will be available at `http://localhost:5000`.

---

## Running with Docker

**Build the image**

```bash
docker build -t meditrack .
```

**Run the container**

```bash
docker run -p 5000:5000 meditrack
```

The API will be available at `http://localhost:5000`.

---

## Running Tests

```bash
pytest test_app.py -v
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | HTML status page (app name, hospital, status, patient count) |
| GET | `/health` | JSON health check |
| GET | `/dashboard` | Interactive patient dashboard (HTML) |
| GET | `/patients` | List all patient records |
| GET | `/patients/<id>` | Get a single patient by ID |
| POST | `/patients` | Create a new patient record |
| PUT | `/patients/<id>` | Update an existing patient record |
| DELETE | `/patients/<id>` | Delete a patient record |

---

## Patient Record Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Auto-generated unique identifier |
| `name` | string | Patient full name |
| `age` | integer | Patient age |
| `gender` | string | e.g. `"Male"`, `"Female"`, `"Other"` |
| `diagnosis` | string | Medical diagnosis |
| `ward` | string | Hospital ward name |
| `admitted_on` | string | Admission date (`YYYY-MM-DD`) |

---

## Example Requests

**Create a patient**
```bash
curl -X POST http://localhost:5000/patients \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane Smith","age":38,"gender":"Female","diagnosis":"Migraine","ward":"Neurology","admitted_on":"2026-03-28"}'
```

**Update a patient**
```bash
curl -X PUT http://localhost:5000/patients/1 \
  -H "Content-Type: application/json" \
  -d '{"diagnosis":"Hypertension Stage 2"}'
```

**Delete a patient**
```bash
curl -X DELETE http://localhost:5000/patients/1
```

---
## Architecture                                                                            
Infrastructure: Provisioned using AWS CloudFormation (Jenkins EC2 server + VPC + EKS Cluster)
CI/CD: GitHub → Jenkins Pipeline (test, build Docker image, push to Docker Hub)
Deployment: Docker container deployed on Amazon EKS with 3 replicas and LoadBalancer service
Monitoring: Prometheus + Grafana for cluster and pod metrics
The pipeline automatically builds and deploys the app whenever code
> Note: All data is stored in memory. It resets every time the server restarts. This is intentional for training purposes.
