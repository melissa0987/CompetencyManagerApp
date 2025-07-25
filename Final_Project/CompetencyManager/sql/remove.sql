--drop tables

drop table courses_elements CASCADE CONSTRAINTS;
drop table competencies CASCADE CONSTRAINTS;
drop table courses CASCADE CONSTRAINTS;
drop table terms CASCADE CONSTRAINTS;
drop table elements CASCADE CONSTRAINTS;
drop table domains CASCADE CONSTRAINTS;
--Logging
drop table audit_logs;

--Users
drop table app_users;

--Drop Triggers
--courses
-- drop trigger after_courses_updated;
-- drop trigger after_courses_inserted;
-- drop trigger after_courses_deleted;
-- --competencies
-- drop trigger after_competencies_updated;
-- drop trigger after_competencies_inserted;
-- drop trigger after_competencies_deleted;

--Drop Views
drop view view_courses;
drop view view_courses_elements;
drop view view_courses_terms;
drop view view_courses_domains;
drop view view_competencies;
drop view view_competencies_elements;
drop view view_courses_elements_competencies;

--Drop Package
drop package courses_package;

--Drop Object
drop type course_typ;
drop type term_typ;
drop type domain_typ;
drop type element_array;
drop type element_typ;
drop type competency_typ;