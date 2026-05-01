"""
MediTrack - Hospital Patient Records API
Hospital: Meridian Health Systems
A simple Flask REST API using in-memory storage (no database required).
Designed as a DevOps training exercise.
"""

from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

# ---------------------------------------------------------------------------
# In-memory patient store (pre-populated with 3 sample records)
# ---------------------------------------------------------------------------
patients = [
    {
        "id": 1,
        "name": "Alice Johnson",
        "age": 45,
        "gender": "Female",
        "diagnosis": "Hypertension",
        "ward": "Cardiology",
        "admitted_on": "2026-03-20"
    },
    {
        "id": 2,
        "name": "Brian Carter",
        "age": 62,
        "gender": "Male",
        "diagnosis": "Type 2 Diabetes",
        "ward": "Endocrinology",
        "admitted_on": "2026-03-22"
    },
    {
        "id": 3,
        "name": "Carmen Reyes",
        "age": 30,
        "gender": "Female",
        "diagnosis": "Appendicitis",
        "ward": "Surgery",
        "admitted_on": "2026-03-27"
    }
]

# Auto-incrementing ID counter for new patients
next_id = 4

# ---------------------------------------------------------------------------
# Dashboard HTML (fully self-contained — no external CSS/JS dependencies)
# ---------------------------------------------------------------------------
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>MediTrack Dashboard</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Arial, sans-serif; background: #f4f6f9; color: #333; }
    header {
      background: #0a2342; color: #fff; padding: 18px 32px;
      display: flex; align-items: center; justify-content: space-between;
    }
    header h1 { font-size: 1.4rem; font-weight: 700; }
    header p  { font-size: 0.85rem; opacity: 0.75; margin-top: 2px; }
    .badge {
      background: #28a745; color: #fff; padding: 5px 14px;
      border-radius: 20px; font-size: 0.8rem; font-weight: 600;
    }
    main { max-width: 1100px; margin: 36px auto; padding: 0 24px; }
    .summary { font-size: 0.95rem; color: #555; margin-bottom: 20px; }
    .summary span { font-weight: 700; color: #0a2342; font-size: 1.1rem; }
    .table-wrapper {
      background: #fff; border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08); overflow: hidden;
    }
    table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
    thead { background: #0a2342; color: #fff; }
    thead th { padding: 13px 16px; text-align: left; font-weight: 600; }
    tbody tr { border-bottom: 1px solid #eef0f3; }
    tbody tr:last-child { border-bottom: none; }
    tbody tr:hover { background: #f0f4ff; }
    tbody td { padding: 12px 16px; }
    .empty-state { text-align: center; padding: 48px 16px; color: #888; }
    .loading    { text-align: center; padding: 40px; color: #aaa; }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>MediTrack</h1>
      <p>Meridian Health Systems</p>
    </div>
    <span class="badge">&#x25CF; System Online</span>
  </header>
  <main>
    <p class="summary">Total patients: <span id="patient-count">...</span></p>
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>ID</th><th>Name</th><th>Age</th><th>Gender</th>
            <th>Diagnosis</th><th>Ward</th><th>Admitted On</th>
          </tr>
        </thead>
        <tbody id="patient-table-body">
          <tr><td colspan="7" class="loading">Loading patient records...</td></tr>
        </tbody>
      </table>
    </div>
  </main>
  <script>
    async function loadPatients() {
      const tbody    = document.getElementById('patient-table-body');
      const countEl  = document.getElementById('patient-count');
      try {
        const res      = await fetch('/patients');
        const patients = await res.json();
        countEl.textContent = patients.length;
        if (patients.length === 0) {
          tbody.innerHTML = '<tr><td colspan="7" class="empty-state">No patient records found</td></tr>';
          return;
        }
        tbody.innerHTML = patients.map(p => `
          <tr>
            <td>${p.id}</td><td>${p.name}</td><td>${p.age}</td>
            <td>${p.gender}</td><td>${p.diagnosis}</td>
            <td>${p.ward}</td><td>${p.admitted_on}</td>
          </tr>`).join('');
      } catch (err) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state">Failed to load patient records.</td></tr>';
        countEl.textContent = '0';
      }
    }
    loadPatients();
  </script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def find_patient(patient_id):
    """Return the patient dict with the given id, or None."""
    return next((p for p in patients if p["id"] == patient_id), None)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """HTML status page showing app name, hospital, status, and patient count."""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>MediTrack Status</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f6f9;
           display: flex; justify-content: center; align-items: center;
           height: 100vh; margin: 0; }}
    .card {{ background: #fff; border-radius: 10px; padding: 40px 56px;
             box-shadow: 0 4px 16px rgba(0,0,0,0.10); text-align: center; }}
    h1 {{ color: #0a2342; margin-bottom: 6px; }}
    .hospital {{ color: #555; font-size: 0.95rem; margin-bottom: 24px; }}
    .status {{ display: inline-block; background: #28a745; color: #fff;
               padding: 6px 18px; border-radius: 20px; font-size: 0.9rem; }}
    .patients {{ margin-top: 20px; font-size: 1rem; color: #333; }}
    .patients span {{ font-weight: 700; color: #0a2342; }}
    a {{ display: inline-block; margin-top: 20px; color: #0a2342; font-size: 0.9rem; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>MediTrack</h1>
    <p class="hospital">Meridian Health Systems</p>
    <span class="status">&#x25CF; Running</span>
    <p class="patients">Patients in memory: <span>{len(patients)}</span></p>
    <a href="/dashboard">Open Dashboard &rarr;</a>
  </div>
</body>
</html>"""
    return html


@app.route("/health")
def health():
    """Health check — returns JSON status for monitoring tools."""
    return jsonify({"status": "healthy", "service": "meditrack-api"}), 200


@app.route("/dashboard")
def dashboard():
    """Serve the self-contained patient dashboard."""
    return render_template_string(DASHBOARD_HTML)


@app.route("/patients", methods=["GET"])
def get_patients():
    """Return all patient records as a JSON list."""
    return jsonify(patients), 200


@app.route("/patients/<int:patient_id>", methods=["GET"])
def get_patient(patient_id):
    """Return a single patient by ID, or 404 if not found."""
    patient = find_patient(patient_id)
    if patient is None:
        return jsonify({"error": f"Patient with id {patient_id} not found"}), 404
    return jsonify(patient), 200


@app.route("/patients", methods=["POST"])
def create_patient():
    """Create a new patient. Expects JSON body with all required fields."""
    global next_id
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    required_fields = ["name", "age", "gender", "diagnosis", "ward", "admitted_on"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    new_patient = {
        "id": next_id,
        "name": data["name"],
        "age": data["age"],
        "gender": data["gender"],
        "diagnosis": data["diagnosis"],
        "ward": data["ward"],
        "admitted_on": data["admitted_on"]
    }
    patients.append(new_patient)
    next_id += 1
    return jsonify(new_patient), 201


@app.route("/patients/<int:patient_id>", methods=["PUT"])
def update_patient(patient_id):
    """Update an existing patient record. Only provided fields are changed."""
    patient = find_patient(patient_id)
    if patient is None:
        return jsonify({"error": f"Patient with id {patient_id} not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    for field in ["name", "age", "gender", "diagnosis", "ward", "admitted_on"]:
        if field in data:
            patient[field] = data[field]

    return jsonify(patient), 200


@app.route("/patients/<int:patient_id>", methods=["DELETE"])
def delete_patient(patient_id):
    """Delete a patient by ID."""
    patient = find_patient(patient_id)
    if patient is None:
        return jsonify({"error": f"Patient with id {patient_id} not found"}), 404

    patients.remove(patient)
    return jsonify({"message": f"Patient with id {patient_id} successfully deleted"}), 200


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # 0.0.0.0 makes the server accessible inside Docker containers
    app.run(host="0.0.0.0", port=5000, debug=True)
