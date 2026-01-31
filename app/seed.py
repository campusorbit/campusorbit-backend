"""Database seeder: populates the database with comprehensive demo data for all ERP modules."""

import asyncio
import json
import uuid

from app.database import async_session_factory, engine, Base
from app.models import *  # noqa: F403 - import all models so they register with Base
from app.services.auth_service import hash_password


async def seed():
    # Drop & recreate all tables (clean seed)
    print("🗑️  Dropping existing tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("🔨 Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("🌱 Seeding demo data...")

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
                id="teacher-3", email="prof.sunita@campusorbit.edu", name="Prof. Sunita Devi",
                hashed_password=password, role="teacher", avatar="👩‍🏫",
                department="Mathematics", phone="+91-9876543230", join_date="2019-07-01",
                specialization="Applied Mathematics",
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
        await session.flush()  # users must exist before FK references

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
            Course(
                id="course-4", code="CSE303", name="Computer Networks",
                instructor_id="teacher-2", semester="Fall 2024", credits=3,
                description="Network architecture, protocols, TCP/IP, and network security",
                student_count=42,
            ),
            Course(
                id="course-5", code="MAT201", name="Discrete Mathematics",
                instructor_id="teacher-3", semester="Fall 2024", credits=3,
                description="Graph theory, combinatorics, logic, and algebraic structures",
                student_count=55,
            ),
        ]
        session.add_all(courses)
        await session.flush()  # courses must exist before exams/assignments

        # ─── Assignments ───
        assignments = [
            Assignment(id="assign-1", course_id="course-1", title="Binary Search Tree Implementation",
                       due_date="2024-11-22", submitted_by=30, total_students=45,
                       description="Implement a complete BST with insert, delete, and search"),
            Assignment(id="assign-2", course_id="course-1", title="Graph Algorithm Analysis",
                       due_date="2024-11-29", submitted_by=12, total_students=45,
                       description="Analyze BFS, DFS, and shortest path algorithms"),
            Assignment(id="assign-3", course_id="course-2", title="SQL Query Optimization",
                       due_date="2024-11-25", submitted_by=35, total_students=48,
                       description="Optimize complex SQL queries for better performance"),
            Assignment(id="assign-4", course_id="course-4", title="TCP/IP Packet Analysis",
                       due_date="2024-12-01", submitted_by=20, total_students=42,
                       description="Analyze TCP/IP packets using Wireshark"),
        ]
        session.add_all(assignments)

        # ─── Grades ───
        grades = [
            Grade(id="grade-1", student_id="student-1", course_id="course-1", midterm=85, endterm=88, assignment_score=92, grade_letter="A"),
            Grade(id="grade-2", student_id="student-1", course_id="course-2", midterm=78, endterm=82, assignment_score=85, grade_letter="B+"),
            Grade(id="grade-3", student_id="student-2", course_id="course-1", midterm=92, endterm=95, assignment_score=96, grade_letter="A+"),
            Grade(id="grade-4", student_id="student-3", course_id="course-1", midterm=72, endterm=75, assignment_score=80, grade_letter="B"),
            Grade(id="grade-5", student_id="student-4", course_id="course-2", midterm=88, endterm=90, assignment_score=94, grade_letter="A"),
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
            Fee(id="fee-4", student_id="student-3", amount=150000, due_date="2024-08-15", status="paid", payment_mode="online"),
            Fee(id="fee-5", student_id="student-4", amount=150000, due_date="2024-08-15", status="pending", payment_mode="online"),
            Fee(id="fee-6", student_id="student-5", amount=150000, due_date="2024-08-15", status="paid", payment_mode="offline"),
        ]
        session.add_all(fees)

        # ─── Attendance ───
        att_records = [
            Attendance(id="att-1", student_id="student-1", date="2024-11-15", status="present"),
            Attendance(id="att-2", student_id="student-1", date="2024-11-14", status="present"),
            Attendance(id="att-3", student_id="student-1", date="2024-11-13", status="absent"),
            Attendance(id="att-4", student_id="student-2", date="2024-11-15", status="present"),
            Attendance(id="att-5", student_id="student-2", date="2024-11-14", status="absent"),
            Attendance(id="att-6", student_id="student-3", date="2024-11-15", status="present"),
            Attendance(id="att-7", student_id="student-3", date="2024-11-14", status="present"),
            Attendance(id="att-8", student_id="student-4", date="2024-11-15", status="present"),
            Attendance(id="att-9", student_id="student-4", date="2024-11-14", status="late"),
            Attendance(id="att-10", student_id="student-5", date="2024-11-15", status="absent"),
            Attendance(id="att-11", student_id="student-5", date="2024-11-14", status="present"),
        ]
        session.add_all(att_records)

        # ─── Biometric ───
        bio = [
            BiometricRecord(id="bio-1", teacher_id="teacher-1", date="2024-11-15", check_in="09:00", check_out="17:30", hours_worked=8),
            BiometricRecord(id="bio-2", teacher_id="teacher-2", date="2024-11-15", check_in="09:15", check_out="17:45", hours_worked=8.5),
            BiometricRecord(id="bio-3", teacher_id="teacher-3", date="2024-11-15", check_in="08:45", check_out="16:30", hours_worked=7.75),
        ]
        session.add_all(bio)

        # ─── Leads (CRM / Admissions) ───
        leads = [
            Lead(id="lead-1", name="Vikram Sharma", email="vikram.sharma@email.com", phone="+91-9876543200", source="QR Code", status="interested", follow_up_date="2024-11-17"),
            Lead(id="lead-2", name="Sneha Verma", email="sneha.verma@email.com", phone="+91-9876543201", source="Website", status="contacted", follow_up_date="2024-11-19"),
            Lead(id="lead-3", name="Rohit Singh", email="rohit.singh@email.com", phone="+91-9876543202", source="Campus Tour", status="interested", follow_up_date="2024-11-15"),
            Lead(id="lead-4", name="Anjali Gupta", email="anjali.gupta@email.com", phone="+91-9876543203", source="Social Media", status="applied", follow_up_date="2024-11-18"),
            Lead(id="lead-5", name="Deepak Kumar", email="deepak.kumar@email.com", phone="+91-9876543204", source="Campus Tour", status="enrolled", follow_up_date="2024-11-20"),
            Lead(id="lead-6", name="Kavya Nair", email="kavya.nair@email.com", phone="+91-9876543205", source="Website", status="interested", follow_up_date="2024-11-22"),
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
            Notification(id="notif-5", user_id="student-3", type="fee", message="Your semester fee has been received. Thank you!", read=False),
            Notification(id="notif-6", user_id="student-4", type="fee", message="Fee payment due on Aug 15. Please pay soon.", read=False),
            Notification(id="notif-7", user_id="student-5", type="attendance", message="Your attendance is below 75%. Please attend regularly.", read=False),
        ]
        session.add_all(notifications)

        # ─── Inventory ───
        inventory = [
            InventoryItem(id="inv-1", name="Dell Laptop", category="Electronics", quantity=25, location="Lab-A", condition="Good", last_updated="2024-11-10"),
            InventoryItem(id="inv-2", name="Physics Lab Equipment Set", category="Equipment", quantity=15, location="Lab-B", condition="Fair", last_updated="2024-11-08"),
            InventoryItem(id="inv-3", name="Chemistry Lab Chemicals", category="Supplies", quantity=200, location="Storage-C", condition="Good", last_updated="2024-11-12"),
            InventoryItem(id="inv-4", name="Projector (Epson EB-X500)", category="Electronics", quantity=10, location="Seminar Hall", condition="Good", last_updated="2024-11-05"),
            InventoryItem(id="inv-5", name="Whiteboard Markers (Box)", category="Supplies", quantity=150, location="Store Room-A", condition="Good", last_updated="2024-11-14"),
            InventoryItem(id="inv-6", name="Office Chairs", category="Furniture", quantity=60, location="Faculty Block", condition="Fair", last_updated="2024-10-20"),
            InventoryItem(id="inv-7", name="Printer (HP LaserJet)", category="Electronics", quantity=8, location="Admin Office", condition="Good", last_updated="2024-11-01"),
            InventoryItem(id="inv-8", name="Sports Equipment Kit", category="Sports", quantity=12, location="Sports Room", condition="Good", last_updated="2024-11-11"),
        ]
        session.add_all(inventory)

        # ─── Transport ───
        buses = [
            TransportBus(id="bus-1", bus_no="BUS-001", route="North Route — Indira Nagar → Campus", latitude=28.5355, longitude=77.391, speed=45, student_count=42),
            TransportBus(id="bus-2", bus_no="BUS-002", route="South Route — Jayanagar → Campus", latitude=28.5345, longitude=77.392, speed=38, student_count=38),
            TransportBus(id="bus-3", bus_no="BUS-003", route="East Route — Whitefield → Campus", latitude=28.5365, longitude=77.393, speed=52, student_count=45),
            TransportBus(id="bus-4", bus_no="BUS-004", route="West Route — Rajajinagar → Campus", latitude=28.5375, longitude=77.394, speed=35, student_count=30),
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
            Complaint(id="comp-1", user_id="student-1", subject="WiFi connectivity in Hostel Block-A",
                      description="WiFi has been extremely slow in the hostel for the past week.", category="infrastructure", status="open", priority="high"),
            Complaint(id="comp-2", user_id="student-3", subject="Lab equipment not working",
                      description="Several computers in Lab-A have non-functional keyboards.", category="infrastructure", status="in_progress", priority="medium"),
            Complaint(id="comp-3", user_id="student-2", subject="Grade discrepancy in midterm",
                      description="My midterm score for DSA shows 72 but should be 82.", category="academic", status="resolved", priority="high",
                      resolution="Score corrected after re-evaluation."),
            Complaint(id="comp-4", user_id="student-4", subject="Canteen food quality",
                      description="The food quality in the canteen has deteriorated significantly.", category="administrative", status="open", priority="medium"),
        ]
        session.add_all(complaints)

        # ══════════════════════════════════════════════════
        # NEW MODULE SEED DATA
        # ══════════════════════════════════════════════════

        # ─── Library Books ───
        library_books = [
            LibraryBook(id="book-1", title="Introduction to Algorithms", author="Thomas H. Cormen", isbn="978-0262033848", category="Computer Science",
                        total_copies=5, available_copies=3, shelf_location="CS-A1", publisher="MIT Press", published_year=2009, barcode="LIB001"),
            LibraryBook(id="book-2", title="Database System Concepts", author="Abraham Silberschatz", isbn="978-0078022159", category="Computer Science",
                        total_copies=4, available_copies=2, shelf_location="CS-A2", publisher="McGraw Hill", published_year=2019, barcode="LIB002"),
            LibraryBook(id="book-3", title="Computer Networking: A Top-Down Approach", author="James Kurose", isbn="978-0133594140", category="Computer Science",
                        total_copies=6, available_copies=4, shelf_location="CS-A3", publisher="Pearson", published_year=2016, barcode="LIB003"),
            LibraryBook(id="book-4", title="Engineering Mathematics", author="B.S. Grewal", isbn="978-8174091154", category="Mathematics",
                        total_copies=8, available_copies=5, shelf_location="MA-B1", publisher="Khanna Publishers", published_year=2020, barcode="LIB004"),
            LibraryBook(id="book-5", title="Discrete Mathematics and Its Applications", author="Kenneth Rosen", isbn="978-0073383095", category="Mathematics",
                        total_copies=5, available_copies=3, shelf_location="MA-B2", publisher="McGraw Hill", published_year=2018, barcode="LIB005"),
            LibraryBook(id="book-6", title="Digital Design", author="Morris Mano", isbn="978-0132774208", category="Electronics",
                        total_copies=4, available_copies=4, shelf_location="EC-C1", publisher="Pearson", published_year=2013, barcode="LIB006"),
            LibraryBook(id="book-7", title="Operating System Concepts", author="Abraham Silberschatz", isbn="978-1118063330", category="Computer Science",
                        total_copies=5, available_copies=2, shelf_location="CS-A4", publisher="Wiley", published_year=2018, barcode="LIB007"),
            LibraryBook(id="book-8", title="The C Programming Language", author="Brian Kernighan & Dennis Ritchie", isbn="978-0131103627", category="Computer Science",
                        total_copies=10, available_copies=7, shelf_location="CS-A5", publisher="Prentice Hall", published_year=1988, barcode="LIB008"),
            LibraryBook(id="book-9", title="Clean Code", author="Robert C. Martin", isbn="978-0132350884", category="Software Engineering",
                        total_copies=3, available_copies=1, shelf_location="SE-D1", publisher="Prentice Hall", published_year=2008, barcode="LIB009"),
            LibraryBook(id="book-10", title="Artificial Intelligence: A Modern Approach", author="Stuart Russell & Peter Norvig", isbn="978-0134610993", category="Computer Science",
                        total_copies=4, available_copies=3, shelf_location="CS-A6", publisher="Pearson", published_year=2020, barcode="LIB010"),
        ]
        session.add_all(library_books)
        await session.flush()  # books must exist before book_issues

        # ─── Book Issues ───
        book_issues = [
            BookIssue(id="issue-1", book_id="book-1", student_id="student-1", issue_date="2024-11-01", due_date="2024-11-15", status="issued", fine=0),
            BookIssue(id="issue-2", book_id="book-2", student_id="student-1", issue_date="2024-10-20", due_date="2024-11-03", return_date="2024-11-02", status="returned", fine=0),
            BookIssue(id="issue-3", book_id="book-3", student_id="student-2", issue_date="2024-11-05", due_date="2024-11-19", status="issued", fine=0),
            BookIssue(id="issue-4", book_id="book-7", student_id="student-3", issue_date="2024-10-15", due_date="2024-10-29", status="overdue", fine=50),
            BookIssue(id="issue-5", book_id="book-9", student_id="student-4", issue_date="2024-11-10", due_date="2024-11-24", status="issued", fine=0),
            BookIssue(id="issue-6", book_id="book-7", student_id="student-2", issue_date="2024-10-01", due_date="2024-10-15", return_date="2024-10-14", status="returned", fine=0),
        ]
        session.add_all(book_issues)

        # ─── Documents ───
        documents = [
            Document(id="doc-1", title="Anti-Ragging Policy 2024-25", category="Policy", file_type="pdf", uploaded_by="Admin Office",
                     uploaded_date="2024-08-01", size="1.2 MB", description="Complete anti-ragging policy and guidelines", access_roles="all", academic_year="2024-25"),
            Document(id="doc-2", title="Fee Structure Circular — Fall 2024", category="Circular", file_type="pdf", uploaded_by="Finance Office",
                     uploaded_date="2024-07-15", size="340 KB", description="Detailed fee breakup for all programs", access_roles="all", academic_year="2024-25"),
            Document(id="doc-3", title="Student Handbook", category="Guide", file_type="pdf", uploaded_by="Dean's Office",
                     uploaded_date="2024-08-10", size="5.8 MB", description="Comprehensive student guidelines and rules", access_roles="student,parent", academic_year="2024-25"),
            Document(id="doc-4", title="Faculty Leave Application Form", category="Form", file_type="docx", uploaded_by="HR Department",
                     uploaded_date="2024-09-01", size="85 KB", description="Standard leave application form for faculty", access_roles="teacher,admin", academic_year="2024-25"),
            Document(id="doc-5", title="Examination Guidelines", category="Circular", file_type="pdf", uploaded_by="Exam Cell",
                     uploaded_date="2024-10-20", size="920 KB", description="End-semester examination rules and schedule", access_roles="all", academic_year="2024-25"),
            Document(id="doc-6", title="Annual Budget Report 2023-24", category="Report", file_type="xlsx", uploaded_by="Finance Office",
                     uploaded_date="2024-04-15", size="2.1 MB", description="Complete financial report for the academic year", access_roles="admin,finance_officer", academic_year="2023-24"),
            Document(id="doc-7", title="Transport Route Map", category="Guide", file_type="pdf", uploaded_by="Transport Cell",
                     uploaded_date="2024-08-05", size="4.5 MB", description="Bus route maps and pickup points", access_roles="all", academic_year="2024-25"),
            Document(id="doc-8", title="Internship Certificate Template", category="Certificate", file_type="docx", uploaded_by="Training & Placement",
                     uploaded_date="2024-09-15", size="120 KB", description="Official internship certificate template", access_roles="admin,teacher", academic_year="2024-25"),
        ]
        session.add_all(documents)

        # ─── Salary Slips ───
        salary_slips = [
            SalarySlip(id="sal-1", employee_id="teacher-1", employee_name="Prof. Priya Sharma", department="Computer Science", designation="Associate Professor",
                       month="October", year=2024, basic=65000, hra=19500, da=6500, allowances=5000, pf_deduction=7800, tax_deduction=8500, other_deductions=1200, net_pay=78500, status="paid", paid_date="2024-10-28"),
            SalarySlip(id="sal-2", employee_id="teacher-2", employee_name="Prof. Amit Kumar", department="Computer Science", designation="Assistant Professor",
                       month="October", year=2024, basic=55000, hra=16500, da=5500, allowances=4000, pf_deduction=6600, tax_deduction=6000, other_deductions=1000, net_pay=66400, status="paid", paid_date="2024-10-28"),
            SalarySlip(id="sal-3", employee_id="teacher-3", employee_name="Prof. Sunita Devi", department="Mathematics", designation="Professor",
                       month="October", year=2024, basic=80000, hra=24000, da=8000, allowances=7000, pf_deduction=9600, tax_deduction=12000, other_deductions=1500, net_pay=95900, status="paid", paid_date="2024-10-28"),
            SalarySlip(id="sal-4", employee_id="employee-1", employee_name="Rohan Singh", department="Student Services", designation="Administrative Assistant",
                       month="October", year=2024, basic=30000, hra=9000, da=3000, allowances=2000, pf_deduction=3600, tax_deduction=2000, other_deductions=500, net_pay=37900, status="paid", paid_date="2024-10-28"),
            SalarySlip(id="sal-5", employee_id="finance-1", employee_name="Ms. Deepika Verma", department="Finance", designation="Finance Officer",
                       month="October", year=2024, basic=60000, hra=18000, da=6000, allowances=5000, pf_deduction=7200, tax_deduction=7500, other_deductions=1000, net_pay=73300, status="paid", paid_date="2024-10-28"),
            SalarySlip(id="sal-6", employee_id="teacher-1", employee_name="Prof. Priya Sharma", department="Computer Science", designation="Associate Professor",
                       month="November", year=2024, basic=65000, hra=19500, da=6500, allowances=5000, pf_deduction=7800, tax_deduction=8500, other_deductions=1200, net_pay=78500, status="generated"),
            SalarySlip(id="sal-7", employee_id="teacher-2", employee_name="Prof. Amit Kumar", department="Computer Science", designation="Assistant Professor",
                       month="November", year=2024, basic=55000, hra=16500, da=5500, allowances=4000, pf_deduction=6600, tax_deduction=6000, other_deductions=1000, net_pay=66400, status="generated"),
        ]
        session.add_all(salary_slips)

        # ─── Leave Requests ───
        leave_requests = [
            LeaveRequest(id="leave-1", user_id="teacher-1", user_name="Prof. Priya Sharma", leave_type="Medical", start_date="2024-11-20", end_date="2024-11-22", days=3,
                         reason="Medical appointment and recovery", status="approved", approved_by="Dr. Rajesh Kumar"),
            LeaveRequest(id="leave-2", user_id="teacher-2", user_name="Prof. Amit Kumar", leave_type="Conference", start_date="2024-11-21", end_date="2024-11-23", days=3,
                         reason="Attending IEEE International Conference on Networks", status="approved", approved_by="Dr. Rajesh Kumar"),
            LeaveRequest(id="leave-3", user_id="employee-1", user_name="Rohan Singh", leave_type="Casual", start_date="2024-11-25", end_date="2024-11-25", days=1,
                         reason="Personal work", status="pending"),
            LeaveRequest(id="leave-4", user_id="teacher-3", user_name="Prof. Sunita Devi", leave_type="Earned", start_date="2024-12-20", end_date="2024-12-31", days=10,
                         reason="Year-end vacation", status="pending"),
            LeaveRequest(id="leave-5", user_id="teacher-1", user_name="Prof. Priya Sharma", leave_type="Casual", start_date="2024-10-10", end_date="2024-10-10", days=1,
                         reason="Family function", status="approved", approved_by="Dr. Rajesh Kumar"),
        ]
        session.add_all(leave_requests)

        # ─── Expenses ───
        expenses = [
            Expense(id="exp-1", title="Lab Equipment Purchase — 10 PCs", category="Infrastructure", amount=450000, date="2024-10-15",
                    vendor="Dell India", approved_by="Dr. Rajesh Kumar", status="approved", receipt_no="RCP-2024-001"),
            Expense(id="exp-2", title="Annual Software Licenses Renewal", category="Software", amount=180000, date="2024-09-01",
                    vendor="Microsoft India", approved_by="Dr. Rajesh Kumar", status="approved", receipt_no="RCP-2024-002"),
            Expense(id="exp-3", title="Campus WiFi Infrastructure Upgrade", category="Infrastructure", amount=320000, date="2024-11-01",
                    vendor="Cisco Systems", approved_by="Dr. Rajesh Kumar", status="approved", receipt_no="RCP-2024-003"),
            Expense(id="exp-4", title="Annual Day Event Expenses", category="Events", amount=85000, date="2024-11-10",
                    vendor="EventPro Solutions", status="pending", receipt_no="RCP-2024-004"),
            Expense(id="exp-5", title="Library Book Purchase — Q4 2024", category="Library", amount=125000, date="2024-10-20",
                    vendor="Amazon India", approved_by="Dr. Rajesh Kumar", status="approved", receipt_no="RCP-2024-005"),
            Expense(id="exp-6", title="Sports Equipment Purchase", category="Sports", amount=65000, date="2024-11-05",
                    vendor="Decathlon India", status="pending", receipt_no="RCP-2024-006"),
            Expense(id="exp-7", title="Canteen Kitchen Maintenance", category="Maintenance", amount=48000, date="2024-10-25",
                    vendor="ServTech Solutions", approved_by="Dr. Rajesh Kumar", status="approved", receipt_no="RCP-2024-007"),
        ]
        session.add_all(expenses)

        # ─── Budgets ───
        budgets = [
            Budget(id="bgt-1", category="Infrastructure", allocated=2000000, spent=770000, academic_year="2024-25"),
            Budget(id="bgt-2", category="Software", allocated=500000, spent=180000, academic_year="2024-25"),
            Budget(id="bgt-3", category="Events", allocated=300000, spent=85000, academic_year="2024-25"),
            Budget(id="bgt-4", category="Library", allocated=400000, spent=125000, academic_year="2024-25"),
            Budget(id="bgt-5", category="Sports", allocated=200000, spent=65000, academic_year="2024-25"),
            Budget(id="bgt-6", category="Maintenance", allocated=350000, spent=48000, academic_year="2024-25"),
            Budget(id="bgt-7", category="Salaries", allocated=15000000, spent=11520000, academic_year="2024-25"),
        ]
        session.add_all(budgets)

        # ─── Exams ───
        exams = [
            Exam(id="exam-1", title="DSA Midterm Examination", course_id="course-1", course_name="Data Structures & Algorithms",
                 exam_type="midterm", date="2024-10-15", duration_mins=120, total_marks=100, status="completed",
                 instructions="No electronic devices. Attempt all questions."),
            Exam(id="exam-2", title="DBMS Quiz 1", course_id="course-2", course_name="Database Management Systems",
                 exam_type="quiz", date="2024-10-20", duration_mins=30, total_marks=25, status="completed",
                 instructions="MCQs and short answer questions."),
            Exam(id="exam-3", title="DSA End-Term Examination", course_id="course-1", course_name="Data Structures & Algorithms",
                 exam_type="endterm", date="2024-12-10", duration_mins=180, total_marks=100, status="scheduled",
                 instructions="Calculator allowed. Attempt all sections."),
            Exam(id="exam-4", title="Computer Networks Midterm", course_id="course-4", course_name="Computer Networks",
                 exam_type="midterm", date="2024-10-22", duration_mins=120, total_marks=100, status="completed"),
            Exam(id="exam-5", title="Digital Circuits Lab Practical", course_id="course-3", course_name="Digital Circuits",
                 exam_type="assignment", date="2024-11-18", duration_mins=90, total_marks=50, status="completed"),
            Exam(id="exam-6", title="DBMS End-Term Examination", course_id="course-2", course_name="Database Management Systems",
                 exam_type="endterm", date="2024-12-12", duration_mins=180, total_marks=100, status="scheduled"),
        ]
        session.add_all(exams)
        await session.flush()  # exams must exist before exam_results

        # ─── Exam Results ───
        exam_results = [
            ExamResult(id="result-1", exam_id="exam-1", student_id="student-1", student_name="Arjun Patel", marks_obtained=85, total_marks=100, percentage=85.0, grade="A"),
            ExamResult(id="result-2", exam_id="exam-1", student_id="student-2", student_name="Priya Sharma", marks_obtained=92, total_marks=100, percentage=92.0, grade="A+"),
            ExamResult(id="result-3", exam_id="exam-1", student_id="student-3", student_name="Rahul Verma", marks_obtained=72, total_marks=100, percentage=72.0, grade="B"),
            ExamResult(id="result-4", exam_id="exam-1", student_id="student-4", student_name="Ananya Gupta", marks_obtained=88, total_marks=100, percentage=88.0, grade="A"),
            ExamResult(id="result-5", exam_id="exam-2", student_id="student-1", student_name="Arjun Patel", marks_obtained=22, total_marks=25, percentage=88.0, grade="A"),
            ExamResult(id="result-6", exam_id="exam-2", student_id="student-3", student_name="Rahul Verma", marks_obtained=18, total_marks=25, percentage=72.0, grade="B"),
            ExamResult(id="result-7", exam_id="exam-4", student_id="student-1", student_name="Arjun Patel", marks_obtained=78, total_marks=100, percentage=78.0, grade="B+"),
            ExamResult(id="result-8", exam_id="exam-5", student_id="student-2", student_name="Priya Sharma", marks_obtained=45, total_marks=50, percentage=90.0, grade="A+"),
        ]
        session.add_all(exam_results)

        # ─── Calendar Events ───
        calendar_events = [
            CalendarEvent(id="cal-1", title="Republic Day", event_type="holiday", start_date="2025-01-26", all_day=True, color="#EF4444", created_by="Admin"),
            CalendarEvent(id="cal-2", title="Holi Festival Break", event_type="holiday", start_date="2025-03-14", end_date="2025-03-15", all_day=True, color="#EF4444", created_by="Admin"),
            CalendarEvent(id="cal-3", title="Mid-Semester Exam Week", event_type="exam", start_date="2025-03-03", end_date="2025-03-08", all_day=True, color="#F59E0B", created_by="Exam Cell"),
            CalendarEvent(id="cal-4", title="Annual Tech Summit", event_type="event", start_date="2025-02-15", end_date="2025-02-16",
                          description="Two-day tech summit with industry speakers and workshops", location="Main Auditorium", all_day=True, color="#3B82F6", created_by="Admin"),
            CalendarEvent(id="cal-5", title="Parent-Teacher Meeting", event_type="meeting", start_date="2025-02-22",
                          description="Semester progress review with parents", location="Conference Hall", all_day=False, color="#8B5CF6", created_by="Dean's Office"),
            CalendarEvent(id="cal-6", title="End-Semester Exam Week", event_type="exam", start_date="2025-04-21", end_date="2025-04-30", all_day=True, color="#F59E0B", created_by="Exam Cell"),
            CalendarEvent(id="cal-7", title="Summer Vacation Begins", event_type="holiday", start_date="2025-05-15", all_day=True, color="#10B981", created_by="Admin"),
            CalendarEvent(id="cal-8", title="Placement Drive — TCS", event_type="event", start_date="2025-02-10",
                          description="Campus recruitment drive by TCS. Pre-registered students only.", location="Seminar Hall B", all_day=True, color="#3B82F6", created_by="Placement Cell"),
            CalendarEvent(id="cal-9", title="Independence Day", event_type="holiday", start_date="2025-08-15", all_day=True, color="#EF4444", created_by="Admin"),
            CalendarEvent(id="cal-10", title="Sports Week", event_type="event", start_date="2025-03-20", end_date="2025-03-25",
                          description="Inter-department sports competition", location="Campus Ground", all_day=True, color="#10B981", created_by="Sports Cell"),
            CalendarEvent(id="cal-11", title="Fee Payment Deadline — Sem 2", event_type="deadline", start_date="2025-01-31", all_day=True, color="#DC2626", created_by="Finance Office"),
            CalendarEvent(id="cal-12", title="College Foundation Day", event_type="event", start_date="2025-04-10",
                          description="Celebrating our founding anniversary", location="Main Campus", all_day=True, color="#6366F1", created_by="Admin"),
        ]
        session.add_all(calendar_events)

        # ─── Store Products ───
        store_products = [
            StoreProduct(id="prod-1", name="College T-Shirt (White)", category="Uniforms", price=599, stock=120,
                         description="Official college t-shirt with embroidered logo", sku="UNI-TSH-W"),
            StoreProduct(id="prod-2", name="College Hoodie (Navy Blue)", category="Uniforms", price=1299, stock=80,
                         description="Premium fleece hoodie with college crest", sku="UNI-HOD-NB"),
            StoreProduct(id="prod-3", name="Lab Coat (White)", category="Uniforms", price=450, stock=200,
                         description="Standard lab coat for laboratory sessions", sku="UNI-LAB-W"),
            StoreProduct(id="prod-4", name="DSA Textbook — Cormen", category="Books", price=799, stock=45,
                         description="Introduction to Algorithms by CLRS", sku="BK-DSA-001"),
            StoreProduct(id="prod-5", name="DBMS Textbook — Korth", category="Books", price=650, stock=38,
                         description="Database System Concepts by Silberschatz", sku="BK-DBMS-001"),
            StoreProduct(id="prod-6", name="Engineering Drawing Kit", category="Stationery", price=350, stock=150,
                         description="Complete drawing kit with compass, ruler, and templates", sku="STN-EDK-001"),
            StoreProduct(id="prod-7", name="College ID Card Holder", category="Accessories", price=99, stock=300,
                         description="Branded lanyard with card holder", sku="ACC-IDH-001"),
            StoreProduct(id="prod-8", name="College Backpack", category="Accessories", price=1499, stock=60,
                         description="30L laptop backpack with college branding", sku="ACC-BAG-001"),
            StoreProduct(id="prod-9", name="Exam Pad (Set of 5)", category="Stationery", price=120, stock=500,
                         description="A4 answer booklets for examinations", sku="STN-EXP-005"),
            StoreProduct(id="prod-10", name="Sports Jersey", category="Uniforms", price=899, stock=90,
                         description="Polyester sports jersey with department name", sku="UNI-SPT-001"),
        ]
        session.add_all(store_products)
        await session.flush()  # products must exist before store_orders

        # ─── Store Orders ───
        store_orders = [
            StoreOrder(id="ord-1", student_id="student-1", student_name="Arjun Patel", product_id="prod-1", product_name="College T-Shirt (White)",
                       quantity=2, unit_price=599, total=1198, status="delivered", order_date="2024-09-10"),
            StoreOrder(id="ord-2", student_id="student-2", student_name="Priya Sharma", product_id="prod-2", product_name="College Hoodie (Navy Blue)",
                       quantity=1, unit_price=1299, total=1299, status="delivered", order_date="2024-09-12"),
            StoreOrder(id="ord-3", student_id="student-3", student_name="Rahul Verma", product_id="prod-4", product_name="DSA Textbook — Cormen",
                       quantity=1, unit_price=799, total=799, status="confirmed", order_date="2024-11-05"),
            StoreOrder(id="ord-4", student_id="student-4", student_name="Ananya Gupta", product_id="prod-6", product_name="Engineering Drawing Kit",
                       quantity=1, unit_price=350, total=350, status="pending", order_date="2024-11-14"),
            StoreOrder(id="ord-5", student_id="student-1", student_name="Arjun Patel", product_id="prod-8", product_name="College Backpack",
                       quantity=1, unit_price=1499, total=1499, status="pending", order_date="2024-11-15"),
        ]
        session.add_all(store_orders)

        # ─── Vendors ───
        vendors = [
            Vendor(id="ven-1", name="Dell India Pvt. Ltd.", contact_person="Suresh Menon", email="enterprise@dell.in", phone="+91-80-46767676",
                   category="IT & Hardware", address="DLF Cyber City, Gurugram", gst_no="06AAACL3170I1Z5", status="active", contract_start="2024-01-01", contract_end="2025-12-31", rating="4"),
            Vendor(id="ven-2", name="Sodexo India Services", contact_person="Anil Sharma", email="contracts@sodexo.in", phone="+91-22-45678901",
                   category="Catering", address="BKC, Mumbai", gst_no="27AACCS4758E1ZV", status="active", contract_start="2024-04-01", contract_end="2025-03-31", rating="3"),
            Vendor(id="ven-3", name="ServTech Facility Mgmt.", contact_person="Meera Krishnan", email="ops@servtech.in", phone="+91-44-23456789",
                   category="Maintenance", address="Anna Nagar, Chennai", gst_no="33AABCS1234E1ZQ", status="active", contract_start="2024-06-01", contract_end="2025-05-31", rating="4"),
            Vendor(id="ven-4", name="City Bus Transport Co.", contact_person="Rajendra Prasad", email="fleet@citybustransport.in", phone="+91-80-34567890",
                   category="Transport", address="Peenya Industrial Area, Bengaluru", gst_no="29AABCC5678E1ZX", status="active", contract_start="2024-08-01", contract_end="2025-07-31", rating="5"),
            Vendor(id="ven-5", name="Sapna Book House", contact_person="Lakshmi Narasimhan", email="bulk@sapnabooks.in", phone="+91-80-23456780",
                   category="Stationery & Books", address="Gandhinagar, Bengaluru", gst_no="29AABCS9876E1ZP", status="active", contract_start="2024-01-01", contract_end="2025-12-31", rating="5"),
            Vendor(id="ven-6", name="UniForm Hub India", contact_person="Pradeep Jain", email="sales@uniformhub.in", phone="+91-11-45678901",
                   category="Uniforms", address="Karol Bagh, New Delhi", gst_no="07AABCU1234E1Z3", status="inactive", contract_start="2023-01-01", contract_end="2024-06-30", rating="3"),
        ]
        session.add_all(vendors)

        await session.commit()

        print("✅ Database seeded successfully!")
        print(f"   👤 Users:           {len(users)}")
        print(f"   📚 Courses:         {len(courses)}")
        print(f"   💰 Fees:            {len(fees)}")
        print(f"   📋 Attendance:      {len(att_records)}")
        print(f"   📰 News:            {len(news)}")
        print(f"   🔔 Notifications:   {len(notifications)}")
        print(f"   🚌 Buses:           {len(buses)}")
        print(f"   📢 Complaints:      {len(complaints)}")
        print(f"   📖 Library Books:   {len(library_books)}")
        print(f"   📄 Documents:       {len(documents)}")
        print(f"   💼 Salary Slips:    {len(salary_slips)}")
        print(f"   🏖️  Leave Requests:  {len(leave_requests)}")
        print(f"   💸 Expenses:        {len(expenses)}")
        print(f"   📊 Budgets:         {len(budgets)}")
        print(f"   📝 Exams:           {len(exams)}")
        print(f"   📈 Exam Results:    {len(exam_results)}")
        print(f"   📅 Calendar Events: {len(calendar_events)}")
        print(f"   🛒 Store Products:  {len(store_products)}")
        print(f"   🛍️  Store Orders:    {len(store_orders)}")
        print(f"   🏢 Vendors:         {len(vendors)}")
        print(f"   📦 Inventory:       {len(inventory)}")
        print(f"   🎯 Leads:           {len(leads)}")
        print(f"   ─────────────────────────")
        print(f"   Demo accounts (all password: admin123):")
        for u in users:
            print(f"     {u.role:16} → {u.email}")


if __name__ == "__main__":
    asyncio.run(seed())
