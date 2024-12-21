import graphene


class PasswordResetResponse(graphene.ObjectType):
    success = graphene.Boolean()
    message = graphene.String()