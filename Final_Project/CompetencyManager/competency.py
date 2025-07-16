class Competency:
    
    def __init__(self, competencyID, competencyName, competencyAchievement, competencyType):

        if isinstance(competencyID, str):
            self.competencyID = competencyID
        else:
            raise Exception("Competency id must be a string.")
        
        if isinstance(competencyName, str):
            self.competencyName = competencyName
        else:
            raise Exception("Competency name must be a string.")
        
        if isinstance(competencyAchievement, str):
            self.competencyAchievement = competencyAchievement
        else:
            raise Exception("Competency achievement must be a string.")
        
        if isinstance(competencyType, str):
            self.competencyType = competencyType
        else:
            raise Exception("Competency type must be a string.")
        
        self.elements = []
        
    def __repr__(self):
        return f"Competency({self.competencyID} {self.competencyName} {self.competencyAchievement} {self.competencyType})"
    
    def __str__(self):
        return f"{self.competencyID} {self.competencyName}"
    

    def to_dict(self):
        return {"competencyID" : self.competencyID,
                "competencyName" : self.competencyName,
                "competencyAchievement" : self.competencyAchievement,
                "competencyType" : self.competencyType,
                "elements" : self.elements}
    
    def from_json(competency_json):
        if not isinstance(competency_json, dict):
            raise TypeError("Invalid Type; expected dict")
        return Competency(competency_json['competencyID'], competency_json['competencyName'], competency_json['competencyAchievement'], competency_json['competencyType'])
