from db import db


class ItemTags(db.Model):
    __tablename__ = "items_tags"

    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey("Tags.id"))
    item_id = db.Column(db.Integer, db.ForeignKey("Items.id"))
