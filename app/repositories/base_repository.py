# repositories/base_repository.py
from app import db

class BaseRepository:
    def __init__(self, model, session=None):
        self.model = model
        self.session = session or db.session

    def get_all(self):
        return self.session.query(self.model).all()

    def get_by_id(self, id):
        return self.session.query(self.model).filter_by(id=id).first()

    def create(self, **kwargs):
        instance = self.model(**kwargs)
        self.session.add(instance)
        self.session.commit()
        return instance

    def update(self, id, **kwargs):
        instance = self.get_by_id(id)
        if not instance:
            return None
        for key, value in kwargs.items():
            setattr(instance, key, value)
        self.session.commit()
        return instance

    def delete(self, id):
        instance = self.get_by_id(id)
        if not instance:
            return False
        self.session.delete(instance)
        self.session.commit()
        return True
