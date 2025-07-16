class Course:
    
    def __init__(self, courseID, courseTitle, theoryHours, labHours, workHours, description, domainID=None, termID=None):
        
        if isinstance(courseID, str):
            self.courseID = courseID
        else:
            raise Exception("Course title must be a string.")
        
        if isinstance(courseTitle, str):
            self.courseTitle = courseTitle
        else:
            raise Exception("Course title must be a string.")
        
        if not theoryHours < 0:
            self.theoryHours = theoryHours
        else:
            raise Exception("Theory hours must be positive.")
        
        if not labHours < 0:
            self.labHours = labHours
        else:
            raise Exception("Lab hours must be positive.")
        
        if not workHours < 0:
            self.workHours = workHours
        else:
            raise Exception("Work hours must be positive.")
        
        if isinstance(description, str):
            self.description = description
        else:
            raise Exception("Course description must be a string.")
        
        self.courseID = courseID
        self.domainID = domainID
        self.termID = termID
        
    def __repr__(self):
        return f"Course({self.courseID} {self.courseTitle} {self.theoryHours} {self.labHours} {self.workHours} {self.description} {self.domainID} {self.termID})"
    
    def __str__(self):
        return f"{self.courseID} {self.courseTitle}"
    
    def from_json(course_json):
        if not isinstance(course_json, dict):
            raise TypeError("Invalid Type; expected dict")
        return Course(course_json['courseID'], course_json['courseTitle'], int(course_json['theoryHours']), int(course_json['labHours']), int(course_json['workHours']), course_json['description'], int(course_json['domainID']), int(course_json['termID']))

    def to_dict(self):
        return {"courseID" : self.courseID,
                "courseTitle" : self.courseTitle,
                "theoryHours" : self.theoryHours,
                "labHours" : self.labHours,
                "workHours" : self.workHours,
                "description" : self.description,
                "domainID" : self.domainID, 
                "termID" : self.termID}
