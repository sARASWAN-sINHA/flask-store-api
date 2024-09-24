from db import db

class Tags(db.Model):
    __tablename__ = "Tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    store_id = db.Column(db.Integer, db.ForeignKey("Store.id"), unique=False, nullable=False)
    store = db.relationship("Store", back_populates="tags")
    items = db.relationship("Items", back_populates="tags", secondary="items_tags")

