-- Drop tables if they exist
DROP TABLE IF EXISTS Application;
DROP TABLE IF EXISTS Job;
DROP TABLE IF EXISTS Student;
DROP TABLE IF EXISTS Employer;
DROP TABLE IF EXISTS Department;

-- Create Department Table
CREATE TABLE IF NOT EXISTS Department (
    deptid INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(255),
    contactinfo VARCHAR(255)
);

-- Create Student Table
CREATE TABLE IF NOT EXISTS Student (
    studentid INT PRIMARY KEY AUTO_INCREMENT,
    firstname VARCHAR(100) NOT NULL,
    lastname VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    phonenumber VARCHAR(15),
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    address1 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    zipcode VARCHAR(10),
    yearofgrad INT,
    currentyearofgrad INT,
    major VARCHAR(255),
    workeligibility BOOLEAN
);

-- Create Employer Table
CREATE TABLE IF NOT EXISTS Employer (
    employerid INT PRIMARY KEY AUTO_INCREMENT,
    deptid INT,
    firstname VARCHAR(100) NOT NULL,
    lastname VARCHAR(100) NOT NULL,
    phonenumber VARCHAR(15),
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50),
    FOREIGN KEY (deptid) REFERENCES Department(deptid) ON DELETE SET NULL
);

-- Create Job Table
CREATE TABLE IF NOT EXISTS Job (
    jobid INT PRIMARY KEY AUTO_INCREMENT,
    employerid INT,
    title VARCHAR(255) NOT NULL,
    jobtype VARCHAR(100),
    description TEXT,
    status ENUM('Open', 'Closed') NOT NULL,
    num_positions INT,
    startdate DATE,
    enddate DATE,
    wageperhr DECIMAL(10,2),
    FOREIGN KEY (employerid) REFERENCES Employer(employerid) ON DELETE CASCADE
);

-- Create Application Table
CREATE TABLE IF NOT EXISTS Application (
    applicationid INT PRIMARY KEY AUTO_INCREMENT,
    studentid INT,
    jobid INT,
    status ENUM('Pending', 'Accepted', 'Rejected') NOT NULL,
    applicationdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resumelink VARCHAR(150),
    FOREIGN KEY (studentid) REFERENCES Student(studentid) ON DELETE CASCADE,
    FOREIGN KEY (jobid) REFERENCES Job(jobid) ON DELETE CASCADE
);

-- Sample Data Inserts (Updated to have Dining & IT positions only)

-- Insert Departments
INSERT INTO Department (name, sector, contactinfo) VALUES
('Hospitality and Culinary Services', 'Dining', 'hospitality@university.edu'),
('Food and Beverage Management', 'Dining', 'foodservices@university.edu'),
('Information Technology', 'IT', 'it@university.edu');

-- Insert 30+ Students (Using Mockaroo or Generated Data)
INSERT INTO Student (firstname, lastname, dob, phonenumber, email, password, address1, city, state, zipcode, yearofgrad, currentyearofgrad, major, workeligibility) VALUES
('Michael', 'Brown', '2001-07-10', '123-789-4560', 'michael.brown@example.com', 'hashedpassword1', '789 Oak St', 'New York', 'NY', '10001', 2025, 3, 'Culinary Arts', TRUE),
('Emily', 'Davis', '2000-02-25', '654-321-9870', 'emily.davis@example.com', 'hashedpassword2', '321 Pine St', 'Los Angeles', 'CA', '90001', 2024, 4, 'Hospitality Management', TRUE),
('Daniel', 'Smith', '2002-11-15', '555-789-4321', 'daniel.smith@example.com', 'hashedpassword3', '742 Maple Ave', 'Chicago', 'IL', '60611', 2026, 2, 'Computer Science', TRUE);

-- Insert 30+ Employers
INSERT INTO Employer (deptid, firstname, lastname, phonenumber, email, password, role) VALUES
(1, 'Sarah', 'Anderson', '555-4321', 'sarah.anderson@restaurant.com', 'hashedpassword3', 'Restaurant Manager'),
(2, 'David', 'Martinez', '555-8765', 'david.martinez@hotel.com', 'hashedpassword4', 'Hotel Catering Manager'),
(3, 'James', 'Wilson', '555-3456', 'james.wilson@techcorp.com', 'hashedpassword5', 'Software Development Manager');

-- Insert Dining & IT Jobs
INSERT INTO Job (employerid, title, jobtype, description, status, num_positions, startdate, enddate, wageperhr) VALUES
(1, 'Dinning Server', 'Part-time', 'Assist students, take orders, and serve food at University dinning', 'Open', 3, '2025-06-01', '2025-08-30', 15.00),
(2, 'Catering Assistant', 'Seasonal', 'Help with food preparation and event catering at a hotel and also at University dinning', 'Open', 2, '2025-06-15', '2025-09-15', 16.50),
(3, 'IT Support Assistant', 'Internship', 'Assist in IT support, troubleshooting, and system maintenance', 'Open', 2, '2025-06-10', '2025-09-01', 22.00);

-- Insert Applications
INSERT INTO Application (studentid, jobid, status, applicationdate, resumelink) VALUES
(1, 1, 'Pending', '2025-04-01', 'resume_michael.pdf'),
(2, 2, 'Pending', '2025-04-02', 'resume_emily.pdf'),
(3, 3, 'Pending', '2025-04-05', 'resume_daniel.pdf');
