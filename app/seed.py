"""Database seeder: populates the database with initial data matching frontend mock-data shapes."""

import asyncio
import json
import uuid

from app.database import async_session_factory, engine, Base
from app.models import *  # noqa: F403 - import all models so they register with Base
from app.services.auth_service import hash_password


async def seed():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        # ─── Users ───
        password = hash_password("admin123")
        users = [
            User(
                id="admin-1", email="admin@campusorbit.edu", name="Dr. Rajesh Kumar",
                hashed_password=password, role="admin", avatar="👨‍💼",
                department="Administration", phone="+91-9876543210", join_date="2020-01-15",
            ),
            User(
                id="teacher-1", email="teacher@campusorbit.edu", name="Prof. Priya Sharma",
                hashed_password=password, role="teacher", avatar="👩‍🏫",
                department="Computer Science", phone="+91-9876543211", join_date="2021-06-10",
                specialization="Data Structures & Algorithms",
                qualifications="M.Tech (IIT Delhi), B.Tech (NIT Trichy)", experience="8 years",
            ),
            User(
                id="teacher-2", email="prof.amit@campusorbit.edu", name="Prof. Amit Kumar",
                hashed_password=password, role="teacher", avatar="👨‍🏫",
                department="Computer Science", phone="+91-9876543216", join_date="2020-03-20",
                specialization="Networks",
            ),
            User(
                id="student-1", email="student@campusorbit.edu", name="Arjun Patel",
                hashed_password=password, role="student", avatar="👨‍🎓",
                department="B.Tech CSE", phone="+91-9876543212", join_date="2023-08-01",
                roll_no="CSE-2023-001", cgpa=8.45,
                parent_name="Vikram Patel", parent_phone="+91-9876543220",
            ),
            User(
                id="student-2", email="priya.sharma@campusorbit.edu", name="Priya Sharma",
                hashed_password=password, role="student", avatar="👩‍🎓",
                department="B.Tech ECE", phone="+91-9876543217", join_date="2023-08-15",
                roll_no="ECE-2023-042", cgpa=9.12,
            ),
            User(
                id="student-3", email="rahul.verma@campusorbit.edu", name="Rahul Verma",
                hashed_password=password, role="student", avatar="👨‍🎓",
                department="B.Tech CSE", phone="+91-9876543218", join_date="2023-08-01",
                roll_no="CSE-2023-015", cgpa=7.80,
            ),
            User(
                id="student-4", email="ananya.gupta@campusorbit.edu", name="Ananya Gupta",
                hashed_password=password, role="student", avatar="👩‍🎓",
                department="B.Tech CSE", phone="+91-9876543219", join_date="2023-08-01",
                roll_no="CSE-2023-023", cgpa=8.93,
            ),
            User(
                id="student-5", email="karthik.nair@campusorbit.edu", name="Karthik Nair",
                hashed_password=password, role="student", avatar="👨‍🎓",
                department="B.Tech ECE", phone="+91-9876543221", join_date="2023-08-15",
                roll_no="ECE-2023-018", cgpa=7.55,
            ),
            User(
                id="parent-1", email="parent@campusorbit.edu", name="Vikram Patel",
                hashed_password=password, role="parent", avatar="👨‍👩‍👧",
                phone="+91-9876543213", join_date="2023-08-01",
            ),
            User(
                id="finance-1", email="finance@campusorbit.edu", name="Ms. Deepika Verma",
                hashed_password=password, role="finance_officer", avatar="👩‍💻",
                department="Finance", phone="+91-9876543214", join_date="2022-03-15",
            ),
            User(
                id="employee-1", email="employee@campusorbit.edu", name="Rohan Singh",
                hashed_password=password, role="employee", avatar="👨‍💼",
                department="Student Services", phone="+91-9876543215", join_date="2021-11-20",
            ),
        ]
        session.add_all(users)

        # ─── Courses ───
        courses = [
            Course(
                id="course-1", code="CSE301", name="Data Structures & Algorithms",
                instructor_id="teacher-1", semester="Fall 2024", credits=4,
                description="Comprehensive study of data structures and algorithm design principles",
                student_count=45,
            ),
            Course(
                id="course-2", code="CSE302", name="Database Management Systems",
                instructor_id="teacher-2", semester="Fall 2024", credits=3,
                description="Design and implementation of relational and NoSQL databases",
                student_count=48,
            ),
            Course(
                id="course-3", code="ECE301", name="Digital Circuits",
                instructor_id="teacher-2", semester="Fall 2024", credits=4,
                description="Logic gates, Boolean algebra, and digital circuit design",
                student_count=50,
            ),
        ]
        session.add_all(courses)

        # ─── Assignments ───
        assignments = [
            Assignment(
                id="assign-1", course_id="course-1", title="Binary Search Tree Implementation",
                due_date="2024-11-22", submitted_by=30, total_students=45,
                description="Implement a complete binary search tree with insert, delete, and search operations",
            ),
            Assignment(
                id="assign-2", course_id="course-1", title="Graph Algorithm Analysis",
                due_date="2024-11-29", submitted_by=12, total_students=45,
                description="Analyze BFS, DFS, and shortest path algorithms",
            ),
            Assignment(
                id="assign-3", course_id="course-2", title="SQL Query Optimization",
                due_date="2024-11-25", submitted_by=35, total_students=48,
                description="Optimize complex SQL queries for better performance",
            ),
        ]
        session.add_all(assignments)

        # ─── Grades ───
        grades = [
            Grade(id="grade-1", student_id="student-1", course_id="course-1", midterm=85, endterm=88, assignment_score=92, grade_letter="A"),
            Grade(id="grade-2", student_id="student-1", course_id="course-2", midterm=78, endterm=82, assignment_score=85, grade_letter="B+"),
            Grade(id="grade-3", student_id="student-2", course_id="course-1", midterm=92, endterm=95, assignment_score=96, grade_letter="A+"),
        ]
        session.add_all(grades)

        # ─── Study Materials ───
        materials = [
            StudyMaterial(id="material-1", course_id="course-1", title="DSA Lecture Notes - Week 1", type="pdf", uploaded_date="2024-11-01", size="2.4 MB", downloads=145),
            StudyMaterial(id="material-2", course_id="course-1", title="Tree Structures Video Tutorial", type="video", uploaded_date="2024-11-05", size="125 MB", downloads=89),
            StudyMaterial(id="material-3", course_id="course-2", title="SQL Fundamentals Presentation", type="pptx", uploaded_date="2024-11-03", size="8.7 MB", downloads=156),
        ]
        session.add_all(materials)

        # ─── Syllabus ───
        syllabus_items = [
            Syllabus(id="syl-1", course_id="course-1", unit_number=1, title="Introduction to Data Structures", topics=json.dumps(["Arrays", "Linked Lists", "Stacks", "Queues"]), hours=10),
            Syllabus(id="syl-2", course_id="course-1", unit_number=2, title="Trees & Graphs", topics=json.dumps(["Binary Trees", "BST", "AVL Trees", "Graph Traversals"]), hours=12),
            Syllabus(id="syl-3", course_id="course-2", unit_number=1, title="Relational Model", topics=json.dumps(["ER Diagrams", "Normalization", "SQL Basics"]), hours=8),
        ]
        session.add_all(syllabus_items)

        # ─── Fees ───
        fees = [
            Fee(id="fee-1", student_id="student-1", amount=150000, due_date="2024-08-15", status="paid", payment_mode="online"),
            Fee(id="fee-2", student_id="student-1", amount=15000, due_date="2024-09-15", status="pending", payment_mode="offline"),
            Fee(id="fee-3", student_id="student-2", amount=150000, due_date="2024-08-15", status="overdue", payment_mode="offline"),
        ]
        session.add_all(fees)

        # ─── Attendance ───
        att_records = [
            Attendance(id="att-1", student_id="student-1", date="2024-11-15", status="present"),
            Attendance(id="att-2", student_id="student-1", date="2024-11-14", status="present"),
            Attendance(id="att-3", student_id="student-1", date="2024-11-13", status="absent"),
            Attendance(id="att-4", student_id="student-2", date="2024-11-15", status="present"),
            Attendance(id="att-5", student_id="student-2", date="2024-11-14", status="absent"),
        ]
        session.add_all(att_records)

        # ─── Biometric ───
        bio = [
            BiometricRecord(id="bio-1", teacher_id="teacher-1", date="2024-11-15", check_in="09:00", check_out="17:30", hours_worked=8),
            BiometricRecord(id="bio-2", teacher_id="teacher-2", date="2024-11-15", check_in="09:15", check_out="17:45", hours_worked=8.5),
        ]
        session.add_all(bio)

        # ─── Leads ───
        leads = [
            Lead(id="lead-1", name="Vikram Sharma", email="vikram.sharma@email.com", phone="+91-9876543200", source="QR Code", status="interested", follow_up_date="2024-11-17"),
            Lead(id="lead-2", name="Sneha Verma", email="sneha.verma@email.com", phone="+91-9876543201", source="Website", status="contacted", follow_up_date="2024-11-19"),
            Lead(id="lead-3", name="Rohit Singh", email="rohit.singh@email.com", phone="+91-9876543202", source="Campus Tour", status="interested", follow_up_date="2024-11-15"),
            Lead(id="lead-4", name="Anjali Gupta", email="anjali.gupta@email.com", phone="+91-9876543203", source="Social Media", status="applied", follow_up_date="2024-11-18"),
        ]
        session.add_all(leads)

        # ─── Campus News ───
        news = [
            CampusNews(id="news-1", title="Annual Tech Summit 2024 Announced", content="Join us for the biggest tech summit featuring industry leaders and workshops", date="2024-11-15", category="event", author="Admin"),
            CampusNews(id="news-2", title="Scholarship Results Declared", content="Merit and need-based scholarship results are now available", date="2024-11-14", category="announcement", author="Finance Office"),
            CampusNews(id="news-3", title="Campus Renovation Project Update", content="New library wing and IT labs opening next semester", date="2024-11-13", category="announcement", author="Admin"),
            CampusNews(id="news-4", title="Placement Drive Schedule", content="Top companies visiting campus for recruitment - details inside", date="2024-11-12", category="event", author="Placement Cell"),
        ]
        session.add_all(news)

        # ─── Notifications ───
        notifications = [
            Notification(id="notif-1", user_id="student-1", type="fee", message="Fee payment due on Nov 15", read=False),
            Notification(id="notif-2", user_id="student-1", type="assignment", message="New assignment added in DSA course", read=False),
            Notification(id="notif-3", user_id="student-1", type="news", message="Annual Tech Summit 2024 announced", read=True),
            Notification(id="notif-4", user_id="student-1", type="exam", message="Midterm schedule released", read=True),
        ]
        session.add_all(notifications)

        # ─── Inventory ───
        inventory = [
            InventoryItem(id="inv-1", name="Dell Laptop", category="Electronics", quantity=25, location="Lab-A", condition="Good", last_updated="2024-11-10"),
            InventoryItem(id="inv-2", name="Physics Lab Equipment", category="Equipment", quantity=15, location="Lab-B", condition="Fair", last_updated="2024-11-08"),
            InventoryItem(id="inv-3", name="Chemistry Lab Chemicals", category="Supplies", quantity=200, location="Storage-C", condition="Good", last_updated="2024-11-12"),
        ]
        session.add_all(inventory)

        # ─── Transport ───
        buses = [
            TransportBus(id="bus-1", bus_no="BUS-001", route="North Route", latitude=28.5355, longitude=77.391, speed=45, student_count=42),
            TransportBus(id="bus-2", bus_no="BUS-002", route="South Route", latitude=28.5345, longitude=77.392, speed=38, student_count=38),
            TransportBus(id="bus-3", bus_no="BUS-003", route="East Route", latitude=28.5365, longitude=77.393, speed=52, student_count=45),
        ]
        session.add_all(buses)

        # ─── Pricing Plans ───
        plans = [
            PricingPlan(id="plan-1", name="Base", price=999, features=json.dumps(["Student Information System", "Basic Fee Management", "AI ChatGPT Assistant"]), icon="🎯", highlighted=False),
            PricingPlan(id="plan-2", name="Standard", price=2999, features=json.dumps(["All Base features", "Custom Report Cards", "Timetable Substitution Manager", "Real-time GPS Tracking"]), icon="⭐", highlighted=True),
            PricingPlan(id="plan-3", name="Premium", price=5999, features=json.dumps(["All Standard features", "Multi-campus Hub", "Biometric Integration", "Website Management", "API Access"]), icon="👑", highlighted=False),
        ]
        session.add_all(plans)

        # ─── Marketplace ───
        marketplace = [
            MarketplaceIntegration(id="power-1", name="Vedantu", category="Academic Content", description="Interactive online tuitions and problem solving", icon="📚"),
            MarketplaceIntegration(id="power-2", name="GrayQuest", category="Fee Financing", description="EMI options for student fees", icon="💳"),
            MarketplaceIntegration(id="power-3", name="MetabookXR", category="VR Learning", description="Immersive VR learning experiences", icon="🎮"),
            MarketplaceIntegration(id="power-4", name="Jodo Finance", category="Fee Financing", description="Flexible payment plans for education", icon="💰"),
        ]
        session.add_all(marketplace)

        # ─── Substitution Requests ───
        subs = [
            SubstitutionRequest(
                id="sub-1", date="2024-11-20", time="10:00 AM", course="Data Structures",
                original_teacher="Prof. Priya Sharma", reason="Medical Leave", status="pending",
                suggested_teachers=json.dumps(["Prof. Amit Kumar", "Prof. Rajesh Kumar"]),
            ),
            SubstitutionRequest(
                id="sub-2", date="2024-11-21", time="2:00 PM", course="Database Systems",
                original_teacher="Prof. Amit Kumar", reason="Conference", status="assigned",
                assigned_teacher="Prof. Rajesh Kumar",
            ),
        ]
        session.add_all(subs)

        # ─── Complaints ───
        complaints = [
            Complaint(
                id="comp-1", user_id="student-1", subject="WiFi connectivity in Hostel Block-A",
                description="WiFi has been extremely slow in the hostel for the past week. Unable to attend online classes or submit assignments.",
                category="infrastructure", status="open", priority="high",
            ),
            Complaint(
                id="comp-2", user_id="student-3", subject="Lab equipment not working",
                description="Several computers in Lab-A have non-functional keyboards and mice. Reported to lab assistant but no action taken.",
                category="infrastructure", status="in_progress", priority="medium",
            ),
            Complaint(
                id="comp-3", user_id="student-2", subject="Grade discrepancy in midterm",
                description="My midterm score for DSA shows 72 but I believe it should be 82 based on the answer key discussion in class.",
                category="academic", status="resolved", priority="high",
                resolution="Score corrected after re-evaluation. Updated grade from 72 to 82.",
            ),
            Complaint(
                id="comp-4", user_id="student-4", subject="Canteen food quality",
                description="The food quality in the canteen has deteriorated significantly this month. Several students have reported stomach issues.",
                category="administrative", status="open", priority="medium",
            ),
        ]
        session.add_all(complaints)

        # ─── Extra Fees for new students ───
        extra_fees = [
            Fee(id="fee-4", student_id="student-3", amount=150000, due_date="2024-08-15", status="paid", payment_mode="online"),
            Fee(id="fee-5", student_id="student-4", amount=150000, due_date="2024-08-15", status="pending", payment_mode="online"),
            Fee(id="fee-6", student_id="student-5", amount=150000, due_date="2024-08-15", status="paid", payment_mode="offline"),
        ]
        session.add_all(extra_fees)

        # ─── Extra Attendance for new students ───
        extra_att = [
            Attendance(id="att-6", student_id="student-3", date="2024-11-15", status="present"),
            Attendance(id="att-7", student_id="student-3", date="2024-11-14", status="present"),
            Attendance(id="att-8", student_id="student-4", date="2024-11-15", status="present"),
            Attendance(id="att-9", student_id="student-4", date="2024-11-14", status="late"),
            Attendance(id="att-10", student_id="student-5", date="2024-11-15", status="absent"),
            Attendance(id="att-11", student_id="student-5", date="2024-11-14", status="present"),
        ]
        session.add_all(extra_att)

        # ─── Notifications for new students ───
        extra_notifs = [
            Notification(id="notif-5", user_id="student-3", type="fee", message="Your semester fee has been received. Thank you!", read=False),
            Notification(id="notif-6", user_id="student-4", type="fee", message="Fee payment due on Aug 15. Please pay soon to avoid late charges.", read=False),
            Notification(id="notif-7", user_id="student-5", type="attendance", message="Your attendance is below 75%. Please attend classes regularly.", read=False),
        ]
        session.add_all(extra_notifs)

        await session.commit()
        print("✅ Database seeded successfully!")
        print(f"   👤 Users:        {len(users)}")
        print(f"   📚 Courses:      {len(courses)}")
        print(f"   💰 Fees:         {len(fees) + len(extra_fees)}")
        print(f"   📋 Attendance:   {len(att_records) + len(extra_att)}")
        print(f"   📰 News:         {len(news)}")
        print(f"   🔔 Notifications:{len(notifications) + len(extra_notifs)}")
        print(f"   🚌 Buses:        {len(buses)}")
        print(f"   📢 Complaints:   {len(complaints)}")
        print(f"   ─────────────────────────")
        print(f"   Demo accounts (all password: admin123):")
        for u in users:
            print(f"     {u.role:16} → {u.email}")


if __name__ == "__main__":
    asyncio.run(seed())
