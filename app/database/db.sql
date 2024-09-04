-- Create the extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


CREATE TABLE centre (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    location VARCHAR NOT NULL,
    region VARCHAR
);

CREATE TABLE directorate (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    name VARCHAR NOT NULL,
    centre_id UUID REFERENCES centre(id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE grade (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    name VARCHAR NOT NULL,
    min_sal DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    max_sal DECIMAL(10, 2) NOT NULL DEFAULT 0.00
);

CREATE TABLE employment_type (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    name VARCHAR NOT NULL,
    description VARCHAR,
    grade_id UUID REFERENCES grade(id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE staff_category (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    category VARCHAR NOT NULL
);

CREATE TABLE bio_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    title VARCHAR DEFAULT 'Other' NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    other_names VARCHAR(100),
    surname VARCHAR(100) NOT NULL,
    previous_name VARCHAR,
    gender VARCHAR DEFAULT 'Other' NOT NULL,
    date_of_birth DATE NOT NULL,
    nationality VARCHAR NOT NULL,
    hometown VARCHAR NOT NULL,
    religion VARCHAR,
    marital_status VARCHAR DEFAULT 'Other' NOT NULL,
    residential_addr VARCHAR NOT NULL,
    active_phone_number VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    ssnit_number VARCHAR NOT NULL,
    ghana_card_number VARCHAR NOT NULL,
    is_physically_challenged BOOLEAN NOT NULL,
    disability VARCHAR,
    image_col VARCHAR,
    registered_by  VARCHAR
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    bio_row_id UUID REFERENCES bio_data(id) ON DELETE CASCADE ON UPDATE CASCADE,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR,
    hashed_password VARCHAR NOT NULL,
    reset_pwd_token VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR DEFAULT 'user',
    failed_login_attempts  INTEGER  DEFAULT 0,
    account_locked_until  TIMESTAMPTZ,
    lock_count INTEGER DEFAULT 0
);


CREATE TABLE refresh_tokens(
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     created_at TIMESTAMPTZ DEFAULT NOW(),
     updated_at TIMESTAMPTZ DEFAULT NOW(),
     user_id UUID REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
     refresh_token VARCHAR,
     expiration_time  TIMESTAMPTZ NOT NULL
);


CREATE TABLE employment_details (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    bio_row_id UUID REFERENCES bio_data(id) ON DELETE CASCADE ON UPDATE CASCADE,
    date_of_first_appointment DATE NOT NULL,
    grade_on_first_appointment VARCHAR,
    grade_on_current_appointment_id UUID REFERENCES grade(id) ON DELETE CASCADE ON UPDATE CASCADE,
    directorate_id UUID REFERENCES directorate(id) ON DELETE CASCADE ON UPDATE CASCADE,
    employee_number VARCHAR UNIQUE NOT NULL,
    employment_type_id UUID REFERENCES employment_type(id) ON DELETE SET NULL ON UPDATE CASCADE,
    staff_category_id UUID REFERENCES staff_category(id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE bank_details (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    bio_row_id UUID REFERENCES bio_data(id) ON DELETE CASCADE ON UPDATE CASCADE,
    bank_name VARCHAR NOT NULL,
    bank_branch VARCHAR NOT NULL,
    account_number VARCHAR UNIQUE NOT NULL,
    account_type VARCHAR NOT NULL,
    account_status VARCHAR
);

CREATE TABLE academics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    bio_row_id UUID REFERENCES bio_data(id) ON DELETE CASCADE ON UPDATE CASCADE,
    institution VARCHAR NOT NULL,
    year DATE CHECK (year >=  '1974-01-01' AND year <=  '2024-12-31'),
    programme VARCHAR,
    qualification VARCHAR
);

CREATE TABLE professional (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    bio_row_id UUID REFERENCES bio_data(id) ON DELETE CASCADE ON UPDATE CASCADE,
    year DATE CHECK (year >= '1974-01-01' AND year <= '2024-12-31'),
    certification VARCHAR NOT NULL,
    institution VARCHAR NOT NULL,
    location VARCHAR
);

CREATE TABLE qualification (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    bio_row_id UUID REFERENCES bio_data(id) ON DELETE CASCADE ON UPDATE CASCADE,
    academic_qualification_id UUID REFERENCES academics(id) ON DELETE CASCADE ON UPDATE CASCADE,
    professional_qualification_id UUID REFERENCES professional(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE employment_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    bio_row_id UUID REFERENCES bio_data(id) ON DELETE CASCADE ON UPDATE CASCADE,
    date_employed DATE NOT NULL,
    institution VARCHAR NOT NULL,
    position VARCHAR NOT NULL,
    end_date DATE
);

CREATE TABLE family_info (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    bio_row_id UUID REFERENCES bio_data(id) ON DELETE CASCADE ON UPDATE CASCADE,
    name_of_spouse VARCHAR,
    occupation VARCHAR,
    phone_number VARCHAR,
    address VARCHAR,
    name_of_father_guardian VARCHAR,
    fathers_occupation VARCHAR,
    fathers_contact VARCHAR,
    fathers_address VARCHAR,
    name_of_mother_guardian VARCHAR,
    mothers_occupation VARCHAR,
    mothers_contact VARCHAR,
    mothers_address VARCHAR,
    children_name VARCHAR,
    children_dob VARCHAR
);

CREATE TABLE emergency_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    bio_row_id UUID REFERENCES bio_data(id) ON DELETE CASCADE ON UPDATE CASCADE,
    name VARCHAR,
    phone_number VARCHAR,
    address VARCHAR,
    email VARCHAR
);

CREATE TABLE next_of_kin (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    bio_row_id UUID REFERENCES bio_data(id) ON DELETE CASCADE ON UPDATE CASCADE,
    title VARCHAR DEFAULT 'Other' NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    other_name VARCHAR,
    surname VARCHAR(100) NOT NULL,
    gender VARCHAR DEFAULT 'Other' NOT NULL,
    relation VARCHAR NOT NULL,
    address VARCHAR,
    town VARCHAR NOT NULL,
    region VARCHAR NOT NULL,
    phone VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL
);

CREATE TABLE declaration (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    bio_row_id UUID REFERENCES bio_data(id) ON DELETE CASCADE ON UPDATE CASCADE,
    status BOOLEAN DEFAULT FALSE,
    reps_signature VARCHAR,
    employees_signature VARCHAR,
    declaration_date DATE DEFAULT NOW()
);

CREATE TABLE trademark (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    name VARCHAR UNIQUE NOT NULL,
    left_logo VARCHAR,
    right_logo VARCHAR
);
 
CREATE TABLE user_role(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    roles VARCHAR UNIQUE NOT NULL,
    dashboard VARCHAR
);



-- Insert seed data into user_role
INSERT INTO user_role (roles, dashboard) VALUES
('Admin', '/admin/home'),
('HR', '/hr/home'),
('I.T Staff', '/staff/home'),
('Customer-Care Staff', '/staff/home'),
('System-Admin', '/admin/home');


-- Insert seed data into centre
INSERT INTO centre (location, region) VALUES
('Accra', 'Greater Accra'),
('Kumasi', 'Ashanti Region'),
('Tamale', 'Northern Region'),
('Takoradi', 'Western Region'),
('Ho', 'Volta Region');

-- Insert seed data into directorate
INSERT INTO directorate (name, centre_id) VALUES
('HR', (SELECT id FROM centre WHERE location = 'Accra')),
('Finance', (SELECT id FROM centre WHERE location = 'Kumasi')),
('IT', (SELECT id FROM centre WHERE location = 'Tamale')),
('Operations', (SELECT id FROM centre WHERE location = 'Takoradi')),
('Marketing', (SELECT id FROM centre WHERE location = 'Ho'));

-- Insert seed data into grade
INSERT INTO grade (name, min_sal, max_sal) VALUES
('Grade 1', 1000.00, 2000.00),
('Grade 2', 2000.00, 3000.00),
('Grade 3', 3000.00, 4000.00),
('Grade 4', 4000.00, 5000.00),
('Grade 5', 5000.00, 6000.00);

-- Insert seed data into employment_type
INSERT INTO employment_type (name, description, grade_id) VALUES
('Full-Time', 'Full-time employment', (SELECT id FROM grade WHERE name = 'Grade 1')),
('Part-Time', 'Part-time employment', (SELECT id FROM grade WHERE name = 'Grade 2')),
('Contract', 'Contract employment', (SELECT id FROM grade WHERE name = 'Grade 3')),
('Internship', 'Internship employment', (SELECT id FROM grade WHERE name = 'Grade 4')),
('Consultant', 'Consultant employment', (SELECT id FROM grade WHERE name = 'Grade 5'));

-- Insert seed data into staff_category
INSERT INTO staff_category (category) VALUES
('Administrative'),
('Technical'),
('Support'),
('Management'),
('Executive');

-- Insert seed data into bio_data
INSERT INTO bio_data (title, first_name, other_names, surname, previous_name, gender, date_of_birth, nationality, hometown, religion, marital_status, residential_addr, active_phone_number, email, ssnit_number, ghana_card_number, is_physically_challenged, disability) VALUES
('Mr.', 'John', 'Kwame', 'Doe', NULL, 'Male', '1980-01-01', 'Ghanaian', 'Accra', 'Christianity', 'Single', '123 Accra Street', '0244123456', 'john.doe@example.com', 'SSN123456', 'GC123456', FALSE, NULL),
('Mrs.', 'Jane', 'Akosua', 'Smith', NULL, 'Female', '1985-02-02', 'Ghanaian', 'Kumasi', 'Islam', 'Married', '456 Kumasi Road', '0244987654', 'jane.smith@example.com', 'SSN654321', 'GC654321', FALSE, NULL),
('Dr.', 'Michael', 'Yaw', 'Brown', NULL, 'Male', '1975-03-03', 'Ghanaian', 'Tamale', 'Traditional', 'Widowed', '789 Tamale Avenue', '0244567890', 'michael.brown@example.com', 'SSN112233', 'GC112233', TRUE, 'Visual impairment'),
('Ms.', 'Angela', 'Adwoa', 'Taylor', NULL, 'Female', '1990-04-04', 'Ghanaian', 'Takoradi', 'Christianity', 'Divorced', '321 Takoradi Lane', '0244345678', 'angela.taylor@example.com', 'SSN445566', 'GC445566', FALSE, NULL),
('Prof.', 'Daniel', 'Kojo', 'Wilson', NULL, 'Male', '1965-05-05', 'Ghanaian', 'Ho', 'Christianity', 'Married', '654 Ho Street', '0244234567', 'daniel.wilson@example.com', 'SSN778899', 'GC778899', TRUE, 'Mobility impairment');

-- Insert seed data into users
--admin: password123
--users: password456
INSERT INTO users (bio_row_id, username, email, hashed_password, reset_pwd_token, is_active, role) VALUES
((SELECT id FROM bio_data WHERE first_name = 'John' AND surname = 'Doe'), 'johndoe', 'john.doe@example.com', '$2b$12$9SImAs0e9awgo6W3fI0qi.hUTgWetdaAWf.UM6wAfif2u1npzM8SW', NULL, TRUE, 'I.T Staff'),
((SELECT id FROM bio_data WHERE first_name = 'Jane' AND surname = 'Smith'), 'janesmith', 'jane.smith@example.com', '$2b$12$9SImAs0e9awgo6W3fI0qi.hUTgWetdaAWf.UM6wAfif2u1npzM8SW', NULL, TRUE, 'HR'),
((SELECT id FROM bio_data WHERE first_name = 'Michael' AND surname = 'Brown'), 'michaelbrown', 'michael.brown@example.com', '$2b$12$w7tjYNMXWMVGUnY14.pBTuqchkwILGQr5tivsUeuFltZT5YW35FqK', NULL, TRUE, 'Admin'),
((SELECT id FROM bio_data WHERE first_name = 'Angela' AND surname = 'Taylor'), 'angelataylor', 'angela.taylor@example.com', '$2b$12$9SImAs0e9awgo6W3fI0qi.hUTgWetdaAWf.UM6wAfif2u1npzM8SW', NULL, TRUE, 'Customer-Care Staff'),
((SELECT id FROM bio_data WHERE first_name = 'Daniel' AND surname = 'Wilson'), 'danielwilson', 'daniel.wilson@example.com', 'hashedpassword5', NULL, TRUE, 'System-Admin');





-- Insert seed data into employment_details
INSERT INTO employment_details (bio_row_id, date_of_first_appointment, grade_on_first_appointment, grade_on_current_appointment_id, directorate_id, employee_number, employment_type_id, staff_category_id) VALUES
((SELECT id FROM bio_data WHERE first_name = 'John' AND surname = 'Doe'), '2010-06-01', 'Grade 1', (SELECT id FROM grade WHERE name = 'Grade 1'), (SELECT id FROM directorate WHERE name = 'HR'), 'EMP001', (SELECT id FROM employment_type WHERE name = 'Full-Time'), (SELECT id FROM staff_category WHERE category = 'Administrative')),
((SELECT id FROM bio_data WHERE first_name = 'Jane' AND surname = 'Smith'), '2012-07-01', 'Grade 2', (SELECT id FROM grade WHERE name = 'Grade 2'), (SELECT id FROM directorate WHERE name = 'Finance'), 'EMP002', (SELECT id FROM employment_type WHERE name = 'Part-Time'), (SELECT id FROM staff_category WHERE category = 'Technical')),
((SELECT id FROM bio_data WHERE first_name = 'Michael' AND surname = 'Brown'), '2005-08-01', 'Grade 3', (SELECT id FROM grade WHERE name = 'Grade 3'), (SELECT id FROM directorate WHERE name = 'IT'), 'EMP003', (SELECT id FROM employment_type WHERE name = 'Contract'), (SELECT id FROM staff_category WHERE category = 'Support')),
((SELECT id FROM bio_data WHERE first_name = 'Angela' AND surname = 'Taylor'), '2018-09-01', 'Grade 4', (SELECT id FROM grade WHERE name = 'Grade 4'), (SELECT id FROM directorate WHERE name = 'Operations'), 'EMP004', (SELECT id FROM employment_type WHERE name = 'Internship'), (SELECT id FROM staff_category WHERE category = 'Management')),
((SELECT id FROM bio_data WHERE first_name = 'Daniel' AND surname = 'Wilson'), '2000-10-01', 'Grade 5', (SELECT id FROM grade WHERE name = 'Grade 5'), (SELECT id FROM directorate WHERE name = 'Marketing'), 'EMP005', (SELECT id FROM employment_type WHERE name = 'Consultant'), (SELECT id FROM staff_category WHERE category = 'Executive'));

-- Insert seed data into bank_details
INSERT INTO bank_details (bio_row_id, bank_name, bank_branch, account_number, account_type, account_status) VALUES
((SELECT id FROM bio_data WHERE first_name = 'John' AND surname = 'Doe'), 'Bank of Accra', 'Accra Main', '1234567890', 'Savings', 'Active'),
((SELECT id FROM bio_data WHERE first_name = 'Jane' AND surname = 'Smith'), 'Kumasi Bank', 'Kumasi Central', '2345678901', 'Current', 'Active'),
((SELECT id FROM bio_data WHERE first_name = 'Michael' AND surname = 'Brown'), 'Tamale Trust', 'Tamale North', '3456789012', 'Savings', 'Inactive'),
((SELECT id FROM bio_data WHERE first_name = 'Angela' AND surname = 'Taylor'), 'Takoradi Savings', 'Takoradi West', '4567890123', 'Current', 'Active'),
((SELECT id FROM bio_data WHERE first_name = 'Daniel' AND surname = 'Wilson'), 'Ho Credit', 'Ho South', '5678901234', 'Savings', 'Active');

-- Insert seed data into academics
INSERT INTO academics (bio_row_id, institution, year, programme, qualification) VALUES
((SELECT id FROM bio_data WHERE first_name = 'John' AND surname = 'Doe'), 'University of Ghana', '2000-06-01', 'Computer Science', 'BSc'),
((SELECT id FROM bio_data WHERE first_name = 'Jane' AND surname = 'Smith'), 'KNUST', '2005-07-01', 'Mechanical Engineering', 'BEng'),
((SELECT id FROM bio_data WHERE first_name = 'Michael' AND surname = 'Brown'), 'University for Development Studies', '1995-08-01', 'Agriculture', 'BSc'),
((SELECT id FROM bio_data WHERE first_name = 'Angela' AND surname = 'Taylor'), 'Takoradi Technical University', '2010-09-01', 'Marketing', 'HND'),
((SELECT id FROM bio_data WHERE first_name = 'Daniel' AND surname = 'Wilson'), 'University of Education, Winneba', '1985-10-01', 'Education', 'BA');

-- Insert seed data into professional
INSERT INTO professional (bio_row_id, year, certification, institution, location) VALUES
((SELECT id FROM bio_data WHERE first_name = 'John' AND surname = 'Doe'), '2015-06-01', 'PMP', 'PMI', 'USA'),
((SELECT id FROM bio_data WHERE first_name = 'Jane' AND surname = 'Smith'), '2018-07-01', 'Six Sigma', 'IASSC', 'UK'),
((SELECT id FROM bio_data WHERE first_name = 'Michael' AND surname = 'Brown'), '2012-08-01', 'CFA', 'CFA Institute', 'USA'),
((SELECT id FROM bio_data WHERE first_name = 'Angela' AND surname = 'Taylor'), '2020-09-01', 'CIM', 'Chartered Institute of Marketing', 'UK'),
((SELECT id FROM bio_data WHERE first_name = 'Daniel' AND surname = 'Wilson'), '2005-10-01', 'CA', 'ICAG', 'Ghana');

-- Insert seed data into qualification
INSERT INTO qualification (bio_row_id, academic_qualification_id, professional_qualification_id) VALUES
((SELECT id FROM bio_data WHERE first_name = 'John' AND surname = 'Doe'), (SELECT id FROM academics WHERE institution = 'University of Ghana' AND programme = 'Computer Science'), (SELECT id FROM professional WHERE certification = 'PMP')),
((SELECT id FROM bio_data WHERE first_name = 'Jane' AND surname = 'Smith'), (SELECT id FROM academics WHERE institution = 'KNUST' AND programme = 'Mechanical Engineering'), (SELECT id FROM professional WHERE certification = 'Six Sigma')),
((SELECT id FROM bio_data WHERE first_name = 'Michael' AND surname = 'Brown'), (SELECT id FROM academics WHERE institution = 'University for Development Studies' AND programme = 'Agriculture'), (SELECT id FROM professional WHERE certification = 'CFA')),
((SELECT id FROM bio_data WHERE first_name = 'Angela' AND surname = 'Taylor'), (SELECT id FROM academics WHERE institution = 'Takoradi Technical University' AND programme = 'Marketing'), (SELECT id FROM professional WHERE certification = 'CIM')),
((SELECT id FROM bio_data WHERE first_name = 'Daniel' AND surname = 'Wilson'), (SELECT id FROM academics WHERE institution = 'University of Education, Winneba' AND programme = 'Education'), (SELECT id FROM professional WHERE certification = 'CA'));

-- Insert seed data into employment_history
INSERT INTO employment_history (bio_row_id, date_employed, institution, position, end_date) VALUES
((SELECT id FROM bio_data WHERE first_name = 'John' AND surname = 'Doe'), '2005-01-01', 'Company A', 'Developer', '2010-01-01'),
((SELECT id FROM bio_data WHERE first_name = 'Jane' AND surname = 'Smith'), '2010-02-01', 'Company B', 'Engineer', '2015-02-01'),
((SELECT id FROM bio_data WHERE first_name = 'Michael' AND surname = 'Brown'), '2000-03-01', 'Company C', 'Manager', '2005-03-01'),
((SELECT id FROM bio_data WHERE first_name = 'Angela' AND surname = 'Taylor'), '2015-04-01', 'Company D', 'Marketer', '2020-04-01'),
((SELECT id FROM bio_data WHERE first_name = 'Daniel' AND surname = 'Wilson'), '1990-05-01', 'Company E', 'Teacher', '2000-05-01');

-- Insert seed data into family_info
INSERT INTO family_info (bio_row_id, name_of_spouse, occupation, phone_number, address, name_of_father_guardian, fathers_occupation, fathers_contact, fathers_address, name_of_mother_guardian, mothers_occupation, mothers_contact, mothers_address, children_name, children_dob) VALUES
((SELECT id FROM bio_data WHERE first_name = 'John' AND surname = 'Doe'), 'Jane Doe', 'Teacher', '0244789654', '123 Accra Street', 'James Doe', 'Farmer', '0244876543', 'Village Road', 'Mary Doe', 'Trader', '0244987654', 'Village Lane', 'John Jr.', '2010-01-01'),
((SELECT id FROM bio_data WHERE first_name = 'Jane' AND surname = 'Smith'), 'John Smith', 'Engineer', '0244987654', '456 Kumasi Road', 'Michael Smith', 'Doctor', '0244567890', 'City Avenue', 'Angela Smith', 'Nurse', '0244345678', 'City Lane', 'Janie', '2015-02-02'),
((SELECT id FROM bio_data WHERE first_name = 'Michael' AND surname = 'Brown'), 'Angela Brown', 'Nurse', '0244567890', '789 Tamale Avenue', 'Daniel Brown', 'Engineer', '0244123456', 'Urban Street', 'Lucy Brown', 'Teacher', '0244789654', 'Urban Lane', 'Mike Jr.', '2005-03-03'),
((SELECT id FROM bio_data WHERE first_name = 'Angela' AND surname = 'Taylor'), 'Michael Taylor', 'Businessman', '0244345678', '321 Takoradi Lane', 'James Taylor', 'Retired', '0244876543', 'Old Street', 'Janet Taylor', 'Homemaker', '0244987654', 'Old Lane', 'Angie', '2010-04-04'),
((SELECT id FROM bio_data WHERE first_name = 'Daniel' AND surname = 'Wilson'), 'Emily Wilson', 'Doctor', '0244234567', '654 Ho Street', 'David Wilson', 'Engineer', '0244567890', 'City Road', 'Sarah Wilson', 'Teacher', '0244345678', 'City Avenue', 'Danny', '1995-05-05');

-- Insert seed data into emergency_contacts
INSERT INTO emergency_contacts (bio_row_id, name, phone_number, address, email) VALUES
((SELECT id FROM bio_data WHERE first_name = 'John' AND surname = 'Doe'), 'Jane Doe', '0244789654', '123 Accra Street', 'jane.doe@example.com'),
((SELECT id FROM bio_data WHERE first_name = 'Jane' AND surname = 'Smith'), 'John Smith', '0244987654', '456 Kumasi Road', 'john.smith@example.com'),
((SELECT id FROM bio_data WHERE first_name = 'Michael' AND surname = 'Brown'), 'Angela Brown', '0244567890', '789 Tamale Avenue', 'angela.brown@example.com'),
((SELECT id FROM bio_data WHERE first_name = 'Angela' AND surname = 'Taylor'), 'Michael Taylor', '0244345678', '321 Takoradi Lane', 'michael.taylor@example.com'),
((SELECT id FROM bio_data WHERE first_name = 'Daniel' AND surname = 'Wilson'), 'Emily Wilson', '0244234567', '654 Ho Street', 'emily.wilson@example.com');

-- Insert seed data into next_of_kin
INSERT INTO next_of_kin (bio_row_id, title, first_name, other_name, surname, gender, relation, address, town, region, phone, email) VALUES
((SELECT id FROM bio_data WHERE first_name = 'John' AND surname = 'Doe'), 'Mrs.', 'Jane', 'Akosua', 'Doe', 'Female', 'Wife', '123 Accra Street', 'Accra', 'Greater Accra', '0244789654', 'jane.doe@example.com'),
((SELECT id FROM bio_data WHERE first_name = 'Jane' AND surname = 'Smith'), 'Mr.', 'John', 'Kofi', 'Smith', 'Male', 'Husband', '456 Kumasi Road', 'Kumasi', 'Ashanti Region', '0244987654', 'john.smith@example.com'),
((SELECT id FROM bio_data WHERE first_name = 'Michael' AND surname = 'Brown'), 'Mrs.', 'Angela', 'Yaw', 'Brown', 'Female', 'Wife', '789 Tamale Avenue', 'Tamale', 'Northern Region', '0244567890', 'angela.brown@example.com'),
((SELECT id FROM bio_data WHERE first_name = 'Angela' AND surname = 'Taylor'), 'Mr.', 'Michael', 'Yaw', 'Taylor', 'Male', 'Husband', '321 Takoradi Lane', 'Takoradi', 'Western Region', '0244345678', 'michael.taylor@example.com'),
((SELECT id FROM bio_data WHERE first_name = 'Daniel' AND surname = 'Wilson'), 'Mrs.', 'Emily', 'Adwoa', 'Wilson', 'Female', 'Wife', '654 Ho Street', 'Ho', 'Volta Region', '0244234567', 'emily.wilson@example.com');

-- Insert seed data into declaration
INSERT INTO declaration (bio_row_id, status, reps_signature, employees_signature, declaration_date) VALUES
((SELECT id FROM bio_data WHERE first_name = 'John' AND surname = 'Doe'), TRUE, '', '', '2024-01-01'),
((SELECT id FROM bio_data WHERE first_name = 'Jane' AND surname = 'Smith'), TRUE, 'base64_representation_of_reps_signature_image', 'base64_representation_of_employees_signature_image', '2024-02-01'),
((SELECT id FROM bio_data WHERE first_name = 'Michael' AND surname = 'Brown'), TRUE, 'base64_representation_of_reps_signature_image', 'base64_representation_of_employees_signature_image', '2024-03-01'),
((SELECT id FROM bio_data WHERE first_name = 'Angela' AND surname = 'Taylor'), TRUE, 'base64_representation_of_reps_signature_image', 'base64_representation_of_employees_signature_image', '2024-04-01'),
((SELECT id FROM bio_data WHERE first_name = 'Daniel' AND surname = 'Wilson'), TRUE, 'base64_representation_of_reps_signature_image', 'base64_representation_of_employees_signature_image', '2024-05-01');
