# CourseListManagementApp 

A comprehensive web application for managing computer science program courses, competencies, and their relationships. Built with Flask for the Web Applications III course (420-420-DW) offered in Dawson College.

## Repository Information

- **Current Repository**: https://github.com/melissa0987/CompetencyManagerApp.git
- **Original GitLab Repository**: https://gitlab.com/python_winter2023/Final_Project *(private)* 

> **Note**: This project was originally developed in a private GitLab repository as part of a team coursework assignment. It has been migrated to GitHub for portfolio purposes while maintaining all original commit history and team contributions.

## Team Members

| Name 				    | Student ID | GitLab Username 		|
|-----------------------|------------|----------------------|
| Monica Dimitrova 		| 2135425 	 | monica_dimitrova 	|
| Christina Chiappini 	| 2042557 	 | christina_chiappini 	|
| Melissa Bangloy 		| 1438659 	 | melissa_louise 		|
| Farhan Khandaker 		| 2135266 	 | farhan_khandaker 	|

## 📋 Project Overview

This Flask-based web application serves as a comprehensive system for managing computer science program data, including:

- **Course Management**: Create, view, edit, and delete courses
- **Competency Management**: Manage program competencies and their relationships
- **User Authentication**: Multi-level user access control system
- **Administrative Dashboard**: User and group management functionality
- **REST API**: Programmatic access to course and competency data

## Features

### User Management
- **Visitors**: Browse public content, register for accounts
- **Members**: Full access to course/competency management
- **Admin Users**: User management capabilities
- **Super Admins**: Complete system administration

### Core Functionality
- Course and competency CRUD operations
- Advanced search and filtering
- User profile management with avatars
- Password reset functionality
- Responsive web design

### API Endpoints
- RESTful API for courses, competencies, and relationships
- JSON responses for external tool integration
- Curl-compatible endpoints for automation

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: Oracle SQL
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: Flask-Login
- **Deployment**: Gunicorn WSGI server
- **Version Control**: Git/GitLab

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- Access to Oracle PDBORA19C database
- Git

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/melissa0987/CompetencyManagerApp.git
   cd CourseListManagementApp
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database connection**
   ```bash
   export DBUSER=your_db_username
   export DBPWD=your_db_password
   ```

5. **Initialize database**
   ```bash
   # Run the schema.sql file against your Oracle database
   sqlplus $DBUSER/$DBPWD@PDBORA19C @schema.sql
   ```

6. **Run the application**
   ```bash
   flask --app CompetencyManager --debug run
   ```

The application will be available at `http://localhost:5000`

### Production Deployment

1. **Follow steps 1-5 from Development Setup**

2. **Configure firewall**
   ```bash
   sudo ufw allow 8000
   ```

3. **Create production configuration**
   ```python
   # config.py
   SECRET_KEY = 'your-secret-key-here'
   ```

4. **Deploy with Gunicorn**
   ```bash
   gunicorn -w 2 -b 0.0.0.0:8000 'CompetencyManager:create_app()'
   ```

## Default Credentials

For testing and demonstration purposes:

- **Email**: instructor@gmail.com
- **Password**: Python420
- **Role**: Super Admin

## Database Schema

The application uses the following main entities:
- **Users**: Member authentication and profiles
- **Courses**: Academic course information
- **Competencies**: Program learning outcomes
- **Elements**: Granular competency components
- **Relationships**: Mappings between courses and competencies

## Testing

The project includes comprehensive unit tests for:
- User authentication flows
- CRUD operations
- API endpoints
- Data validation

Run tests with:
```bash
python -m unittest discover tests/
```

## API Documentation

### Courses API
- `GET /api/v1/courses` - List all courses
- `POST /api/v1/courses` - Create new course
- `GET /api/v1/courses/<id>` - Get specific course
- `PUT /api/v1/courses/<id>` - Update course
- `DELETE /api/v1/courses/<id>` - Delete course

### Competencies API
- `GET /api/v1/competencies` - List all competencies
- `POST /api/v1/competencies` - Create new competency
- `GET /api/v1/competencies/<id>` - Get specific competency
- `PUT /api/v1/competencies/<id>` - Update competency
- `DELETE /api/v1/competencies/<id>` - Delete competency

### Example Usage
**Note:** These examples require college network access. External users will receive "This site can't be reached" errors.

```bash
# Get all courses
curl http://10.172.23.16:8000/api/v1/courses

# Get specific course
curl http://10.172.23.16:8000/api/v1/courses/COURSE_ID
```

## Development Practices

This project follows:
- **PEP 8**: Python style guidelines (with noted exceptions)
- **MVC Architecture**: Clear separation of concerns
- **Feature Branch Workflow**: Protected main branch with merge requests
- **Code Reviews**: All changes reviewed before merging
- **Meaningful Commits**: Descriptive commit messages

## Known Issues & Development Notes

### Naming Convention Disclaimer

**Please excuse the partial non-conforming to PEP8 standards in naming conventions.** Our team is aware that camelCase is not the standard acceptable naming convention for variables in Python. We made a mistake implementing it in the beginning of development and didn't want to risk breaking functionalities. We should have used snake_case.

This naming inconsistency remains in the codebase as a learning example and to maintain system stability.


## License

This project is developed for educational purposes as part of the Web Applications III course at Dawson College.
 
