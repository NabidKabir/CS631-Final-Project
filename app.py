from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from sqlalchemy import func, select
from dotenv import load_dotenv
from datetime import datetime, date
from decimal import Decimal
import os

app = Flask(__name__)

load_dotenv()

db_user = os.environ["DB_USER"]
db_pass = os.environ["DB_PASS"]
db_name = os.environ["DB_NAME"]
secret_key = os.environ["SECRET_KEY"]

if not all([db_user, db_pass, db_name, secret_key]):
    raise EnvironmentError("Missing required environment variables.")

app.config["SECRET_KEY"] = secret_key
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://{db_user}:{db_pass}@localhost/{db_name}".format(
    db_user = db_user, db_pass = db_pass, db_name = db_name
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Division(db.Model):
    __tablename__ = 'Division'
    Division_Name = db.Column(db.String(100), primary_key=True)
    Head_Employee_No = db.Column(db.Integer, db.ForeignKey('Employee.Employee_No'), unique=True)
    departments = db.relationship('Department', backref='division', lazy=True)
    employees = db.relationship('Employee', foreign_keys='Employee.Division_Name', backref='direct_division', lazy=True)  

class Employee(db.Model):
    __tablename__ = "Employee"
    Employee_No = db.Column(db.Integer, primary_key=True)
    Employee_Name = db.Column(db.String(200))
    Phone_Number = db.Column(db.String(20))
    Title = db.Column(db.String(100), db.ForeignKey('EmployeeTitle.Title'))

    Department_Name = db.Column(db.String(100), db.ForeignKey('Department.Department_Name'), nullable=True) 
    Division_Name = db.Column(db.String(100), db.ForeignKey('Division.Division_Name'), nullable=True)

    Is_Hourly = db.Column(db.Boolean, default=False)
    Hourly_Rate = db.Column(db.Numeric(10, 2))

    projects_assigned = db.relationship(
        'EmployeeProject', 
        back_populates='employee', 
        lazy=True,
        primaryjoin="and_(Employee.Employee_No == EmployeeProject.Employee_No, EmployeeProject.Date_Ended == None)"
    )
    payroll_history = db.relationship('PayrollHistory', backref='employee', lazy=True)

    projects_managed = db.relationship('Project', back_populates='manager', lazy=True)

    Is_Active = db.Column(db.Boolean, default=True)

class Department(db.Model):
    __tablename__ = 'Department'
    Department_Name = db.Column(db.String(100), primary_key=True)
    Budget = db.Column(db.Numeric(12, 2))
    Division_Name = db.Column(db.String(100), db.ForeignKey('Division.Division_Name'))
    Head_Employee_No = db.Column(db.Integer, db.ForeignKey('Employee.Employee_No'), unique=True)
    employees = db.relationship('Employee', foreign_keys='Employee.Department_Name', backref='department', lazy=True)
    rooms = db.relationship('DepartmentRoom', backref='department', lazy=True)

class Project(db.Model):
    __tablename__ = 'Project'
    Project_No = db.Column(db.Integer, primary_key=True)
    Budget = db.Column(db.Numeric(12, 2))
    Date_Started = db.Column(db.Date)
    Date_Ended = db.Column(db.Date)
    Manager_Employee_No = db.Column(db.Integer, db.ForeignKey('Employee.Employee_No'), unique=True)
    employees_on_project = db.relationship('EmployeeProject', back_populates='project', lazy=True)
    milestones = db.relationship('ProjectMilestone', back_populates='project', lazy=True)
    manager = db.relationship('Employee', back_populates='projects_managed', lazy=True)

class Building(db.Model):
    __tablename__ = 'Building'
    Building_Code = db.Column(db.String(10), primary_key=True)
    Building_Name = db.Column(db.String(200))
    Year_Bought = db.Column(db.Integer) 
    Cost = db.Column(db.Numeric(12, 2))
    rooms = db.relationship('Room', backref='building', lazy=True)

class Room(db.Model):
    __tablename__ = 'Room'
    Office_Number = db.Column(db.Integer, primary_key=True)
    Square_Feet = db.Column(db.Integer)
    Type = db.Column(db.String(50))
    Building_Code = db.Column(db.String(20), db.ForeignKey('Building.Building_Code'))
    employee_rooms = db.relationship('EmployeeRoom', backref='room_assignment', lazy=True)
    department_rooms = db.relationship('DepartmentRoom', backref='room_office', lazy=True)

class EmployeeTitle(db.Model):
    __tablename__ = 'EmployeeTitle'
    Title = db.Column(db.String(100), primary_key=True)
    Salary = db.Column(db.Numeric(12, 2))

class EmployeeRoom(db.Model):
    __tablename__ = 'EmployeeRoom'
    Employee_No = db.Column(db.Integer, db.ForeignKey('Employee.Employee_No'), primary_key=True)
    Room_Number = db.Column(db.Integer, db.ForeignKey('Room.Office_Number'), unique=True)

class DepartmentRoom(db.Model):
    __tablename__ = 'DepartmentRoom'
    Department_Name = db.Column(db.String(100), db.ForeignKey('Department.Department_Name'), primary_key=True)
    Room_Number = db.Column(db.Integer, db.ForeignKey('Room.Office_Number'), primary_key=True)

class EmployeeProject(db.Model):
    __tablename__ = 'EmployeeProject'
    Employee_No = db.Column(db.Integer, db.ForeignKey('Employee.Employee_No'), primary_key=True)
    Project_No = db.Column(db.Integer, db.ForeignKey('Project.Project_No'), primary_key=True)
    Role = db.Column(db.String(100))
    Hours_Worked = db.Column(db.Numeric(10, 2))
    Date_Started = db.Column(db.Date)
    Date_Ended = db.Column(db.Date)

    employee = db.relationship('Employee', back_populates='projects_assigned')
    project = db.relationship('Project', back_populates='employees_on_project')
    #employees_on_project = db.relationship('EmployeeProject', back_populates='project', lazy=True)

class PayrollHistory(db.Model):
    __tablename__ = 'Payroll_History'
    Payroll_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Employee_No = db.Column(db.Integer, db.ForeignKey('Employee.Employee_No'))
    Payment_Date = db.Column(db.Date)
    Gross_Pay = db.Column(db.Numeric(12, 2))
    Federal_Tax = db.Column(db.Numeric(12, 2))
    State_Tax = db.Column(db.Numeric(12, 2))
    Other_Tax = db.Column(db.Numeric(12, 2)) 
    Net_Pay = db.Column(db.Numeric(12, 2))

class ProjectMilestone(db.Model):
    __tablename__ = 'ProjectMilestone'
    Milestone_No = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Project_No = db.Column(db.Integer, db.ForeignKey('Project.Project_No'), nullable=False)
    milestone_description = db.Column(db.Text, nullable=False)
    Date_Logged = db.Column(db.Date, nullable=False)
    
    project = db.relationship('Project', back_populates='milestones', lazy=True)

#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
# Main Dashboard
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
@app.route('/')
def main_dashboard():
    """Renders the main application hub with links to HR and PM applications."""
    return render_template('main_dashboard.html')

#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
# Human Resources/Payment Routes
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
@app.route('/hr_dashboard')
def hr_dashboard():
    """Renders the main employee list dashboard, including project data."""
    try:
        # Fetch all employees.
        employees = db.session.query(Employee).filter_by(Is_Active=True).options( 
            db.joinedload(Employee.projects_assigned)
        ).all()
        

        return render_template('hr_dashboard.html', employees=employees)
    except Exception as e:
        flash(f"Database Error: Could not fetch employee data. Error: {e}", 'error')
        return render_template('hr_dashboard.html', employees=[])  
    
@app.route('/payroll/<int:emp_id>', methods=['POST'])
def generate_payroll(emp_id):
    """Calculates and records payroll for a specific employee."""
    employee = Employee.query.get_or_404(emp_id)
    
    # Tax Rates
    FEDERAL_TAX_RATE = 0.10
    STATE_TAX_RATE = 0.05
    OTHER_TAX_RATE = 0.03
    
    try:
        gross_pay = 0.0
        
        if employee.Is_Hourly:
            # Get hours from the form submission (from index.html)
            hours_str = request.form.get('hours')
            if not hours_str:
                flash("Hourly employee payroll requires hours worked.", 'warning')
                return redirect(url_for('hr_dashboard'))
            
            hours_worked = float(hours_str)
            gross_pay = float(employee.Hourly_Rate) * hours_worked
        else:

            title_obj = EmployeeTitle.query.get(employee.Title)
            if title_obj:
                # Assuming this is the gross monthly salary
                gross_pay = float(title_obj.Salary) 
            else:
                flash(f"Error: Salaried employee {employee.Employee_Name} has no defined salary.", 'error')
                return redirect(url_for('hr_dashboard'))

        gross_pay = round(gross_pay, 2)
        fed_tax = round(gross_pay * FEDERAL_TAX_RATE, 2)
        state_tax = round(gross_pay * STATE_TAX_RATE, 2)
        other_tax = round(gross_pay * OTHER_TAX_RATE, 2)
        total_deductions = fed_tax + state_tax + other_tax
        
        net_pay = round(gross_pay - total_deductions, 2)
        
        new_record = PayrollHistory(
            Employee_No=emp_id,
            Payment_Date=datetime.now().date(),
            Gross_Pay=gross_pay,
            Federal_Tax=fed_tax,
            State_Tax=state_tax,
            Other_Tax=other_tax,
            Net_Pay=net_pay
        )
        
        db.session.add(new_record)
        db.session.commit()
        
        flash(f"Successfully processed ${net_pay:.2f} net pay for {employee.Employee_Name}.", 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f"Payroll failed for {employee.Employee_Name}. Error: {e}", 'error')
        
    return redirect(url_for('hr_dashboard'))

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    """Displays the form or processes the form submission to add a new employee, 
       creating new titles if necessary."""
       
    titles = EmployeeTitle.query.with_entities(EmployeeTitle.Title).all()
    departments = Department.query.with_entities(Department.Department_Name).all()
    divisions = Division.query.with_entities(Division.Division_Name).all()
    
    context = {
        'titles': [t[0] for t in titles],
        'departments': [d[0] for d in departments],
        'divisions': [d[0] for d in divisions]
    }
                               
    if request.method == 'POST':
        try:
            last_employee = Employee.query.order_by(Employee.Employee_No.desc()).first()
            new_emp_no = (last_employee.Employee_No + 1) if last_employee else 1001

            employee_name = request.form['employee_name']
            phone_number = request.form['phone_number']
            title = request.form['title']
            
            pay_type = request.form['pay_type']
            is_hourly = (pay_type == 'hourly')
            hourly_rate = request.form.get('hourly_rate')
            salary_rate = request.form.get('salary_rate') # NEW: Capture salary input

            affiliation_type = request.form['affiliation_type']
            dept_name = request.form.get('department_name') if affiliation_type == 'department' else None
            div_name = request.form.get('division_name') if affiliation_type == 'division' else None
            

            existing_title = EmployeeTitle.query.get(title)
            
            if not existing_title:
                # Determine the salary to save: use the submitted salary if salaried, otherwise 0.00
                if is_hourly or not salary_rate:
                    # If hourly, the salary field is irrelevant/empty, so set title salary to 0.00
                    default_salary = Decimal('0.00') 
                else:
                    # If salaried, use the salary entered by the user to set the title's salary
                    default_salary = Decimal(salary_rate)

                new_title = EmployeeTitle(Title=title, Salary=default_salary) 
                db.session.add(new_title)
            
            if dept_name and not Department.query.get(dept_name):
                 flash(f"Error: Department '{dept_name}' not found.", 'error')
                 return render_template('add_employee.html', **context)
            
            if div_name and not Division.query.get(div_name):
                 flash(f"Error: Division '{div_name}' not found.", 'error')
                 return render_template('add_employee.html', **context)
            

            new_employee = Employee(
                Employee_No=new_emp_no,
                Employee_Name=employee_name,
                Phone_Number=phone_number,
                Title=title,
                Department_Name=dept_name,
                Division_Name=div_name,
                Is_Hourly=is_hourly,
                Hourly_Rate=Decimal(hourly_rate) if hourly_rate else None
            )


            db.session.add(new_employee)
            db.session.commit()
            flash(f"Employee {employee_name} ({new_emp_no}) successfully added! Title '{title}' created/used.", 'success')
            return redirect(url_for('hr_dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error adding employee: {e}", 'error')

            return render_template('add_employee.html', **context)

    return render_template('add_employee.html', **context)

@app.route('/edit_employee/<int:emp_id>', methods=['GET', 'POST'])
def edit_employee(emp_id):
    """Handles displaying the pre-filled form and processing updates for an employee."""
    
    # Fetch necessary data for context (titles, departments, divisions)
    titles = EmployeeTitle.query.with_entities(EmployeeTitle.Title).all()
    departments = Department.query.with_entities(Department.Department_Name).all()
    divisions = Division.query.with_entities(Division.Division_Name).all()
    
    context = {
        'titles': [t[0] for t in titles],
        'departments': [d[0] for d in departments],
        'divisions': [d[0] for d in divisions]
    }
    
    employee = Employee.query.get_or_404(emp_id)

    if request.method == 'GET':
        return render_template('edit_employee.html', employee=employee, **context)

    if request.method == 'POST':
        try:

            # Basic Info
            employee.Employee_Name = request.form['employee_name']
            employee.Phone_Number = request.form['phone_number']
            new_title = request.form['title']
            
            # Payroll Info
            pay_type = request.form['pay_type']
            is_hourly = (pay_type == 'hourly')
            hourly_rate = request.form.get('hourly_rate')
            salary_rate = request.form.get('salary_rate')

            employee.Is_Hourly = is_hourly
            employee.Hourly_Rate = Decimal(hourly_rate) if hourly_rate and is_hourly else None

            if new_title != employee.Title: 
                existing_title_obj = EmployeeTitle.query.get(new_title)
                
                if not existing_title_obj:
                    if is_hourly or not salary_rate:
                        default_salary = Decimal('0.00') 
                    else:
                        default_salary = Decimal(salary_rate)

                    new_title_obj = EmployeeTitle(Title=new_title, Salary=default_salary)
                    db.session.add(new_title_obj)
            
            employee.Title = new_title 

            affiliation_type = request.form['affiliation_type']
            
            if affiliation_type == 'department':
                employee.Department_Name = request.form.get('department_name')
                employee.Division_Name = None
            elif affiliation_type == 'division':
                employee.Division_Name = request.form.get('division_name')
                employee.Department_Name = None
            
            db.session.commit()
            flash(f"Employee {employee.Employee_Name}'s record (ID: {emp_id}) updated successfully!", 'success')
            return redirect(url_for('hr_dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error updating employee {employee.Employee_Name}. Error: {e}", 'error')
            return render_template('edit_employee.html', employee=employee, **context)
  
@app.route('/fire_employee/<int:emp_id>', methods=['POST'])
def fire_employee(emp_id):
    employee = Employee.query.get_or_404(emp_id)
    
    try:
        is_div_head = Division.query.filter_by(Head_Employee_No=emp_id).first()
        is_dept_head = Department.query.filter_by(Head_Employee_No=emp_id).first()
        
        if is_div_head or is_dept_head:
            db.session.rollback()
            # Prevent firing if the employee is still leading a team
            flash(f"Cannot terminate {employee.Employee_Name}. They must first be relieved of their duties as a Division Head or Department Head.", 'error')
            return redirect(url_for('hr_dashboard'))
            
        employee.Is_Active = False
        db.session.commit()
        flash(f"Employee {employee.Employee_Name} ({emp_id}) has been successfully terminated.", 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to terminate employee {employee.Employee_Name}. Error: {e}", 'error')
        
    return redirect(url_for('hr_dashboard'))

@app.route('/payroll_history')
def payroll_history():
    try:
        history_records = db.session.query(PayrollHistory).options(
            joinedload(PayrollHistory.employee)
        ).order_by(PayrollHistory.Payment_Date.desc()).all()
        
        return render_template('payroll_history.html', records=history_records)
    
    except Exception as e:
        flash(f"Error fetching payroll history: {e}", 'error')
        return render_template('payroll_history.html', records=[])

#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
# Project Management Routes
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------    
@app.route('/pm_dashboard')
def pm_dashboard():
    """
    Renders the Project Management dashboard
    """
    try:

        projects = Project.query.options(
            db.joinedload(Project.manager),
            db.joinedload(Project.milestones)
        ).all()
        
        # Calculate Total Hours Worked per Project
        hours_query = db.session.query(
            EmployeeProject.Project_No,
            func.sum(EmployeeProject.Hours_Worked).label('total_hours')
        ).group_by(EmployeeProject.Project_No).all()
        
        hours_map = {item.Project_No: item.total_hours for item in hours_query}
        
        # Calculate Active Team Size per Project
        team_size_query = db.session.query(
            EmployeeProject.Project_No,
            func.count(EmployeeProject.Employee_No).label('active_team_size')
        ).filter(EmployeeProject.Date_Ended == None
        ).group_by(EmployeeProject.Project_No).all()

        team_size_map = {item.Project_No: item.active_team_size for item in team_size_query}

        projects_with_stats = []
        for project in projects:
            
            total_milestones = len(project.milestones)
            
            project_data = {
                'project': project,
                'team_count': team_size_map.get(project.Project_No, 0),
                'total_hours': hours_map.get(project.Project_No, Decimal('0.00')),
                'total_milestones': total_milestones
            }
            projects_with_stats.append(project_data)
            
        return render_template('pm_dashboard.html', projects=projects_with_stats)
        
    except Exception as e:
        print(f"ERROR: Failed to load PM Dashboard data: {e}") 
        flash(f"Error fetching projects: {e}", 'error')
        return render_template('pm_dashboard.html', projects=[])
    
@app.route('/project/<int:project_id>')
def view_project(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        
        team_assignments = EmployeeProject.query.filter(
            EmployeeProject.Project_No == project_id,
            EmployeeProject.Date_Ended.is_(None)
        ).options(joinedload(EmployeeProject.employee)).all()
        
        # Calculate total hours (for display in summary card)
        total_hours_result = db.session.query(
            func.sum(EmployeeProject.Hours_Worked).label('total_hours')
        ).filter(EmployeeProject.Project_No == project_id).scalar()
        
        total_hours = total_hours_result if total_hours_result is not None else Decimal('0.00')

        # --- Milestones ---
        milestones = ProjectMilestone.query.filter_by(Project_No=project_id).order_by(ProjectMilestone.Date_Logged.desc()).all()
        milestone_stats = {'total': len(milestones)}

        all_employees = Employee.query.filter_by(Is_Active=True).order_by(Employee.Employee_Name).all()
        
        context = {
            'project': project,
            'team': team_assignments,
            'total_hours': total_hours,
            'milestones': milestones,
            'milestone_stats': milestone_stats,
            'all_employees': all_employees
        }
        
        return render_template('view_project.html', **context)
        
    except Exception as e:
        print(f"Error fetching project data in view_project: {e}")
        flash(f"Error fetching project data: {e}", 'error')
        return redirect(url_for('pm_dashboard'))

@app.route('/create_project', methods=['GET', 'POST'])
def create_project():
    """Handles creating a new project"""
    
    active_employees = Employee.query.filter_by(Is_Active=True).order_by(Employee.Employee_Name).all()

    if request.method == 'POST':
        try:
            project_no_str = request.form.get('project_no')
            budget_str = request.form.get('budget')
            date_started_str = request.form.get('date_started')
            manager_id = request.form.get('manager_employee_no')
            
            if not all([project_no_str, budget_str, date_started_str, manager_id]):
                flash("All required project fields must be filled out.", 'error')
                return render_template('create_project.html', employees=active_employees)

            project_no = int(project_no_str)
            budget = Decimal(budget_str)
            date_started = datetime.strptime(date_started_str, '%Y-%m-%d').date()
            manager_id = int(manager_id)
            
            if Project.query.get(project_no):
                flash(f"Project Number P{project_no} already exists. Please choose a unique number.", 'error')
                return render_template('create_project.html', employees=active_employees)

            existing_manager_project = Project.query.filter_by(Manager_Employee_No=manager_id, Date_Ended=None).first()
            if existing_manager_project:
                flash(f"Employee {manager_id} is already managing Project P{existing_manager_project.Project_No}. Please select a different manager.", 'error')
                return render_template('create_project.html', employees=active_employees)

            new_project = Project(
                Project_No=project_no, 
                Budget=budget,
                Date_Started=date_started,
                Manager_Employee_No=manager_id,
            )
            db.session.add(new_project)
            
            manager_assignment = EmployeeProject(
                Employee_No=manager_id,
                Project_No=new_project.Project_No,
                Role='Project Manager',
                Hours_Worked=Decimal('0.00'),
                Date_Started=date_started
            )
            db.session.add(manager_assignment)
            
            db.session.commit()
            
            flash(f"Project P{project_no} created successfully. Project Manager assigned.", 'success')
            return redirect(url_for('pm_dashboard'))
            
        except ValueError:
            db.session.rollback()
            flash("Invalid input for Project Number, Budget, or Employee ID. Please check the values.", 'error')
            return render_template('create_project.html', employees=active_employees)
        
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating project: {e}", 'error')
            return render_template('create_project.html', employees=active_employees)

    return render_template('create_project.html', employees=active_employees)

@app.route('/complete_project/<int:project_id>', methods=['POST'])
def complete_project(project_id): 
    """Handles marking a project as complete."""
    try:
        project = Project.query.get_or_404(project_id)

        if not project.Date_Ended:
            project.Date_Ended = date.today()
            
            active_assignments = EmployeeProject.query.filter_by(
                Project_No=project_id, 
                Date_Ended=None
            ).all()
            
            for assignment in active_assignments:
                assignment.Date_Ended = date.today()
            
            db.session.commit()
            flash(f"Project '{project.Project_No or project_id}' marked as complete, and all active team assignments have ended.", 'success')
        else:
            flash(f"Project '{project.Project_No or project_id}' was already complete.", 'info')

    except Exception as e:
        db.session.rollback()
        flash(f"Failed to complete project: {e}", 'error')
        
    return redirect(url_for('pm_dashboard'))

@app.route('/add_milestone/<int:project_id>', methods=['POST'])
def add_milestone(project_id):
    """Handles logging a new milestone for a project."""
    try:
        project = Project.query.get_or_404(project_id)
        
        description = request.form.get('milestone_description')
        date_logged_str = request.form.get('date_logged')

        if not all([description, date_logged_str]):
            flash("Milestone description and date are required.", 'error')
            return redirect(url_for('view_project', project_id=project_id))
        
        date_logged = datetime.strptime(date_logged_str, '%Y-%m-%d').date()

        new_milestone = ProjectMilestone(
            Project_No=project_id,
            milestone_description=description, 
            Date_Logged=date_logged
        )
        db.session.add(new_milestone)
        db.session.commit()
        
        flash(f"Milestone logged successfully for Project P{project_id}.", 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error logging milestone: {e}", 'error')
        
    return redirect(url_for('view_project', project_id=project_id))

@app.route('/add_team_member/<int:project_id>', methods=['POST'])
def add_team_member(project_id):
    """Handles adding an existing employee to a project team."""
    try:
        project = Project.query.get_or_404(project_id)

        employee_id = request.form.get('employee_no')
        role = request.form.get('role', 'Team Member').strip()
        date_started_str = request.form.get('date_started')

        if not all([employee_id, date_started_str]):
            flash("Employee and start date are required for assignment.", 'error')
            return redirect(url_for('view_project', project_id=project_id))

        employee_id = int(employee_id)
        date_started = datetime.strptime(date_started_str, '%Y-%m-%d').date()

        # Check for existing active assignment
        existing_assignment = EmployeeProject.query.filter_by(
            Project_No=project_id, 
            Employee_No=employee_id, 
            Date_Ended=None 
        ).first()

        if existing_assignment:
            flash(f"Employee {employee_id} is already actively assigned to this project.", 'warning')
        else:
            new_assignment = EmployeeProject(
                Project_No=project_id,
                Employee_No=employee_id,
                Role=role,
                Hours_Worked=Decimal('0.00'),
                Date_Started=date_started
            )
            db.session.add(new_assignment)
            db.session.commit()
            flash(f"Employee {employee_id} assigned as '{role}' to Project P{project_id}.", 'success')

    except Exception as e:
        db.session.rollback()
        flash(f"Error adding team member: {e}", 'error')
        
    return redirect(url_for('view_project', project_id=project_id))
    
if __name__ == '__main__':
    app.run(debug=True)