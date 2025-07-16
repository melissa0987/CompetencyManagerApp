class Domain:
    
    def __init__(self, domainName, description, domainID=None):
        
        
        if isinstance(domainName, str):
            self.domainName = domainName
        else:
            raise Exception("Domain name must be a string.")
        
        if isinstance(description, str):
            self.description = description
        else:
            raise Exception("Domain description must be a string.")
        
        self.domainID = domainID
        
    def __repr__(self):
        return f"Domain({self.domainID} {self.domainName} {self.description})"
    
    def __str__(self):
        return f"{self.domainName}"
    

    def to_dict(self):
        return {"description": self.description,
                "domainName": self.domainName,
                "domainID": self.domainID}
    
    def from_json(domain_json):
        if not isinstance(domain_json, dict):
            raise TypeError("Invalid Type; expected dict")
        return Domain(domain_json['domainName'], domain_json['description'], domain_json['domainID'])


    
    