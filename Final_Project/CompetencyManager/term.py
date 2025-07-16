class Term:
    
    def __init__(self, termID, termName):
        
        if isinstance(termID, int):
            if termID > 0:
                self.termID = termID
            else:
                raise Exception("Term id must be greater than 0.")
        else:
            raise Exception("Term id must be a number.")
        
        if isinstance(termName, str):
            self.termName = termName
        else:
            raise Exception("Term name must be a string.")
        
    def __repr__(self):
        return f"Term({self.termID} {self.termName})"
    
    def __str__(self):
        return f"Term {self.termID}: {self.termName}"
    
    
    def to_dict(self):
        return {"termID": self.termID,
                "termName": self.termName}
    
    def from_json(term_json):
        if not isinstance(term_json, dict):
            raise TypeError("Invalid Type; expected dict")
        return Term(term_json['termID'], term_json['termName'])
    
    