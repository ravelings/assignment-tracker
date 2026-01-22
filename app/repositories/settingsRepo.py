from extensions.extensions import db
from models.settings import Settings

class SettingsRepo():
    def __init__(self):
        pass
    
    def commit(self):
        db.session.commit()
    
    def initSettings(self, user_id):
        user_settings = Settings(user_id=user_id, function=1)
        db.session.add(user_settings)
        self.commit()
        return self

    def getUserSettings(self, user_id):
        return (Settings.query.filter_by(user_id=user_id).first())
    
    def setFunction(self, user_id, function):
        print(f"Function type: {type(function)}")
        settings = self.getUserSettings(user_id)
        if settings is None or not isinstance(function, int):
            return False 
        
        settings.scoring_strategy = function 
        
        self.commit()
        
        return True
