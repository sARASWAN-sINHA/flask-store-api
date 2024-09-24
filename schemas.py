from marshmallow import Schema, fields


class PlainStoreSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)


class PlainItemSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)


class PlainTagSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)


class ItemSchema(PlainItemSchema):
    store_id = fields.Integer(load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)


class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)


class TagSchema(PlainTagSchema):
    store_id = fields.Integer(load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    item = fields.Nested(PlainItemSchema(), dump_only=True)


class ItemTagsScehma(Schema):
    message = fields.Str(dump_only=True)
    item = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    tags = fields.Nested(PlainTagSchema(), dump_only=True)


class ItemUpdateSchema(Schema):
    name = fields.Str()
    price = fields.Float()


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.Str()
    password = fields.Str(load_only=True)

