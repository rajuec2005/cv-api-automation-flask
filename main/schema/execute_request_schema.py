from marshmallow import Schema, fields, post_load


class RequestSchema():
    def __init__(self, serviceName, testEnv, testerEmailId, groups=None, testscenario_name=None):
        self.serviceName = serviceName
        self.groups = groups
        self.testscenario_name = testscenario_name
        self.testEnv = testEnv
        self.testerEmailId = testerEmailId

    def __repr__(self):
        return '<RequestSchema {}/{}>'.format(self.serviceName, self.groups)


class ExecuteRequestSchema(Schema):
    # The variable names should match the payload fields
    serviceName = fields.List(fields.Str, required=True)
    groups = fields.List(fields.Str, required=False)
    testscenario_name = fields.List(fields.Str, required=False)
    testEnv = fields.Str(required=True)
    testerEmailId = fields.Email(required=True)


    @post_load
    def make_user(self, data, **kwargs):
        return RequestSchema(**data)