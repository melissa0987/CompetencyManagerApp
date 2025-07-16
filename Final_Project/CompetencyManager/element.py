class Element:
    
    def __init__(self, elementOrder, elementName, elementCriteria, elementID=None, competencyID=None):

        if elementID != None:
            if isinstance(elementID, int):
                if elementID > 0:
                    self.elementID = elementID
                else:
                    raise Exception("Element ID must be greater than 0")
            else:
                raise Exception("Element ID must be a number.")
        
        if isinstance(elementOrder, int):
            self.elementOrder = elementOrder
        else:
            raise Exception("Element order must be a number.")
        
        if isinstance(elementName, str):
            self.elementName = elementName
        else:
            raise Exception("Element name must be a string.")
        
        if isinstance(elementCriteria, str):
            self.elementCriteria = elementCriteria
        else:
            raise Exception("Element criteria must be a string.")
        
        if competencyID != None:
            if isinstance(competencyID, str):
                self.competencyID = competencyID
            else:
                raise Exception("Element criteria must be a string.")
            
        self.elementHours = None
        
        
    def __repr__(self):
        return f"Element({self.elementID} {self.elementOrder} {self.elementName} {self.elementCriteria} {self.competencyID})"
    
    def __repr__(self):
        return f"{self.elementName}"
    
    def from_json(element_json):
        if not isinstance(element_json, dict):
            raise TypeError("Invalid Type; expected dict")
        return Element(element_json['elementOrder'], element_json['elementName'], element_json['elementCriteria'], int(element_json['elementID']), element_json['competencyID'])
    
    def to_dict(self):
        return {"elementOrder" : self.elementOrder,
         "elementName" : self.elementName,
         "elementCriteria" : self.elementCriteria,
         "elementID" : self.elementID,
         "competencyID" : self.competencyID}