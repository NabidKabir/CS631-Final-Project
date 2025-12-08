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
    -- Added Manager_Employee_No to explicitly track the project manager
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
    
    -- Department_Name is NULLABLE to allow employees affiliated directly with a Division
    Department_Name VARCHAR(100), 
    
    -- Added Division_Name for direct division employees
    Division_Name VARCHAR(100),
    
    -- Added flags for payroll
    Is_Hourly BOOLEAN DEFAULT FALSE,
    Hourly_Rate DECIMAL(10, 2),
    
    FOREIGN KEY (Title) REFERENCES EmployeeTitle(Title),
    FOREIGN KEY (Department_Name) REFERENCES Department(Department_Name),
    FOREIGN KEY (Division_Name) REFERENCES Division(Division_Name)
    -- You may also want to add FKs linking Head_Employee_No in Division/Department back here
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
-- EMPLOYEE_ROOM
-- ================================================================
CREATE TABLE EmployeeRoom (
    Employee_No INT PRIMARY KEY,
    Room_Number INT UNIQUE,

    FOREIGN KEY (Employee_No) REFERENCES Employee(Employee_No),
    FOREIGN KEY (Room_Number) REFERENCES Room(Office_Number)
);


-- ================================================================
-- DEPARTMENT_ROOM
-- ================================================================
CREATE TABLE DepartmentRoom (
    Department_Name VARCHAR(100),
    Room_Number INT,
    PRIMARY KEY (Department_Name, Room_Number),

    FOREIGN KEY (Department_Name) REFERENCES Department(Department_Name),
    FOREIGN KEY (Room_Number) REFERENCES Room(Office_Number)
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