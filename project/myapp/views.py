import datetime
import logging
from django.http import JsonResponse
from django.shortcuts import render
from graphql import GraphQLError
import jwt
import requests
from projectBuilders.projectBuilders import UserBuilder, TicketService, UserProfileBuilder
from project_dto.project import *
from .models import *
import graphene
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from project_dto.Response import *

from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.views import APIView # type: ignore
from .serializer import FileSerializer
from .models import Files
from rest_framework.response import Response # type: ignore
from graphene import Mutation, Boolean, String
from django.core.exceptions import PermissionDenied
import base64
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.http import HttpResponse
from .tasks import send_verification_email
import uuid
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
import paypalrestsdk
from django.views.decorators.csrf import ensure_csrf_cookie

    
class RegisterUser(graphene.Mutation):
    user = graphene.Field(UserRegistrationObject)
    success = graphene.Boolean()
    message = graphene.String()
    
    class Arguments:
        input = UserRegistrationInputObject(required=True)
        
    def mutate(self, info, input):
        
        username = input.username
        email = input.email
        password = input.password
        password_confirm = input.password_confirm
        
        ##check if the user exist
        if User.objects.filter(username=username).exists():
            return RegisterUser(success=False, message="username alredy exists")
        
        ##check if the email exist
        if User.objects.filter(email=email).exists():
            return RegisterUser(success=False, message="Email alredy exists")
        
        if password != password_confirm:
            return RegisterUser(success=False, message="Passwords do not match")
        
        user = User(username=username, email=email)
        user.set_password(password)
        user.is_superuser = False
        user.is_staff = False
        user.save()
        
        user_profile = UserProfile(user=user, verification_token=uuid.uuid4())
        user_profile.save()
        print("Token are created here")
        
        # Generate verification URL
        # verification_url = f"{settings.FRONTEND_URL}/verify-email/{user_profile.verification_token}/"
        verification_url = f"{settings.BACKEND_URL}/verify-email/{user_profile.verification_token}/"

        print("Token can also pass here 2")
        # Call Celery task
        send_verification_email.delay(email, verification_url)
        
        return RegisterUser(
            user=UserRegistrationObject(id=user.id, username=user.username, email=user.email),
            success=True,
            message="Registration successful. Please check your email to verify your account."
        )

        
def verify_email(request, token):
    try:
        user_profile = UserProfile.objects.get(verification_token=token)
        user_profile.is_email_verified = True
        user_profile.user.is_active = True
        user_profile.user.save()
        print("Data pass here")
        user_profile.save()
        # return redirect('/login')
        # return HttpResponseRedirect(f"{settings.FRONTEND_URL}/verification-success")  # or '/login' for angular
        return HttpResponseRedirect(f"{settings.FRONTEND_URL}/") # for vue
    except UserProfile.DoesNotExist:
        return HttpResponse("Invalid verification token.", status=400)





class LoginUser(graphene.Mutation):
    user = graphene.Field(UserLoginObject)
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        input = UserLoginInputObject(required=True)
        
    def mutate(self, info, input):
        username = input.username
        password = input.password

        try:
            # Authenticate and log in the user
            result = UserBuilder.login_user(username, password)
            user = result['user']
            
            # Check if the user is a superuser
            is_superuser = user.is_superuser
            
            return LoginUser(
                user=UserLoginObject(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    refresh_token=result['refresh_token'],
                    access_token=result['access_token'],
                    isSuperuser=is_superuser
                ),
                success=True,
                message="Login successful",
            )
        except ValidationError as e:
            return LoginUser(success=False, message=str(e))
        except Exception as e:
            return LoginUser(success=False, message="An error occurred during login.")


        
class RegisterEvent(graphene.Mutation):
    class Arguments:
        input = EventRegistrationInputObject(required=True)
        # file = Upload(required=True)
    
    event = graphene.Field(EventRegistrationObject)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, input):
        try:
            # image_file = input.image if 'image' in input else None
            
            event_instance = Event.objects.create(
                event_username = input.event_username,
                event_name = input.event_name,
                event_date=input.event_date,
                event_location=input.event_location,
                event_category=input.event_category
                # image = image_file
            )
            
            # Create the event response object
            event_response = EventRegistrationObject(
                event_username=event_instance.event_username,
                event_name=event_instance.event_name,
                event_date=event_instance.event_date,
                event_location=event_instance.event_location,
                event_category=event_instance.event_category,
                # image = event_instance.image.url if event_instance.image else None
            )
            
            return RegisterEvent(
                event=event_response,
                success=True,
                message="Event registered successfully."
            )
            
        except Exception as e:
            # Handle exceptions and return error message
            return RegisterEvent(
                event=None,
                success=False,
                message=str(e)  # or a custom error message
            )


class UpdateEvent(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    event = graphene.Field(EventRegistrationObject)
    
    class Arguments:
        input = EventUpdateInputObject(required=True)
        
    def mutate(self, info, input):
        try:
            #chukua events kwa ID zake
            event_instance = Event.objects.get(id=input.id)
            
            #then update the event
            if input.event_username is not None:
                event_instance.event_username = input.event_username
                
            if input.event_name is not None:
                event_instance.event_name = input.event_name
                
            if input.event_date is not None:
                event_instance.event_date = input.event_date
                
            if input.event_location is not None:
                event_instance.event_location = input.event_location
                
            if input.event_category is not None:
                event_instance.event_category = input.event_category
                
                ##then save the updates
            event_instance.save()
            
            
            #the create a response event
            event_response = EventRegistrationObject(
                id = event_instance.id,
                event_username = event_instance.event_username,
                event_name = event_instance.event_name,
                event_date = event_instance.event_date,
                event_location = event_instance.event_location,
                event_category = event_instance.event_category
            )
            
            return UpdateEvent(
                event = event_response,
                success = True,
                message = "Event update successfully"
            )
            
        except Event.DoesNotExist:
            return UpdateEvent(
                event=None,
                success=False,
                message='Event not found'
            )
            
        except Exception as e:
            
            #handle chochote kitakachotokea
            return UpdateEvent(
                event=None,
                success=False,
                message=str(e)
            )
    

class DeleteEvent(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id):
        try:
            event = Event.objects.get(pk=id)
            event.delete()
            return DeleteEvent(
                success = True,
                message = 'Event delete successfully!'
            )
        except Event.DoesNotExist:
            return DeleteEvent(success=False, message='Event not found')
            


class DeleteApplication(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id):
        try:
            application = EventApplication.objects.get(pk=id)
            application.delete()
            return DeleteApplication(
                success = True,
                message = 'Event Delete Successfully'
            )
        except EventApplication.DoesNotExist:
            return DeleteApplication(success=False, message='Failed to delete event')
        
        
        

class ApplicationEvent(graphene.Mutation):
    class Arguments:
        input = EventApplicationInputObject(required=True)
        
    success = Boolean()
    message = String()
    application = graphene.Field(EventApplicationObject)
    ticket_pdf = graphene.String()
    
    def mutate(self, info, input):
        application = UserBuilder.application_event(
            name=input.name,
            email=input.email,
            status=input.status,
            event_id=input.event_id
        )
        
        if application:
            ticket_id, encoded_pdf = TicketService.generate_ticket(application)
            
            application.ticket_id = ticket_id
            application.save()
            
            
            return ApplicationEvent(
                success=True,
                message='Application successfully created with ticket generated',
                application=application,
                ticket_pdf=encoded_pdf
            )
        else:
            return ApplicationEvent(
                success=False,
                message="Failed to complete application",
                application=None,
                ticket_pdf=None,
            )
            



class ConferenceRoomBooking(graphene.Mutation):
    message = graphene.String()
    success = graphene.Boolean()
    booking = graphene.Field(BookingRoomObject)
    total_price = graphene.Float()
    
    class Arguments:
        input = BookingRoomInputObject(required=True)
        
    def mutate(self, info, input):
        booking = UserBuilder.conference_room_booking(
            room_id = input.room_id,
            organization_name = input.organization_name,
            contact_email = input.contact_email,
            event_name = input.event_name,
            number_of_attendees = input.number_of_attendees,
            booking_date = input.booking_date,
            start_time  =input.start_time,
            end_time = input.end_time
        )
        
        if booking:
            total_price = booking.room.price_per_hour * (
                (input.end_time.hour - input.start_time.hour) + (input.end_time.minute - input.start_time.minute) / 60
            )
            
            return ConferenceRoomBooking(
                success  =True,
                message = "Room Booked successfully",
                booking = booking,
                total_price = total_price,
            )
        else:
            
            return ConferenceRoomBooking(
                success = False,
                message = "Failed to book room",
                booking = None,
                total_price = 0,
            )
            

class RegisterRoom(graphene.Mutation):
    message = graphene.String()
    success = graphene.Boolean()
    room = graphene.Field(RegisterRoomObject)

    class Arguments:
        input = RegisterRoomInputObject(required=True)

    def mutate(self, info, input):
        try:
            # Ensure name is one of the pre-defined choices
            valid_room_names = [room[0] for room in Room.SELECT_ROOM]
            if input.name not in valid_room_names:
                raise ValueError(f"Invalid room name. Allowed values are: {', '.join(valid_room_names)}")

            # Ensure the room has not already been registered
            if Room.objects.filter(name=input.name).exists():
                raise ValueError(f"Room '{input.name}' has already been registered.")

            # Additional validations
            if input.capacity <= 0:
                raise ValueError("Capacity must be greater than 0.")
            if input.price <= 0:
                raise ValueError("Price must be greater than 0.")
            if not input.location or not input.description:
                raise ValueError("Location and description are required.")

            # Save the room
            room = UserBuilder.register_room(
                name=input.name,
                capacity=input.capacity,
                price=input.price,
                location=input.location,
                description=input.description
            )

            return RegisterRoom(
                success=True,
                message="Room registered successfully",
                room=room
            )

        except ValueError as ve:
            return RegisterRoom(
                success=False,
                message=str(ve),
                room=None
            )

        except Exception as e:
            print(f"Unexpected error: {e}")
            return RegisterRoom(
                success=False,
                message="Failed to register room due to an unexpected error.",
                room=None
            )


class RequestRoom(graphene.Mutation):
    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        room_id = graphene.Int()
        
    def mutate(self, info, room_id):
        try:
            room = Room.objects.get(id=room_id)
            
            if room.is_available and not room.is_requested:
                room.is_requested = True
                room.save()
                return RequestRoom(
                    success = True,
                    message = "Room request successfully"
                )
            else:
                return RequestRoom(
                    success = False,
                    message = "Room is alredy taken"
                )
        except Room.DoesNotExist:
            return RequestRoom(success=False, message="Room not found")
        
def create_order(request):
    room_id = request.data.get('room_id')
    try:
        room = Room.objects.get(id=room_id)  # Ensure the room exists
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room not found'}, status=404)



paypalrestsdk.configure({
    "mode": settings.PAYPAL_ENVIRONMENT,  # "sandbox" or "live"
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_SECRET_KEY,
})

@csrf_exempt  # Exempt CSRF for PayPal API requests
def create_paypal_order(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            room_id = data.get("roomId")
            
            if not room_id:
                return JsonResponse({"error": "Room ID is required."}, status=400)

            # Fetch room details
            room = Room.objects.get(id=room_id)
            price = float(room.price)  # Ensure price is a valid float
            if price <= 0:
                return JsonResponse({"error": "Invalid room price."}, status=400)

            # Create a PayPal payment
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal",
                },
                "transactions": [{
                    "amount": {
                        "total": f"{price:.2f}",  # Format as a string with 2 decimals
                        "currency": "USD",  # Adjust currency if necessary
                    },
                    "description": f"Payment for {room.name} room booking",
                }],
                "redirect_urls": {
                    "return_url": f"{settings.BASE_URL}/rooms",
                    "cancel_url": f"{settings.BASE_URL}/payment/cancel/",
                }
            })

            if payment.create():
                # Find approval URL dynamically
                approval_url = next(link.href for link in payment.links if link.rel == "approval_url")
                return JsonResponse({"approval_url": approval_url})
            else:
                return JsonResponse({"error": payment.error}, status=500)

        except Room.DoesNotExist:
            return JsonResponse({"error": "Room not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=400)


@csrf_exempt
def payment_success(request):
    try:
        payment_id = request.GET.get('paymentId')  # PayPal payment ID
        payer_id = request.GET.get('PayerID')  # PayPal payer ID
        
        # Retrieve the payment details from PayPal
        payment = paypalrestsdk.Payment.find(payment_id)
        
        # Verify the payment
        if payment.execute({"payer_id": payer_id}):
            # The payment is successful
            # You can now update your database, confirm the booking, etc.
            room_id = payment.transactions[0].description.split(" ")[2]  # Example extraction
            room = Room.objects.get(id=room_id)
            room.status = "Booked"
            room.save()

            return JsonResponse({"status": "Payment successful!"}, status=200)
        else:
            return JsonResponse({"error": "Payment execution failed."}, status=400)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



def payment_success(request):
    return JsonResponse({"message": "Payment was successful!"})


def payment_cancel(request):
    return JsonResponse({"message": "Payment was canceled."})




@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({"message": "CSRF cookie set."})





class UserProfileQuery(graphene.ObjectType):
    user = graphene.Field(UserProfileObject, id=graphene.ID())

    def resolve_user(self, info, id):
        try:
            # Fetch the user from the database using the ID
            return User.objects.get(id=id)
        except User.DoesNotExist:
            return None




from graphene_django.views import GraphQLView # type: ignore
from .utils import authenticate_user

class MyGraphQLView(GraphQLView):
    def get_context(self, request):
        context = super().get_context(request)
        token = request.headers.get('Authorization', None)
        if token:
            user = authenticate_user(token)  # Authenticate using JWT
            context.user = user
        return context



    
    

from graphql_jwt.decorators import login_required # type: ignore
from .utils import reset_user_password
    
class ResetPassword(graphene.Mutation):
    
    class Arguments:
        input = ResetPasswordInputObject(required=True)
        
    success = graphene.Boolean()
    message = graphene.String()
        
    @login_required
    def mutate(self, info, input):
        user = info.context.user
        old_password = input.old_password
        new_password = input.new_password
        new_password_confirm = input.new_password_confirm
        
        
        result = reset_user_password(user, old_password, new_password, new_password_confirm)
        
        return ResetPassword(success=result['success'], message=result['message'])
    


class GitHubOAuthMutation(graphene.Mutation):
    class Arguments:
        code = graphene.String(required=True)

    success = graphene.Boolean()
    error = graphene.String()
    token = graphene.String()  # Add token to return the access token to the client

    def mutate(self, info, code):
        if not code:
            return GitHubOAuthMutation(success=False, error='Code is required')

        # Step 1: Get access token from GitHub
        try:
            token_response = requests.post(
                'https://github.com/login/oauth/access_token',
                data={
                    'client_id': settings.GITHUB_CLIENT_ID,
                    'client_secret': settings.GITHUB_CLIENT_SECRET,
                    'code': code,
                },
                headers={'Accept': 'application/json'}
            )
            token_response.raise_for_status()
        except requests.RequestException as e:
            return GitHubOAuthMutation(success=False, error=f'Error getting token: {str(e)}')

        token_data = token_response.json()
        if 'access_token' not in token_data:
            return GitHubOAuthMutation(success=False, error='Failed to retrieve access token')

        access_token = token_data['access_token']

        # Step 2: Fetch user info from GitHub
        try:
            user_response = requests.get(
                'https://api.github.com/user',
                headers={'Authorization': f'token {access_token}'}
            )
            user_response.raise_for_status()
        except requests.RequestException as e:
            return GitHubOAuthMutation(success=False, error=f'Error fetching user data: {str(e)}')

        user_data = user_response.json()
        if 'login' not in user_data:
            return GitHubOAuthMutation(success=False, error='Incomplete user data')

        # Step 3: Create or fetch user from the database
        user, created = User.objects.get_or_create(
            username=user_data['login'],
            defaults={'email': user_data.get('email', 'no-email@example.com')}  # Default email if None
        )

        # Return success with the access token
        return GitHubOAuthMutation(success=True, error=None, token=access_token)

        
        
class CategoryQuery(graphene.ObjectType):
    categories = graphene.List(CategoryObject)
    
    def resolve_categories(self, info):
        return Category.objects.all()

class EventQuery(graphene.ObjectType):
    all_events = graphene.List(EventObject)
    
    def resolve_all_events(self, info):
        return Event.objects.all()
    
class EventCountQuery(graphene.ObjectType):
    event_count = graphene.Int(description="Nipate number zote za event")
    
    def resolve_event_count(self, info):
        return Event.objects.count()


class EventUserQuery(graphene.ObjectType):
    eventuser_count = graphene.Int(description='Total applications')
    
    def resolve_eventuser_count(self, info):
        return EventApplication.objects.count()
    
class EventApplicationQuery(graphene.ObjectType):
    all_application = graphene.List(EventApplicationObject)
    
    def resolve_all_application(self, info):
        return EventApplication.objects.all()
    
class RoomQuery(graphene.ObjectType):
    rooms = graphene.List(RegisterRoomObject)
    
    def resolve_rooms(self, info):
        return Room.objects.filter(is_available=True)
    

class UserQuery(graphene.ObjectType):
    users = graphene.List(UserRegistrationObject)
    
    def resolve_users(self, info):
        return User.objects.all()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

class FileUploadView(APIView):
    def post(self, request):
        file = request.FILES.get("file")
        
        if file:
            try:
                saved_file = Files.objects.create(file=file)
                return Response({"error": False, "data": FileSerializer(saved_file).data})
            except Exception as e:
                return Response({"error": True, "message": str(e)})
            
        return Response({"error": True, "message": "No file uploaded"})
    
    def get(self, request):
        try:
            data = Files.objects.all()
            return Response(FileSerializer(instance=data, many=True).data)
        except Exception as e:
            return Response({"error": True, "message": str(e)})















































































































# @csrf_exempt
# def execute_code(request):
#     if request.method == 'POST':
#         try:
#             # Parse the JSON data
#             data = json.loads(request.body)
#             temperature = data.get('temperature')
#             humidity = data.get('humidity')

#             # Print the temperature and humidity to the console
#             print(f"Temperature: {temperature} °C")
#             print(f"Humidity: {humidity} %")

#             # Save data to the Weather model
#             if temperature is not None and humidity is not None:
#                 Weather.objects.create(
#                     temperature=int(temperature),  # Ensure it's stored as an integer
#                     humidity=int(humidity)         # Ensure it's stored as an integer
#                 )
#                 return JsonResponse({'status': 'success', 'message': 'Data received and stored successfully'}, status=200)
#             else:
#                 return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
#         except json.JSONDecodeError:
#             return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
#         except ValueError:
#             return JsonResponse({'status': 'error', 'message': 'Invalid data type'}, status=400)
#     else:
#         return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# from rest_framework import viewsets
# from rest_framework.response import Response
# from rest_framework.decorators import api_view
# from rest_framework import viewsets
# from rest_framework.response import Response
# from rest_framework.decorators import api_view
# from .models import Weather
# # from .serializers import WeatherSerializer
# # import pandas as pd
# from rest_framework.views import APIView
# from .serializer import FileSerializer
# from .models import Files

# from rest_framework.parsers import FileUploadParser
# @api_view(['GET'])
# def hourly_average_summary(request):
#     data = Weather.objects.all().order_by('created_at')
#     serializer = WeatherSerializer(data, many=True)
#     df = pd.DataFrame(serializer.data)
#     df['created_at'] = pd.to_datetime(df['created_at'])
#     df.set_index('created_at', inplace=True)
#     df_resampled = df.resample('10T').agg({
#         'temperature': 'mean',
#         'humidity': 'mean'
#     }).reset_index()
#     df_resampled.fillna(0, inplace=True)  # Replace NaN values with 0
    
#     df_resampled.replace([float('inf'), float('-inf')], 0, inplace=True)  # Replace infinite values with 0
    
#     # Delete rows where either 'Temperature Average' or 'Humidity Average' is 0
#     df_resampled = df_resampled[(df_resampled['temperature'] != 0) & (df_resampled['humidity'] != 0)]
#     df_resampled.replace([float('inf'), float('-inf')], 0, inplace=True)  # Replace infinite values with 0
#     df_resampled.columns = ['Date', 'Temperature Average', 'Humidity Average']
#     response_data = df_resampled.to_dict(orient='records')
#     return Response(response_data)



# @api_view(['GET'])
# def current_weather(request):
#     try:
#         # Retrieve the latest weather record
#         latest_weather = Weather.objects.latest('created_at')
        
#         # Serialize the latest weather record
#         serializer = WeatherSerializer(latest_weather)
        
#         # Return the serialized data
#         return Response(serializer.data)
    
#     except Weather.DoesNotExist:
#         # If no weather data is available, return an empty response or an error message
#         return Response({"error": "No weather data available."}, status=404)
    
    
