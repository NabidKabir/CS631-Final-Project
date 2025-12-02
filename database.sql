--================================================================
--DIVISION
--================================================================
CREATE TABLE Division(
    Division_Name VARCHAR(100) PRIMARY KEY,
    Head_Employee_No INT UNIQUE
);

--================================================================
--DEPARTMENT
--================================================================
CREATE TABLE Department(
    Department_Name VARCHAR(100) PRIMARY KEY,
    Budget DECIMAL (12, 2),
    Division_Name VARCHAR(100),
    Head_Employee_No INT UNIQUE,

    FOREIGN KEY (Division_Name) REFERENCES Division(Division_Name)
);

--================================================================
--BUILDING
--================================================================
CREATE TABLE Building(
    Building_Code VARCHAR(10) PRIMARY KEY,
    Building_Name VARCHAR(200),
    Year_Bought YEAR,
    Cost DECIMAL(12, 2)
);

--================================================================
--PROJECT
--================================================================
CREATE TABLE Project(
    Project_No INT PRIMARY KEY,
    Budget DECIMAL(12, 2),
    Date_Started DATE,
    Date_Ended DATE
);

--================================================================
--EMPLOYEE_TITLE
--================================================================
CREATE TABLE EmployeeTitle(
    Title VARCHAR(100) PRIMARY KEY,
    Salary DECIMAL(12,2)
);

--================================================================
--EMPLOYEE
--================================================================
CREATE TABLE Employee(
    Employee_No INT PRIMARY KEY,
    Employee_Name VARCHAR(200),
    Phone_Number VARCHAR(20),
    Title VARCHAR(100),
    Department_Name VARCHAR(100),

    FOREIGN KEY Title REFERENCES Employee_Title(Title),
    FOREIGN KEY Department_Name REFERENCES Department(Department_Name)
);

--================================================================
--ROOM
--================================================================
CREATE TABLE Room (
    Office_Number INT PRIMARY KEY,
    Square_Feet INT,
    Type VARCHAR(50),
    Building_Code VARCHAR(20),
    
    FOREIGN KEY (Building_Code) REFERENCES Building(Building_Code)
);

--================================================================
--EMPLOYEE_ROOM
--================================================================
CREATE TABLE EmployeeRoom (
    Employee_No INT PRIMARY KEY,
    Room_Number INT UNIQUE,

    FOREIGN KEY (Employee_No) REFERENCES Employee(Employee_No),
    FOREIGN KEY (Room_Number) REFERENCES Room(Office_Number)
);


--================================================================
--DEPARTMENT_ROOM
--================================================================
CREATE TABLE DepartmentRoom (
    Department_Name VARCHAR(100),
    Room_Number INT,
    PRIMARY KEY (Department_Name, Room_Number),

    FOREIGN KEY (Department_Name) REFERENCES Department(Department_Name),
    FOREIGN KEY (Room_Number) REFERENCES Room(Office_Number)
);

--================================================================
--EMPLOYEE_PROJECT
--================================================================
CREATE TABLE EmployeeProject (
    Employee_No INT,
    Project_Number INT,
    PRIMARY KEY (Employee_No, Project_Number),

    FOREIGN KEY (Employee_No) REFERENCES Employee(Employee_No),
    FOREIGN KEY (Project_Number) REFERENCES Project(Project_Number)
);