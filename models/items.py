from db import db

class Items(db.Model):
    __tablename__ = "Items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.String)
    price = db.Column(db.Float(precision=2), nullable=False, unique=False)
    store_id = db.Column(db.Integer, db.ForeignKey("Store.id"), unique=False, nullable=False)
    store = db.relationship("Store", back_populates="items")
    tags = db.relationship("Tags", back_populates="items", secondary="items_tags")
