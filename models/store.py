from db import db

class Store(db.Model):
    __tablename__ = "Store"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    items = db.relationship("Items", back_populates="store", lazy="dynamic", cascade="all, delete")
    tags = db.relationship("Tags", back_populates="store", lazy="dynamic")
