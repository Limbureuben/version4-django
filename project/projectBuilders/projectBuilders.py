import graphene
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from project_dto.project import *
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class UserBuilder:
    @staticmethod
    def register_user(username, email, password, password_confirm):
        if password != password_confirm:
            raise ValidationError("Password do not match")
        
        user = User(username=username, email=email)
        user.set_password(password)
        user.save()
        return user
    
    
    @staticmethod
    def login_user(username, password):
        user = authenticate(username=username, password=password)
        if user is None:
            raise ValidationError('Invalid username or password')

    # Check if the user's email is verified unless they are a superuser
        if not user.is_superuser and not user.userprofile.is_email_verified:
            raise ValidationError('Email not verified')

    # Create tokens for the authenticated user
        refresh = RefreshToken.for_user(user)
        return {
            'user': user,
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token),
        }


        
    @staticmethod
    def create_event(event_username, event_name, event_date, event_location, event_category):
        try:
            event = Event(
                event_username = event_username,
                event_name = event_name,
                event_date = event_date,
                event_location = event_location,
                event_category = event_category
                # image = image
            )
            event.save()
            return event
        except Exception as e:
            print("Error creating event: {e}")
            return None
        
        
    @staticmethod
    def update_event(event_id, event_username=None, event_name=None, event_date=None, event_location=None, event_category=None):
        try:
            event = Event.objects.get(id=event_id)
            
            #update the provide fields
            if event_username is not None:
                event.event_username = event_username
            if event.event_name is not None:
                event.event_name = event_name
            if event.event_date is not None:
                event.event_date = event_date
            if event.event_location is not None:
                event.event_location = event_location
                
            event.save()
            return event
        except Event.DoesNotExist:
            print(f"Event with ID {event_id} does not exist.")
            return None
        except Exception as e:
            print(f"Error updating event: {e}")
            return None
    
    
    
    @staticmethod
    def application_event(name, email, status, event_id):
        try:
            event_application = EventApplication(
                name = name,
                email = email,
                status = status,
                event_id = event_id
            )
            
            event_application.save()
            
            return event_application
        except Exception as e:
            print('Error creating event application: {e}')
            return None
        
    @staticmethod
    def conference_room_booking(
        room_id,
        organization_name,
        contact_email,
        event_name,
        number_of_attendees,
        booking_date,
        start_time,
        end_time,
    ):
        try:
            room = Room.objects.get(id=room_id)
            
            if number_of_attendees > room.capacity:
                raise ValidationError("Number of attendees exceeds room capacity")
            
            room_booking = RoomBooking(
                room = room,
                organization_name = organization_name,
                contact_email = contact_email,
                event_name = event_name,
                number_of_attendees = number_of_attendees,
                booking_date = booking_date,
                start_time = start_time,
                end_time = end_time,
            )
        
            room_booking.save()
            return room_booking
        except Room.DoesNotExist:
            print("Error: Room does not exist")
            return None
        except Exception as e:
            print(f"Error creating a room booking: {e}")
            return None
        
        
    @staticmethod
    def register_room(name, capacity, price, location, description):
        room = Room(
            name=name,
            capacity=capacity,
            price=price,
            location=location,
            description=description
        )
        room.full_clean()  # Ensure data validation before saving
        room.save()
        return room

    
    
    

class UserProfileBuilder:
    
    @staticmethod
    def create_user_profile(user: User) ->UserProfileObject:
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
        
    @staticmethod
    def reset_user_password(user, old_password, new_password, new_password_confirm):
        try:
            # Check if the new passwords match
            if new_password != new_password_confirm:
                return {
                    'success': False,
                    'message': 'New password does not match confirmation'
                }
                
            # Verify the old password
            if not user.check_password(old_password):
                return {
                    'success': False,
                    'message': 'The old password is incorrect'
                }
                
            # Validate the new password against Django's password rules
            validate_password(new_password, user)
            
            # Set and save the new password
            user.set_password(new_password)
            user.save()
            
            return {
                'success': True,
                'message': 'Password reset successfully'
            }
        
        except ValidationError as e:
            # Handle password validation errors (e.g., too short, too common, etc.)
            return {
                'success': False,
                'message': ' '.join(e.messages)  # Join multiple validation error messages
            }
            
        except Exception as e:
            # General exception handling
            print(f"Error resetting password: {e}")
            return {
                'success': False,
                'message': 'An error occurred during password reset'
            }
            





























        


import base64
from io import BytesIO
from django.contrib.staticfiles import finders
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import qrcode
from PIL import Image, ImageDraw
import tempfile
import os



class TicketService:
    @staticmethod
    def generate_ticket(application):
        ticket_id = f"TKT-{application.id}"
        qr_data = f"Ticket ID: {ticket_id}\nEvent: {application.event.event_name}\nName: {application.name}\nEmail: {application.email}\nStatus: {application.status}"

        # Generate QR code and save to a temporary file
        qr = qrcode.make(qr_data)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as qr_temp_file:
            qr_temp_file_name = qr_temp_file.name
            qr.save(qr_temp_file_name)

        # Set ticket dimensions
        ticket_width = 595  # A5 Landscape width
        ticket_height = 300  # Sleek ticket height

        # Create PDF in memory
        pdf_buffer = BytesIO()
        pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=(ticket_width, ticket_height))

        # HEADER SECTION
        header_color = colors.lightseagreen
        pdf_canvas.setFillColor(header_color)
        pdf_canvas.rect(0, ticket_height - 60, ticket_width, 60, fill=True, stroke=False)  # Header background
        pdf_canvas.setFont("Helvetica-Bold", 20)
        pdf_canvas.setFillColor(colors.white)
        pdf_canvas.drawString(20, ticket_height - 40, application.event.event_name.upper())  # Event name

        # Handle Logo with Header Background Color
        logo_path = finders.find("myapp/images/logo1.png")  # Adjust to your logo path
        if logo_path:
            # Open the logo image
            logo_image = Image.open(logo_path)

            # Convert to RGBA and fill transparent areas with header color
            if logo_image.mode != 'RGBA':
                logo_image = logo_image.convert('RGBA')
            header_rgb = (32, 178, 170, 255)  # Convert lightseagreen to RGBA
            background_layer = Image.new("RGBA", logo_image.size, header_rgb)
            logo_image = Image.alpha_composite(background_layer, logo_image)

            # Resize and save the processed logo
            logo_image = logo_image.resize((50, 50))  # Resize to fit header
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as logo_temp_file:
                logo_temp_file_name = logo_temp_file.name
                logo_image.save(logo_temp_file_name, format="PNG")

            # Draw the logo in the header
            pdf_canvas.drawImage(logo_temp_file_name, ticket_width - 80, ticket_height - 55, width=50, height=50)

        # CELEBRATION POPUP SECTION
        pdf_canvas.setFillColor(colors.gold)
        pdf_canvas.setFont("Helvetica-Bold", 24)
        # pdf_canvas.drawString(20, ticket_height - 90, "🎉 CONGRATULATIONS! 🎉")
        # pdf_canvas.drawString(20, ticket_height - 90, "CONGRATULATIONS! ")
        pdf_canvas.setFillColor(colors.darkgreen)
        pdf_canvas.setFont("Helvetica", 12)
        pdf_canvas.drawString(20, ticket_height - 110, "You have successfully registered for the event!")

        # EVENT DETAILS SECTION
        pdf_canvas.setFont("Helvetica-Bold", 14)
        pdf_canvas.setFillColor(colors.darkblue)
        details_start_y = ticket_height - 140
        line_spacing = 20

        pdf_canvas.drawString(20, details_start_y, f"Ticket ID: {ticket_id}")
        pdf_canvas.drawString(20, details_start_y - line_spacing, f"Name: {application.name}")
        pdf_canvas.drawString(20, details_start_y - 2 * line_spacing, f"Email: {application.email}")
        pdf_canvas.drawString(20, details_start_y - 3 * line_spacing, f"Event Date: {application.event.event_date}")
        pdf_canvas.drawString(20, details_start_y - 4 * line_spacing, f"Location: {application.event.event_location}")
        pdf_canvas.drawString(20, details_start_y - 5 * line_spacing, f"Status: {application.status}")

        # QR CODE SECTION
        pdf_canvas.drawImage(qr_temp_file_name, ticket_width - 150, details_start_y - 80, width=100, height=100)

        # FOOTER SECTION
        pdf_canvas.setFont("Helvetica-Oblique", 10)
        pdf_canvas.setFillColor(colors.gray)
        pdf_canvas.drawString(20, 30, "Please bring this ticket to the event for entry. Thank you!")

        # Save PDF and encode it in Base64
        pdf_canvas.showPage()
        pdf_canvas.save()
        pdf_buffer.seek(0)
        encoded_pdf = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')

        # Clean up temporary files
        os.remove(qr_temp_file_name)
        if logo_path:
            os.remove(logo_temp_file_name)

        return ticket_id, encoded_pdf




















# class TicketService:
#     @staticmethod
#     def generate_ticket(application):
#         ticket_id = f"TKT-{application.id}"

#         # Data to encode in QR code
#         qr_data = f"Ticket ID: {ticket_id}\nEvent: {application.event.event_name}\nName: {application.name}\nEmail: {application.email}\nStatus: {application.status}"

#         # Generate QR code and save to temporary file
#         qr = qrcode.make(qr_data)
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as qr_temp_file:
#             qr_temp_file_name = qr_temp_file.name
#             qr.save(qr_temp_file_name)

#         # Create a PDF in memory
#         pdf_buffer = BytesIO()

#         # Define the size of the ticket exactly
#         ticket_width = 595  # width in points (landscape A5 width)
#         ticket_height = 420  # height in points (landscape A5 height)
        
#         # Create a canvas with the exact size of the ticket
#         pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=(ticket_width, ticket_height))

#         # Load university logo image from static files
#         logo_path = finders.find("myapp/images/logo1.png")  # Adjust the path as needed
#         if logo_path:
#             # Open the logo image and handle transparency if present
#             logo_image = Image.open(logo_path)
#             # Ensure the logo image has transparency (RGBA)
#             if logo_image.mode != 'RGBA':
#                 logo_image = logo_image.convert('RGBA')

#             # Resize the logo to fit the ticket's design
#             logo_image = logo_image.resize((120, 120))  # Increased size (120x120)

#             # Now, we'll replace transparent areas with the ticket's background color
#             # Create a new image with the same size, filling it with the lightgrey color
#             background_color = (211, 211, 211, 255)  # lightgrey in RGBA (with full opacity)
#             new_image = Image.new('RGBA', logo_image.size, background_color)
#             new_image.paste(logo_image, (0, 0), logo_image)  # Paste the logo onto the background

#             # Save the new logo to a temporary file
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as logo_temp_file:
#                 logo_temp_file_name = logo_temp_file.name
#                 new_image.save(logo_temp_file_name, format="PNG")

#             # Position the logo inside the ticket card, near the QR code
#             qr_x = 400  # QR code position on the left
#             qr_y = 150  # QR code position within the ticket card
#             logo_x = qr_x - 130  # Logo is positioned to the left of the QR code
#             logo_y = qr_y  # Keep the logo at the same vertical position as the QR code

#             # Draw the ticket content card with lightgrey background
#             pdf_canvas.setFillColor(colors.lightgrey)
#             pdf_canvas.roundRect(30, 100, 510, 220, 10, fill=1)

#             # Set the border color to lightseagreen
#             pdf_canvas.setStrokeColor(colors.lightseagreen)
#             pdf_canvas.setLineWidth(2)  # Optional: Adjust the thickness of the border
#             pdf_canvas.roundRect(30, 100, 510, 220, 10, fill=0)  # Draw the border

#             # Draw the QR code on the card
#             pdf_canvas.drawImage(qr_temp_file_name, qr_x, qr_y, width=100, height=100)

#             # Draw the logo image over the ticket card with the background color
#             pdf_canvas.drawImage(logo_temp_file_name, logo_x, logo_y, width=120, height=120)

#         # Header Section (drawn above the ticket card)
#         pdf_canvas.setFillColor(colors.midnightblue)
#         pdf_canvas.setFont("Helvetica-Bold", 18)
#         pdf_canvas.setFillColor(colors.white)
#         pdf_canvas.drawString(160, 330, "Event Ticket")

#         # Ticket Details Section
#         pdf_canvas.setFont("Helvetica", 12)
#         pdf_canvas.setFillColor(colors.darkblue)
#         pdf_canvas.drawString(60, 300, f"Event Name: {application.event.event_name}")
#         pdf_canvas.drawString(60, 280, f"Name: {application.name}")
#         pdf_canvas.drawString(60, 260, f"Email: {application.email}")
#         pdf_canvas.drawString(60, 240, f"Status: {application.status}")
#         pdf_canvas.drawString(60, 220, f"Ticket ID: {ticket_id}")
#         pdf_canvas.drawString(60, 200, f"Date: {application.event.event_date}")
#         pdf_canvas.drawString(60, 180, f"Location: {application.event.event_location}")

#         # Footer Message
#         pdf_canvas.setFillColor(colors.darkblue)
#         pdf_canvas.setFont("Helvetica-Oblique", 10)
#         pdf_canvas.drawString(60, 140, "Thank you for your participation! Please keep this ticket safe.")

#         # Save and Encode PDF
#         pdf_canvas.showPage()
#         pdf_canvas.save()
#         pdf_buffer.seek(0)

#         # Base64 encode the PDF
#         pdf_bytes = pdf_buffer.getvalue()
#         encoded_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

#         # Cleanup temporary files
#         os.remove(qr_temp_file_name)
#         if logo_path:
#             os.remove(logo_temp_file_name)

#         return ticket_id, encoded_pdf




