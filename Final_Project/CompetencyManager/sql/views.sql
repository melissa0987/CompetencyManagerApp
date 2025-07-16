--creating all views
create or replace view view_courses as
    (select * from courses);
    /
create or replace view view_courses_elements as
    (select * from courses 
     join courses_elements using(course_id)
     join elements using(element_id));
     /
create or replace view view_courses_terms as
    (select * from courses
     join terms using(term_id));
     /
create or replace view view_courses_domains as
    (select * from courses
     join domains using(domain_id));
     /
create or replace view view_competencies as
    (select * from competencies);
/
create or replace view view_competencies_elements as
    (select * from competencies
     join elements using(competency_id));
     /
create or replace view view_courses_elements_competencies as
    (select * from courses
     join courses_elements using(course_id)
     join elements using(element_id)
     join competencies using(competency_id));
     /
CREATE OR REPLACE VIEW view_audit_logs
AS
    (SELECT * FROM audit_logs);
 /
CREATE OR REPLACE VIEW view_members AS(
    SELECT id, email, password, name, avatar_path, account_type, is_locked 
    FROM app_users 
    WHERE account_type = 'MEMBER' ) ORDER BY id ;

/
CREATE OR REPLACE VIEW view_admin_user_gp AS(
    SELECT id, email, password, name, avatar_path, account_type, is_locked 
    FROM app_users 
    WHERE account_type = 'ADMIN_USER_GP' )ORDER BY id ;

/
CREATE OR REPLACE VIEW view_admin_gp AS(
    SELECT id, email, password, name, avatar_path, account_type, is_locked 
    FROM app_users 
    WHERE account_type = 'ADMINISTRATOR_GP' ) ORDER BY id ;

/
CREATE OR REPLACE VIEW view_all_users AS(
    SELECT id, email, password, name, avatar_path, account_type, is_locked 
    FROM app_users ) ORDER BY id;
    
/
CREATE OR REPLACE VIEW view_blocked_users AS(
    SELECT id, email, password, name, avatar_path, account_type, is_locked 
    FROM app_users
    WHERE is_locked = 1) ORDER BY id;
    
/

CREATE INDEX course_id_search ON courses(course_id) INDEXTYPE IS CTXSYS.CONTEXT PARAMETERS ('FILTER CTXSYS.NULL_FILTER SECTION GROUP CTXSYS.HTML_SECTION_GROUP');
CREATE INDEX course_name_search ON courses(course_title) INDEXTYPE IS CTXSYS.CONTEXT PARAMETERS ('FILTER CTXSYS.NULL_FILTER SECTION GROUP CTXSYS.HTML_SECTION_GROUP');
CREATE INDEX course_description_search ON courses(description) INDEXTYPE IS CTXSYS.CONTEXT PARAMETERS ('FILTER CTXSYS.NULL_FILTER SECTION GROUP CTXSYS.HTML_SECTION_GROUP');

CREATE INDEX competency_id_search ON competencies(competency_id) INDEXTYPE IS CTXSYS.CONTEXT PARAMETERS ('FILTER CTXSYS.NULL_FILTER SECTION GROUP CTXSYS.HTML_SECTION_GROUP');
CREATE INDEX competency_name_search ON competencies(competency) INDEXTYPE IS CTXSYS.CONTEXT PARAMETERS ('FILTER CTXSYS.NULL_FILTER SECTION GROUP CTXSYS.HTML_SECTION_GROUP');
CREATE INDEX competency_achievement_search ON competencies(competency_achievement) INDEXTYPE IS CTXSYS.CONTEXT PARAMETERS ('FILTER CTXSYS.NULL_FILTER SECTION GROUP CTXSYS.HTML_SECTION_GROUP');

CREATE INDEX element_competency_id_search ON elements(competency_id) INDEXTYPE IS CTXSYS.CONTEXT PARAMETERS ('FILTER CTXSYS.NULL_FILTER SECTION GROUP CTXSYS.HTML_SECTION_GROUP');
CREATE INDEX element_criteria_search ON elements(element_criteria) INDEXTYPE IS CTXSYS.CONTEXT PARAMETERS ('FILTER CTXSYS.NULL_FILTER SECTION GROUP CTXSYS.HTML_SECTION_GROUP');
CREATE INDEX element_search ON elements(element) INDEXTYPE IS CTXSYS.CONTEXT PARAMETERS ('FILTER CTXSYS.NULL_FILTER SECTION GROUP CTXSYS.HTML_SECTION_GROUP');

CREATE INDEX domain_search ON domains(domain) INDEXTYPE IS CTXSYS.CONTEXT PARAMETERS ('FILTER CTXSYS.NULL_FILTER SECTION GROUP CTXSYS.HTML_SECTION_GROUP');
CREATE INDEX domain_description_search ON domains(domain_description) INDEXTYPE IS CTXSYS.CONTEXT PARAMETERS ('FILTER CTXSYS.NULL_FILTER SECTION GROUP CTXSYS.HTML_SECTION_GROUP');


