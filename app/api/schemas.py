from marshmallow import Schema, fields


class ClassSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    day = fields.Str()
    start_time = fields.Time(format="%I:%M %p")
    end_time = fields.Time(format="%I:%M %p")
    capacity = fields.Int()
    spots_remaining = fields.Int(dump_only=True)
    is_full = fields.Bool(dump_only=True)


class ReservationCreateSchema(Schema):
    class_id = fields.Int(required=True)


class ReservationSchema(Schema):
    id = fields.Int(dump_only=True)
    class_id = fields.Int()
    user_id = fields.Int()
    status = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    cancelled_at = fields.DateTime(dump_only=True)
    studio_class = fields.Nested(ClassSchema, dump_only=True)


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str()
    email = fields.Email()
    first_name = fields.Str()
    last_name = fields.Str()
    created_at = fields.DateTime(dump_only=True)
