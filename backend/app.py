from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.getenv('DB_PATH', 'attendance.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

db = SQLAlchemy(app)
CORS(app)

# ========== DATABASE MODELS ==========
class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default="student")
    template_pos = db.Column(db.Integer, unique=True, nullable=False)
    date_enrolled = db.Column(db.DateTime, default=datetime.utcnow)

class Attendance(db.Model):
    __tablename__ = "attendance"
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    scan_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="present")
    course_code = db.Column(db.String(20))
    synced = db.Column(db.Integer, default=0)

# ========== HELPER FUNCTIONS ==========
def get_sensor():
    """Initialize fingerprint sensor"""
    from pyfingerprint.pyfingerprint import PyFingerprint
    try:
        port = os.getenv('COM_PORT', 'COM3')
        baud = int(os.getenv('BAUD_RATE', '57600'))
        sensor = PyFingerprint(port, baud, 0xFFFFFFFF, 0x00000000)
        if not sensor.verifyPassword():
            raise ValueError("Sensor password incorrect")
        return sensor
    except Exception as e:
        raise Exception(f"Sensor init failed: {str(e)}")

# ========== API ROUTES ==========

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if backend is running"""
    return jsonify({"status": "ok", "message": "Backend is running"}), 200

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all enrolled users"""
    try:
        users = User.query.all()
        return jsonify({
            "success": True,
            "users": [{
                "user_id": u.user_id,
                "full_name": u.full_name,
                "role": u.role,
                "template_pos": u.template_pos,
                "date_enrolled": u.date_enrolled.isoformat()
            } for u in users]
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/enroll', methods=['POST'])
def enroll_fingerprint():
    """Enroll a new fingerprint"""
    try:
        data = request.json
        full_name = data.get('full_name')
        role = data.get('role', 'student')
        
        if not full_name:
            return jsonify({"success": False, "error": "Name required"}), 400

        sensor = get_sensor()
        
        # Read first image
        print("✋ Waiting for finger...")
        attempts = 0
        while not sensor.readImage() and attempts < 50:
            attempts += 1
        
        if attempts >= 50:
            return jsonify({"success": False, "error": "Timeout waiting for finger"}), 408
        
        sensor.convertImage(0x01)
        
        # Check if already enrolled
        result = sensor.searchTemplate()
        if result[0] >= 0:
            return jsonify({
                "success": False, 
                "error": f"Fingerprint already enrolled at position {result[0]}"
            }), 409
        
        # Read second image
        print("🔄 Remove finger and place again...")
        while sensor.readImage():
            pass
        
        attempts = 0
        while not sensor.readImage() and attempts < 50:
            attempts += 1
            
        if attempts >= 50:
            return jsonify({"success": False, "error": "Timeout on second scan"}), 408
        
        sensor.convertImage(0x02)
        sensor.createTemplate()
        template_pos = sensor.storeTemplate()
        
        # Save to database
        new_user = User(
            full_name=full_name,
            role=role,
            template_pos=template_pos
        )
        db.session.add(new_user)
        db.session.commit()
        
        print(f"✅ Enrolled: {full_name} at position {template_pos}")
        return jsonify({
            "success": True,
            "message": "Fingerprint enrolled successfully",
            "user_id": new_user.user_id,
            "template_pos": template_pos,
            "full_name": full_name
        }), 201
        
    except Exception as e:
        print(f"❌ Enrollment error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/identify', methods=['POST'])
def identify_fingerprint():
    """Identify a fingerprint and log attendance"""
    try:
        data = request.json
        course_code = data.get('course_code', 'N/A')
        
        sensor = get_sensor()
        
        print("👆 Waiting for finger to identify...")
        attempts = 0
        while not sensor.readImage() and attempts < 50:
            attempts += 1
            
        if attempts >= 50:
            return jsonify({"success": False, "error": "Timeout waiting for finger"}), 408
        
        sensor.convertImage(0x01)
        result = sensor.searchTemplate()
        template_pos = result[0]
        accuracy = result[1]
        
        if template_pos < 0:
            print("❌ Fingerprint not recognized")
            return jsonify({
                "success": False, 
                "error": "Fingerprint not recognized"
            }), 404
        
        # Find user by template position
        user = User.query.filter_by(template_pos=template_pos).first()
        if not user:
            return jsonify({
                "success": False,
                "error": f"No user found for template position {template_pos}"
            }), 404
        
        # Log attendance
        attendance_log = Attendance(
            user_id=user.user_id,
            course_code=course_code,
            status="present"
        )
        db.session.add(attendance_log)
        db.session.commit()
        
        print(f"✅ Attendance logged: {user.full_name}")
        return jsonify({
            "success": True,
            "message": "Attendance logged",
            "user": {
                "user_id": user.user_id,
                "full_name": user.full_name,
                "role": user.role
            },
            "accuracy": accuracy,
            "scan_time": attendance_log.scan_time.isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Identification error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    """Get all attendance records"""
    try:
        records = db.session.query(Attendance, User).join(
            User, Attendance.user_id == User.user_id
        ).all()
        
        return jsonify({
            "success": True,
            "records": [{
                "log_id": a.log_id,
                "user_id": a.user_id,
                "full_name": u.full_name,
                "scan_time": a.scan_time.isoformat(),
                "status": a.status,
                "course_code": a.course_code
            } for a, u in records]
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/attendance/<int:user_id>', methods=['GET'])
def get_user_attendance(user_id):
    """Get attendance for specific user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        records = Attendance.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            "success": True,
            "user": {
                "user_id": user.user_id,
                "full_name": user.full_name,
                "role": user.role
            },
            "records": [{
                "log_id": r.log_id,
                "scan_time": r.scan_time.isoformat(),
                "status": r.status,
                "course_code": r.course_code
            } for r in records]
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/sensor/test', methods=['GET'])
def test_sensor():
    """Test if sensor is connected and working"""
    try:
        sensor = get_sensor()
        templates = sensor.getTemplateCount()
        storage = sensor.getStorageCapacity()
        
        return jsonify({
            "success": True,
            "message": "Sensor connected successfully",
            "templates_stored": templates,
            "storage_capacity": storage
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ========== ERROR HANDLERS ==========
@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "error": "Internal server error"}), 500

# ========== RUN SERVER ==========
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    print("\n" + "="*50)
    print("🚀 R307 Fingerprint Attendance Backend")
    print("="*50)
    print("📍 Server: http://localhost:5000")
    print("🔗 Health: http://localhost:5000/api/health")
    print("👥 Users: http://localhost:5000/api/users")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)