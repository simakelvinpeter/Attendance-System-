from flask import jsonify, request
from datetime import datetime

class AttendanceService:

    @staticmethod
    def get_attendance():
        # Lazy import to avoid circular import
        from app import Attendance, User

        records = Attendance.query.order_by(Attendance.scan_time.desc()).all()
        out = []
        for r in records:
            user = User.query.get(r.user_id)
            out.append({
                "log_id": r.log_id,
                "user_id": r.user_id,
                "full_name": user.full_name if user else None,
                "scan_time": r.scan_time.isoformat() if r.scan_time else None,
                "status": r.status,
                "course_code": r.course_code,
                "synced": bool(r.synced)
            })
        return jsonify({"success": True, "data": out}), 200

    @staticmethod
    def mark_attendance(data):
        from app import db, Attendance, User
        try:
            if not data:
                return jsonify({"success": False, "error": "JSON body required"}), 400

            user_id = data.get("user_id") or data.get("student_id")
            if not user_id:
                return jsonify({"success": False, "error": "user_id (or student_id) required"}), 400

            # allow string ids
            try:
                user_id_int = int(user_id)
            except Exception:
                return jsonify({"success": False, "error": "user_id must be an integer"}), 400

            user = User.query.get(user_id_int)
            if not user:
                return jsonify({"success": False, "error": "user not found"}), 404

            att = Attendance(
                user_id=user.user_id,
                scan_time=datetime.utcnow(),
                status=data.get("status", "present"),
                course_code=data.get("course_code")
            )
            db.session.add(att)
            db.session.commit()
            return jsonify({"success": True, "message": "Attendance marked", "log_id": att.log_id}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500

    @staticmethod
    def get_users():
        from app import User
        users = User.query.order_by(User.full_name).all()
        data = [
            {
                "user_id": u.user_id,
                "full_name": u.full_name,
                "role": u.role,
                "template_pos": u.template_pos,
                "date_enrolled": u.date_enrolled.isoformat() if u.date_enrolled else None
            } for u in users
        ]
        return jsonify({"success": True, "data": data}), 200

    @staticmethod
    def enroll_fingerprint(student_id):
        from app import db, User
        try:
            if student_id is None:
                return jsonify({"success": False, "error": "student_id required"}), 400

            try:
                uid = int(student_id)
            except Exception:
                return jsonify({"success": False, "error": "student_id must be integer"}), 400

            user = User.query.get(uid)
            if not user:
                return jsonify({"success": False, "error": "user not found"}), 404

            # Placeholder: simulate enrollment by assigning a template_pos if missing
            if not user.template_pos:
                max_pos = db.session.query(db.func.max(User.template_pos)).scalar() or 0
                user.template_pos = max_pos + 1
                db.session.commit()

            return jsonify({
                "success": True,
                "message": "Enrollment simulated (sensor integration required for real enroll)",
                "user_id": user.user_id,
                "template_pos": user.template_pos
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500

    @staticmethod
    def identify_fingerprint():
        # If client POSTs {"user_id": <id>} allow testing without sensor.
        data = request.get_json(silent=True) or {}
        if data.get("user_id"):
            return AttendanceService.mark_attendance(data)
        return jsonify({
            "success": False,
            "error": "Fingerprint sensor not integrated. To test, POST JSON {\"user_id\": <id>} to this endpoint."
        }), 501
