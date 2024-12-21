from django.conf import settings
import graphene
from django.contrib.auth.models import User
from myapp.models import *



class UserRegistrationInputObject(graphene.InputObjectType):
    username = graphene.String()
    email = graphene.String()
    password = graphene.String()
    password_confirm = graphene.String()
    
class UserRegistrationObject(graphene.ObjectType):
    id = graphene.ID()
    username = graphene.String()
    email = graphene.String()
    
class UserLoginInputObject(graphene.InputObjectType):
    username = graphene.String()
    password = graphene.String()
    
class UserLoginObject(graphene.ObjectType):
    id = graphene.ID()
    username = graphene.String()
    email = graphene.String()
    refresh_token = graphene.String()
    access_token = graphene.String()
    isSuperuser = graphene.Boolean()
    
class UserProfileObject(graphene.ObjectType):
    id = graphene.ID()
    username = graphene.String()
    email = graphene.String()
    
    
class ResetPasswordInputObject(graphene.InputObjectType):
    old_password = graphene.String()
    new_password = graphene.String()
    new_password_confirm = graphene.String()


class ResetPasswordObject(graphene.ObjectType):
    old_password = graphene.String()
    new_password = graphene.String()
    new_password_confirm = graphene.String()
    

class CategoryObject(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    
class EventObject(graphene.ObjectType):
    id  = graphene.ID()
    event_username = graphene.String()
    event_name = graphene.String()
    event_date = graphene.String()
    event_location = graphene.String()
    event_category = graphene.String()
    application_count = graphene.Int()
    
    def resolve_application_count(self, info):
        return EventApplication.objects.filter(event_id=self.id).count()
    
from graphene_file_upload.scalars import Upload 
 

class EventRegistrationInputObject(graphene.InputObjectType):
    event_username = graphene.String()
    event_name = graphene.String()
    event_date = graphene.String()
    event_location = graphene.String()
    event_category = graphene.String()
    # image = graphene.upload(required=False)
    
class EventUpdateInputObject(graphene.InputObjectType):
    id = graphene.ID()
    event_username = graphene.String()
    event_name = graphene.String()
    event_date = graphene.String()
    event_location = graphene.String()
    event_category = graphene.String()

    
class EventRegistrationObject(graphene.ObjectType):
    id = graphene.ID()
    event_username = graphene.String()
    event_name = graphene.String()
    event_date = graphene.String()
    event_location = graphene.String()
    event_category = graphene.String()
    # image = graphene.String()

class EventApplicationInputObject(graphene.InputObjectType):
    name = graphene.String()
    email = graphene.String()
    status = graphene.String()
    event_id = graphene.String()
    
class EventApplicationObject(graphene.ObjectType):
    name = graphene.String()
    email = graphene.String()
    status = graphene.String()
    event_id = graphene.String()
    
    

class BookingRoomInputObject(graphene.InputObjectType):
    room_id = graphene.Int()
    organization_name = graphene.String()
    contact_email = graphene.String()
    event_name = graphene.String()
    number_of_attendees = graphene.Int()
    booking_date = graphene.Date()
    start_time = graphene.Time()
    end_time = graphene.Time()
    

class BookingRoomObject(graphene.ObjectType):
    id = graphene.ID()
    organization_name = graphene.String()
    contact_email = graphene.String()
    event_name = graphene.String()
    number_of_attendees = graphene.Int()
    booking_date = graphene.Date()
    start_time = graphene.Time()
    end_time = graphene.Time()
    
class RegisterRoomInputObject(graphene.InputObjectType):
    name = graphene.String()
    capacity = graphene.Int()
    price = graphene.Float()
    location = graphene.String()
    description = graphene.String()
    
class RegisterRoomObject(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    capacity = graphene.Int()
    price = graphene.Float()
    location = graphene.String()
    description = graphene.String()
    image = graphene.String()
    
    def resolve_image(self, info):
        # Prepend MEDIA_URL to the relative image path
        if self.image:
            return f"{settings.MEDIA_URL}{self.image}"
        return None 

class GithubAoth(graphene.ObjectType):
    username = graphene.String()
    email = graphene.String()

