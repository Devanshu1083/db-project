create database rms;
use rms;

create table user (
	user_id int NOT NULL UNIQUE,
    email varchar(20) NOT NULL UNIQUE,
    user_pass varchar(20),
	usertype varchar(20) NOT NULL,
    PRIMARY KEY(user_id)
);

drop table user;

insert into user
values ( 1024,"mudgal@iitrpr.com", "muddu@ada","Applicant"),
		( 1026, "jagp@iitrpr.com", "jaggu@os","Recruiter");
        
-- create table recruiter (
-- 	recruiter_id int NOT NULL UNIQUE,
-- 	recruiter_name varchar(20) NOT NULL,
--     email varchar(20) NOT NULL UNIQUE,
--     recruiter_pass varchar(20)
-- );

-- drop table recruiter;

create table jobs (
	job_id int NOT NULL UNIQUE,
	job_name varchar(20) NOT NULL,
    user_id int NOT NULL,
    foreign key (user_id) references user(user_id),
    PRIMARY KEY(job_id)
);

create table applications (
    application_id int NOT NULL,
	job_id int NOT NULL,
	user_id int NOT NULL,
    foreign key (job_id) references jobs(job_id),
    foreign key (user_id) references user(user_id),
    PRIMARY KEY(application_id)
);

create table test_questions (
	job_id int NOT NULL UNIQUE,
    q1 varchar(50),
    q2 varchar(50),
    q3 varchar(50),
    ans1 int,
    ans2 int,
    ans3 int,
    foreign key (job_id) references jobs(job_id),
    PRIMARY KEY(job_id)
);

create table results (
	user_id int NOT NULL,
    job_id int NOT NULL,
    
    response1 int,
    response2 int,
    response3 int,
    total_score int,
    
    foreign key (job_id) references jobs(job_id),
    foreign key (user_id) references user(user_id),
    PRIMARY KEY(user_id,job_id)
);
