import graphene
from graphene_django.types import DjangoObjectType # type: ignore

from .models import *
from datetime import date
from django.contrib.auth.models import User
from project_dto.project import *
from projectBuilders.projectBuilders import *
from .views import *
import graphql_jwt # type: ignore

        
        
class Mutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
    register_event = RegisterEvent.Field()
    login_user = LoginUser.Field()
    update_event = UpdateEvent.Field()
    delete_event = DeleteEvent.Field()
    delete_application = DeleteApplication.Field()
    conference_room_booking = ConferenceRoomBooking.Field()
    register_room = RegisterRoom.Field()
    request_room = RequestRoom.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    create_event_application = ApplicationEvent.Field()
    reset_password = ResetPassword.Field()
    github_oauth  = GitHubOAuthMutation.Field()


class Query(CategoryQuery, EventQuery, UserProfileQuery, EventCountQuery, EventApplicationQuery, EventUserQuery, RoomQuery, UserQuery, graphene.ObjectType):
    pass

    
schema =graphene.Schema(query=Query, mutation=Mutation)
        
    