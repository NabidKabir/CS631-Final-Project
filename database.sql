-- ================================================================
-- DIVISION
-- ================================================================
CREATE TABLE Division(
    Division_Name VARCHAR(100) PRIMARY KEY,
    Head_Employee_No INT UNIQUE
);

-- ================================================================
-- DEPARTMENT
-- ================================================================
CREATE TABLE Department(
    Department_Name VARCHAR(100) PRIMARY KEY,
    Budget DECIMAL (12, 2),
    Division_Name VARCHAR(100),
    Head_Employee_No INT UNIQUE,

    FOREIGN KEY (Division_Name) REFERENCES Division(Division_Name)
);

-- ================================================================
-- BUILDING
-- ================================================================
CREATE TABLE Building(
    Building_Code VARCHAR(10) PRIMARY KEY,
    Building_Name VARCHAR(200),
    Year_Bought YEAR,
    Cost DECIMAL(12, 2)
);

-- ================================================================
-- PROJECT
-- ================================================================
CREATE TABLE Project(
    Project_No INT PRIMARY KEY,
    Budget DECIMAL(12, 2),
    Date_Started DATE,
    Date_Ended DATE,
    Manager_Employee_No INT UNIQUE
);

-- ================================================================
-- EMPLOYEE_TITLE
-- Defines standard salary for salaried employees based on title
-- ================================================================
CREATE TABLE EmployeeTitle(
    Title VARCHAR(100) PRIMARY KEY,
    Salary DECIMAL(12,2)
);

-- ================================================================
-- EMPLOYEE (UPDATED for HR requirements)
-- Supports salaried/hourly, direct division affiliation, and head roles
-- ================================================================
CREATE TABLE Employee(
    Employee_No INT PRIMARY KEY,
    Employee_Name VARCHAR(200),
    Phone_Number VARCHAR(20),
    Title VARCHAR(100),
    
    Department_Name VARCHAR(100), 
    

    Division_Name VARCHAR(100),
    

    Is_Hourly BOOLEAN DEFAULT FALSE,
    Hourly_Rate DECIMAL(10, 2),
    
    FOREIGN KEY (Title) REFERENCES EmployeeTitle(Title),
    FOREIGN KEY (Department_Name) REFERENCES Department(Department_Name),
    FOREIGN KEY (Division_Name) REFERENCES Division(Division_Name)

);

-- ================================================================
-- ROOM
-- ================================================================
CREATE TABLE Room (
    Office_Number INT PRIMARY KEY,
    Square_Feet INT,
    Type VARCHAR(50),
    Building_Code VARCHAR(20),
    
    FOREIGN KEY (Building_Code) REFERENCES Building(Building_Code)
);

-- ================================================================
-- EMPLOYEE_PROJECT (UPDATED for Project History)
-- Now tracks role, time spent, and specific dates for history reporting
-- ================================================================
CREATE TABLE EmployeeProject (
    Employee_No INT,
    Project_No INT,
    Role VARCHAR(100),
    Hours_Worked DECIMAL(10, 2), 
    Date_Started DATE,
    Date_Ended DATE,
    PRIMARY KEY (Employee_No, Project_No),

    FOREIGN KEY (Employee_No) REFERENCES Employee(Employee_No),
    FOREIGN KEY (Project_No) REFERENCES Project(Project_No)
);

-- ================================================================
-- PAYROLL_HISTORY (NEW TABLE)
-- Required for IRS and salary/tax history reporting
-- ================================================================
CREATE TABLE Payroll_History (
    Payroll_ID INT AUTO_INCREMENT PRIMARY KEY,
    Employee_No INT,
    Payment_Date DATE,
    Gross_Pay DECIMAL(12, 2),
    Federal_Tax DECIMAL(12, 2), -- 10%
    State_Tax DECIMAL(12, 2),   -- 5%
    Other_Tax DECIMAL(12, 2),   -- 3%
    Net_Pay DECIMAL(12, 2),
    
    FOREIGN KEY (Employee_No) REFERENCES Employee(Employee_No)
);

CREATE TABLE ProjectMilestone (
    Milestone_No INT PRIMARY KEY AUTO_INCREMENT, 
    Project_No INT NOT NULL,                    
    milestone_description TEXT NOT NULL,                  
    Date_Logged DATE NOT NULL,                

    FOREIGN KEY (Project_No) REFERENCES Project(Project_No)
);

-- ================================================================
-- Adding Foreign Keys for Head Employees
-- Note: It's best practice to add these after the Employee table is defined.
-- ================================================================
ALTER TABLE Division
ADD FOREIGN KEY (Head_Employee_No) REFERENCES Employee(Employee_No);

ALTER TABLE Department
ADD FOREIGN KEY (Head_Employee_No) REFERENCES Employee(Employee_No);

ALTER TABLE Project
ADD FOREIGN KEY (Manager_Employee_No) REFERENCES Employee(Employee_No);

-- ================================================================
-- Relational queries for populating database with fake data for testing.
-- ================================================================

INSERT INTO Building (Building_Code, Building_Name, Year_Bought, Cost) VALUES
('HQ01', 'Main Headquarters', 2005, 15000000.00),
('ANNX', 'West Annex Building', 2018, 5500000.00);

INSERT INTO Room (Office_Number, Square_Feet, Type, Building_Code) VALUES
(101, 200, 'Office', 'HQ01'),
(102, 350, 'Conference', 'HQ01'),
(201, 150, 'Office', 'HQ01'),
(301, 180, 'Office', 'ANNX'),
(302, 100, 'Storage', 'ANNX');

INSERT INTO EmployeeTitle (Title, Salary) VALUES
('CEO', 25000.00),         
('VP of Technology', 18000.00),
('Software Engineer L4', 10000.00),
('HR Coordinator', 6000.00),
('Project Technician', 0.00);

INSERT INTO Division (Division_Name, Head_Employee_No) VALUES
('Executive', NULL),
('Technology', NULL),
('Human Resources', NULL);

INSERT INTO Department (Department_Name, Budget, Division_Name, Head_Employee_No) VALUES
('Software Development', 1200000.00, 'Technology', NULL),
('IT Infrastructure', 500000.00, 'Technology', NULL),
('Recruitment', 150000.00, 'Human Resources', NULL);

INSERT INTO Employee (Employee_No, Employee_Name, Phone_Number, Title, Department_Name, Division_Name, Is_Hourly, Hourly_Rate) VALUES
--Salaried Employees
(1001, 'Alice Johnson', '555-1001', 'CEO', NULL, 'Executive', FALSE, NULL),           
(1002, 'Bob Smith', '555-1002', 'VP of Technology', NULL, 'Technology', FALSE, NULL), 
(1003, 'Charlie Brown', '555-1003', 'Software Engineer L4', 'Software Development', NULL, FALSE, NULL),
(1004, 'Dana Scully', '555-1004', 'HR Coordinator', 'Recruitment', NULL, FALSE, NULL), 
(1005, 'Eve Adams', '555-1005', 'HR Coordinator', NULL, 'Human Resources', FALSE, NULL),
-- Hourly Employees
(2001, 'Frank Miller', '555-2001', 'Project Technician', NULL, NULL, TRUE, 35.00),
(2002, 'Grace Lee', '555-2002', 'Project Technician', 'IT Infrastructure', NULL, TRUE, 45.50);


UPDATE Division SET Head_Employee_No = 1001 WHERE Division_Name = 'Executive';
UPDATE Division SET Head_Employee_No = 1002 WHERE Division_Name = 'Technology';


UPDATE Department SET Head_Employee_No = 1003 WHERE Department_Name = 'Software Development';
UPDATE Department SET Head_Employee_No = 1004 WHERE Department_Name = 'Recruitment';


INSERT INTO Project (Project_No, Budget, Date_Started, Date_Ended, Manager_Employee_No) VALUES
(101, 500000.00, '2025-01-15', '2025-06-30', 1003), 
(102, 120000.00, '2025-03-01', '2025-05-15', 1002);


INSERT INTO EmployeeRoom (Employee_No, Room_Number) VALUES
(1001, 101),
(1003, 201), 
(1004, 301); 


INSERT INTO DepartmentRoom (Department_Name, Room_Number) VALUES
('Software Development', 102), 
('Recruitment', 302);         


INSERT INTO EmployeeProject (Employee_No, Project_No, Role, Hours_Worked, Date_Started, Date_Ended) VALUES
(1003, 102, 'Lead Developer', 400.00, '2025-03-01', '2025-05-15'),
(2001, 101, 'Technician', 80.00, '2025-05-01', NULL),
(2002, 101, 'Engineer', 160.00, '2025-04-10', NULL);

INSERT INTO Payroll_History (Employee_No, Payment_Date, Gross_Pay, Federal_Tax, State_Tax, Other_Tax, Net_Pay) VALUES
(1001, '2025-11-30', 25000.00, 2500.00, 1250.00, 750.00, 20500.00);