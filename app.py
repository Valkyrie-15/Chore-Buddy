import redis
from flask_caching import Cache
from functools import wraps
from flask import Flask, json , jsonify, request, send_from_directory
from flask_cors import CORS
from sqlalchemy import func
from backend.tasks import download_csv
from backend.model import Customer, Payment, Professional, ServiceRequest, ServiceReview, Services, User, db
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, current_user, get_jwt, get_jwt_identity,jwt_required, unset_jwt_cookies
from datetime import datetime, timedelta
from backend.celery_init import celery_init_app
from celery.result import AsyncResult

app = Flask(__name__)
celery = celery_init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
app.config['JWT_SECRET_KEY'] = 'data'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)

app.config.from_object(__name__)
db.init_app(app)
CORS(app, resources={r"/*":{'origins':"*"}})

app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
jwt = JWTManager(app)



#cache configuration
redis_client = redis.Redis(host='localhost',port=6379,db=0)
cache = Cache(app,config={'CACHE_TYPE':'redis','CACHE_REDIS':redis_client})





def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()  # Get full JWT claims
        if claims.get("role") != "admin":
            return jsonify(message="Admin access required"), 403
        return fn(*args, **kwargs)
    return wrapper




@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    
    # First check if user exists
    if not user:
        return {'message': 'Invalid Username or password'}, 401
    
    # Then check if password is correct
    if not check_password_hash(user.password, password):
        return {'message': 'Invalid Username or password'}, 401
    
    # If we get here, user exists and password is correct
    # Now check if user is approved
    if not user.approved:
        return {'message': 'Please wait for approval from admin'}, 400
    
    # User exists, password is correct, and user is approved
    access_token = create_access_token(identity=user.id, additional_claims={"role": user.role})
    print(access_token)
    user_info = {
        "id": user.id,
        "username": user.username,
        "role": user.role
    }

    return {'access_token': access_token, "user": user_info}, 200



@app.route('/approve_professional/<int:user_id>', methods=['POST'])
def approve_professional(user_id):
    professional = Professional.query.filter_by(user_id=user_id).first()
    if not professional:
        return jsonify({"message": "Professional not found"}), 404

    user = User.query.get(professional.user_id)
    if user:
        user.approved = True
        db.session.commit()
        return jsonify({"message": "Professional approved successfully"}), 200
    else:
        return jsonify({"message": "User not found"}), 404
    
    

@app.route('/approved_professionals', methods=['GET'])
def get_approved_professionals():
    professionals = Professional.query.join(User).filter(User.approved == True).all()
    
    result = []
    for professional in professionals:
        result.append({
            "id": professional.id,
            "fullname": professional.fullname,
            "service": professional.service.service_name,
            "experience": professional.experience,
            "contact": professional.contact,
            "address": professional.address,
            "pin_code": professional.pin_code
        })
    
    return jsonify(result)


@app.route('/pending_professionals', methods=['GET'])
def get_pending_professionals():
    professionals = Professional.query.join(User).filter(User.approved == False).all()
    
    result = []
    for professional in professionals:
        result.append({
            "id": professional.id,
            "fullname": professional.fullname,
            "service": professional.service.service_name
        })
    
    return jsonify(result)


@app.route('/all_users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    user_list = []

    for user in users:
        # Basic user data
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'approved': user.approved,
            'fullname': None,
            'service': None,
            'flagged_status': user.flagged if hasattr(user, 'flagged') else False
        }
        
        # Handle different data models based on role
        try:
            if user.role == 'professional':
                # For Professional users
                professional = None
                # Direct query to get professional data
                #from model import Professional  # Import your Professional model
                professional = Professional.query.filter_by(user_id=user.id).first()
                
                if professional:
                    user_data['fullname'] = professional.fullname
                    # Handle service if it exists
                    if hasattr(professional, 'service') and professional.service:
                        user_data['service'] = professional.service.service_name
            
            elif user.role == 'customer':
                # For Customer users
                customer = None
                # Direct query to get customer data
                #from model import Customer  # Import your Customer model
                customer = Customer.query.filter_by(user_id=user.id).first()
                
                if customer:
                    user_data['fullname'] = customer.fullname
        except Exception as e:
            print(f"Error processing user {user.username}: {str(e)}")
            # Continue without failing the entire request
            
        user_list.append(user_data)

    return jsonify(user_list)




@app.route('/flag_user/<int:user_id>', methods=['POST'])
def flag_user(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.approved = False  
    user.flagged_status = True  # Mark as flagged
    db.session.commit()
    
    return jsonify({'message': f'User {user.username} has been flagged'}), 200


# Add a new service
@app.route('/api/services', methods=['POST'])
def add_service():
    # Parse request data
    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 400
    
    data = request.get_json()
    
    # Validate required fields
    if 'name' not in data:
        return jsonify({"message": "Name is required"}), 400
    if 'basePrice' not in data:
        return jsonify({"message": "Base price is required"}), 400
    
    # Check if service already exists
    if Services.query.filter_by(service_name=data['name']).first():
        return jsonify({"message": "Service already exists"}), 400
    
    # Create new service with all fields
    new_service = Services(
        service_name=data['name'],
        base_price=data['basePrice'],
        timing=data.get('timing'),  # Optional fields use .get() with default None
        location=data.get('location'),
        is_closed=data.get('isClosed', False)  # Default to False if not provided
    )
    
    db.session.add(new_service)
    db.session.commit()
    
    return jsonify({"message": "Service created successfully"}), 201





# Update a service
@app.route('/api/services/<int:service_id>', methods=['PUT'])
def update_service(service_id):
    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 400
    
    data = request.get_json()
    
    service = Services.query.get(service_id)
    if not service:
        return jsonify({"message": "Service not found"}), 404
    
    # Update fields if provided
    if 'name' in data:
        service.service_name = data['name']
    if 'basePrice' in data:
        service.base_price = data['basePrice']
    if 'timing' in data:
        service.timing = data['timing']
    if 'location' in data:
        service.location = data['location']
    if 'isClosed' in data:
        service.is_closed = data['isClosed']
    
    db.session.commit()
    
    return jsonify({"message": "Service updated successfully"}), 200

# Delete a service
@app.route('/api/services/<int:service_id>', methods=['DELETE'])
def delete_service(service_id):
    service = Services.query.get(service_id)
    if not service:
        return jsonify({"message": "Service not found"}), 404
    
    db.session.delete(service)
    db.session.commit()
    
    return jsonify({"message": "Service deleted successfully"}), 200  # Added return statement







from flask import jsonify, request
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError

@app.route('/services', methods=['GET'])
@cache.cached(timeout=10)
def get_services():
    try:
        services = Services.query.all()
        return jsonify([{
            'id': s.id,
            'service_name': s.service_name,
            'base_price': s.base_price,
            'timing': s.timing,
            'location': s.location,
            'is_closed': s.is_closed
        } for s in services])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    try:
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'role', 'fullname', 
                         'contact', 'address', 'pin_code']
        if data['role'] == 'professional':
            required_fields.extend(['service_id', 'experience'])
        
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        # Validate service_id for professionals
        if data['role'] == 'professional':
            service = Services.query.get(data['service_id'])
            if not service:
                return jsonify({'error': 'Invalid service ID'}), 400
            if service.is_closed:
                return jsonify({'error': 'This service is currently closed'}), 400

        # Create user and role-specific record
        user = User(
            username=data['username'],
            email=data['email'],
            password=generate_password_hash(data['password']),
            role=data['role']
        )
        
        # Set approved status based on role
        if data['role'] == 'customer':
            user.approved = True
        else:
            user.approved = False  # Explicitly set to False for professionals
        
        try:
            db.session.add(user)
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'Username or email already exists'}), 409

        if data['role'] == 'professional':
            professional = Professional(
                user_id=user.id,
                fullname=data['fullname'],
                service_id=data['service_id'],
                experience=data['experience'],
                contact=data['contact'],
                address=data['address'],
                pin_code=data['pin_code']
            )
            db.session.add(professional)
        else:
            customer = Customer(
                user_id=user.id,
                fullname=data['fullname'],
                contact=data['contact'],
                address=data['address'],
                pin_code=data['pin_code']
            )
            db.session.add(customer)

        db.session.commit()
        return jsonify({'message': 'Signup successful!'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
    

@app.route('/logout', methods=['POST'])
@jwt_required()
def post(self):
    role = get_jwt_identity()
    print(role)
    resp = {"message":"Logged out successfully"}
    unset_jwt_cookies(jsonify(resp))
    return resp,200


@app.route('/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    """Create a new service booking and request"""
    # Get the current user ID from the JWT token
    current_user_id = get_jwt_identity()
    
    # Get customer details
    customer = Customer.query.filter_by(user_id=current_user_id).first()
    if not customer:
        return jsonify({'error': 'Customer profile not found'}), 404
    
    # Parse request data
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request data'}), 400
    
    # Validate required fields
    required_fields = ['service_id', 'booking_time']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if service exists
    service = Services.query.get(data['service_id'])
    if not service:
        return jsonify({'error': 'Service not found'}), 404
    
    # Check if service is closed/unavailable
    if service.is_closed:
        return jsonify({'error': 'This service is currently unavailable'}), 400
    
    try:
        # Parse booking time
        booking_time = datetime.fromisoformat(data['booking_time'].replace('Z', '+00:00'))
        
        # Find an available professional for this service
        # Query professionals who provide this service type
        # Order by those with fewest assigned pending requests
        from sqlalchemy import func
        
    # First, check if ANY professionals exist for this service
        all_professionals = Professional.query.filter_by(service_id=data['service_id']).all()
        print(f"Found {len(all_professionals)} professionals for service {data['service_id']}")

        if not all_professionals:
            return jsonify({'error': 'No professionals available for this service'}), 400

        # Then proceed with your more complex query
        professional = Professional.query.filter_by(
            service_id=data['service_id']
        ).outerjoin(
            ServiceRequest, 
            (ServiceRequest.professional_id == Professional.id) & 
            (ServiceRequest.status == 'pending')
        ).group_by(
            Professional.id
        ).order_by(
            func.count(ServiceRequest.id).asc()
        ).first()

        print(f"Selected professional: {professional.fullname if professional else 'None'}")
        
        if not professional:
            # If no professional found, create request without assigning a professional
            new_request = ServiceRequest(
                customer_id=customer.id,
                service_id=data['service_id'],
                status='pending',
                request_date=booking_time
            )
            
            # Add to database
            db.session.add(new_request)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Service request created and awaiting professional assignment',
                'request_id': new_request.id,
                'status': new_request.status
            }), 201
        
        # Create new service request with assigned professional
        new_request = ServiceRequest(
            customer_id=customer.id,
            service_id=data['service_id'],
            professional_id=professional.id,
            status='pending',
            request_date=booking_time
        )
        
        # Add to database
        db.session.add(new_request)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Service request created successfully',
            'request_id': new_request.id,
            'professional_name': professional.fullname,
            'status': new_request.status
        }), 201
        
    except ValueError as e:
        return jsonify({'error': f'Invalid datetime format: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create service request: {str(e)}'}), 500



@app.route('/my-bookings', methods=['GET'])
@jwt_required()

def get_all_bookings():
    user_id = get_jwt_identity()
    
    customer = Customer.query.filter_by(user_id=user_id).first()
    
    if not customer:
        return jsonify({"error": "Customer profile not found"}), 404
    
    bookings = ServiceRequest.query.filter_by(customer_id=customer.id).all()
    
    bookings_list = []
    for booking in bookings:
        booking_data = {
            "id": booking.id,
            "service_name": booking.service.service_name,
            "status": booking.status,
            "request_date": booking.request_date.strftime('%Y-%m-%d %H:%M:%S'),
            "professional": {
                "id": booking.professional.id if booking.professional else None,
                "name": booking.professional.fullname if booking.professional else "Not Assigned"
            } if booking.professional else None,
            # Add these new fields
            "price": booking.service.base_price,
            "duration": booking.service.timing
        }
        bookings_list.append(booking_data)
    
    return jsonify({"bookings": bookings_list}), 200



@app.route('/api/update-booking/<int:booking_id>', methods=['PUT'])
@jwt_required()
def update_booking(booking_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Verify user owns this booking
    customer = Customer.query.filter_by(user_id=user_id).first()
    if not customer:
        return jsonify({"error": "Customer profile not found"}), 404
        
    booking = ServiceRequest.query.filter_by(id=booking_id, customer_id=customer.id).first()
    if not booking:
        return jsonify({"error": "Booking not found or not authorized"}), 404
    
    # Only allow editing pending bookings
    if booking.status.lower() != 'pending':
        return jsonify({"error": "Only pending bookings can be edited"}), 400
    
    # Update the booking
    if 'request_date' in data:
        booking.request_date = datetime.fromisoformat(data['request_date'].replace('Z', '+00:00'))
    if 'duration' in data:
        booking.duration = data['duration']
    
    
    db.session.commit()
    
    return jsonify({"message": "Booking updated successfully"}), 200




@app.route('/update-booking-status/<int:booking_id>', methods=['PUT'])
@jwt_required()
def update_booking_status(booking_id):
    user_id = get_jwt_identity()
    customer = Customer.query.filter_by(user_id=user_id).first()

    if not customer:
        return jsonify({"error": "Customer profile not found"}), 404

    booking = ServiceRequest.query.filter_by(id=booking_id, customer_id=customer.id).first()

    if not booking:
        return jsonify({"error": "Booking not found or unauthorized"}), 404

    data = request.get_json()
    new_status = data.get("status")

    if new_status not in ["Cancelled", "Completed"]:
        return jsonify({"error": "Invalid status. Only 'Cancelled' or 'Completed' allowed."}), 400

    print(f"🔍 Before update: Booking ID {booking.id} has status {booking.status}")

    booking.status = new_status  # Updating status in memory

    print(f"✅ After update: Booking ID {booking.id} has status {booking.status}")

    try:
        db.session.commit()
        print("✅ Database commit successful")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error committing to database: {e}")
        return jsonify({"error": "Database update failed"}), 500

    return jsonify({"message": f"Booking status updated to {new_status}."}), 200



@app.route('/api/professional/requests', methods=['GET'])
@jwt_required()
@cache.cached(timeout=10)
def get_professional_requests():
    """Get all service requests assigned to the logged-in professional"""
    # Get current user ID from JWT token
    current_user_id = get_jwt_identity()
    
    # Get professional details
    professional = Professional.query.filter_by(user_id=current_user_id).first()
    if not professional:
        return jsonify({'error': 'Professional profile not found'}), 404
    
    # Get query parameters for filtering
    status = request.args.get('status', None)
    
    # Base query
    query = ServiceRequest.query.filter_by(professional_id=professional.id)
    
    # Apply status filter if provided
    if status:
        query = query.filter_by(status=status)
    
    # Order by request date, newest first
    requests = query.order_by(ServiceRequest.request_date.desc()).all()
    
    # Format the results
    results = []
    for req in requests:
        # Get customer and service details
        customer = Customer.query.get(req.customer_id)
        service = Services.query.get(req.service_id)
        
        results.append({
            'id': req.id,
            'customer_name': customer.fullname if customer else 'Unknown',
            'customer_contact': customer.contact if customer else 'N/A',
            'customer_address': customer.address if customer else 'N/A',
            'service_name': service.service_name if service else 'Unknown Service',
            'request_date': req.request_date.isoformat(),
            'status': req.status,
            'price': service.base_price if service else 0,
            'duration': service.timing if service else 0,
            'location': service.location if service else 'N/A',
            'created_at': req.created_at.isoformat() if hasattr(req, 'created_at') else None
        })
    
    return jsonify({
        'success': True,
        'requests': results,
        'total': len(results)
    }), 200




@app.route('/api/requests/<int:request_id>/status', methods=['PATCH'])
@jwt_required()
def update_request_status(request_id):
    """Update the status of a service request"""
    # Get current user ID from JWT token
    current_user_id = get_jwt_identity()
    
    # Get professional details
    professional = Professional.query.filter_by(user_id=current_user_id).first()
    if not professional:
        return jsonify({'error': 'Professional profile not found'}), 404
    
    # Get request data
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400
    
    # Valid status values
    valid_statuses = ['pending', 'accepted', 'rejected', 'completed', 'Cancelled']
    if data['status'] not in valid_statuses:
        return jsonify({'error': 'Invalid status value'}), 400
    
    # Find the service request
    service_request = ServiceRequest.query.get(request_id)
    if not service_request:
        return jsonify({'error': 'Service request not found'}), 404
    
    # Check if this professional is authorized to update this request
    if service_request.professional_id != professional.id:
        return jsonify({'error': 'Not authorized to update this request'}), 403
    
    # Update the status
    service_request.status = data['status']
    
    # Save to database
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Request status updated successfully',
            'status': service_request.status
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update request status: {str(e)}'}), 500




@app.route('/api/bookings/<int:booking_id>/pay', methods=['POST'])
@jwt_required()
def process_booking_payment(booking_id):
    """
    Process payment for a booking and update its status to 'paid'
    """
    # Get current user ID from JWT token
    user_id = get_jwt_identity()
    
    # Find the customer
    customer = Customer.query.filter_by(user_id=user_id).first()
    if not customer:
        return jsonify({'error': 'Customer profile not found'}), 404
    
    # Find the service request with its associated service
    service_request = ServiceRequest.query.filter_by(
        id=booking_id, 
        customer_id=customer.id
    ).first()
    
    # Validate the booking exists and is in a payable state
    if not service_request:
        return jsonify({'error': 'Booking not found'}), 404
    
    # Check if booking is in a state that can be paid
    valid_payment_statuses = ['Completed']
    if service_request.status not in valid_payment_statuses:
        return jsonify({
            'error': f'Cannot pay for booking with status {service_request.status}. Must be {valid_payment_statuses}'
        }), 400
    
    # Validate payment details
    payment_data = request.get_json()
    
    try:
        # Use the service's base price for payment
        payment_amount = service_request.service.base_price
        
        # Update booking status to paid
        service_request.status = 'Paid'
        
        # Create a payment record
        new_payment = Payment(
            service_request_id=service_request.id,
            amount=payment_amount,
            payment_date=datetime.utcnow(),
            payment_method=payment_data.get('payment_method', 'Unknown')
        )
        db.session.add(new_payment)
        
        # Commit changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Payment processed successfully',
            'status': service_request.status,
            'amount': payment_amount
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': f'Payment processing failed: {str(e)}'
        }), 500



@app.route('/api/professional/earnings', methods=['GET'])
@jwt_required()
def get_professional_earnings():
    """
    Get comprehensive earnings details for a professional
    Supports filtering by date range and provides detailed earnings breakdown
    """
    # Get current user ID from JWT token
    current_user_id = get_jwt_identity()
    
    # Get professional details
    professional = Professional.query.filter_by(user_id=current_user_id).first()
    if not professional:
        return jsonify({'error': 'Professional profile not found'}), 404
    
    # Get query parameters for filtering
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    # Base query for completed service requests with payments
    query = db.session.query(
        ServiceRequest, 
        Payment, 
        Services
    ).join(
        Payment, ServiceRequest.id == Payment.service_request_id
    ).join(
        Services, ServiceRequest.service_id == Services.id
    ).filter(
        ServiceRequest.professional_id == professional.id,
        Payment.payment_status == 'pending'
    )
    
    # Apply date range filter if provided
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            query = query.filter(
                Payment.payment_date.between(start_date, end_date)
            )
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Execute the query
    earnings_data = query.all()
    
    # Prepare detailed earnings breakdown
    earnings_breakdown = []
    total_earnings = 0
    service_earnings = {}
    
    for service_request, payment, service in earnings_data:
        earning_item = {
            'request_id': service_request.id,
            'service_name': service.service_name,
            'amount': payment.amount,
            'payment_date': payment.payment_date.isoformat(),
            'payment_method': payment.payment_method
        }
        earnings_breakdown.append(earning_item)
        
        # Calculate total earnings
        total_earnings += payment.amount
        
        # Calculate earnings by service
        if service.service_name not in service_earnings:
            service_earnings[service.service_name] = 0
        service_earnings[service.service_name] += payment.amount
    
    # Prepare summary statistics
    summary = {
        'total_earnings': round(total_earnings, 2),
        'total_completed_requests': len(earnings_breakdown),
        'earnings_by_service': {
            service: round(amount, 2) 
            for service, amount in service_earnings.items()
        },
        'average_earnings_per_request': round(
            total_earnings / len(earnings_breakdown) if earnings_breakdown else 0, 2
        )
    }
    
    # Additional time-based earnings analysis
    earnings_by_month = {}
    for item in earnings_breakdown:
        month_key = datetime.fromisoformat(item['payment_date']).strftime('%Y-%m')
        if month_key not in earnings_by_month:
            earnings_by_month[month_key] = 0
        earnings_by_month[month_key] += item['amount']
    
    return jsonify({
        'success': True,
        'earnings_breakdown': earnings_breakdown,
        'summary': summary,
        'earnings_by_month': {
            month: round(amount, 2) 
            for month, amount in earnings_by_month.items()
        }
    }), 200




@app.route('/api/service-requests/<int:service_request_id>/review', methods=['POST'])
@jwt_required()
def create_service_review(service_request_id):
    """
    Create a review for a completed service request
    """
    current_user_id = get_jwt_identity()
    
    # Validate incoming review data
    data = request.get_json()
    rating = data.get('rating')
    review_text = data.get('review_text')
    
    # Validate inputs
    if not rating or not review_text:
        return jsonify({
            'error': 'Rating and review text are required'
        }), 400
    
    # Validate rating range
    if rating < 1 or rating > 5:
        return jsonify({
            'error': 'Rating must be between 1 and 5'
        }), 400
    
    try:
        # Find the customer associated with the current user
        customer = Customer.query.filter_by(user_id=current_user_id).first()
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Find the service request
        service_request = ServiceRequest.query.get(service_request_id)
        if not service_request:
            return jsonify({'error': 'Service request not found'}), 404
        
        # Ensure the service request belongs to the current customer
        if service_request.customer_id != customer.id:
            return jsonify({'error': 'Unauthorized to review this service request'}), 403
        
        # Ensure service request is completed before allowing review
        if service_request.status != 'Paid':
            return jsonify({'error': 'Can only review completed service requests'}), 400
        
        # Check if review already exists for this service request
        existing_review = ServiceReview.query.filter_by(
            customer_id=customer.id, 
            service_id=service_request.service_id,
            professional_id=service_request.professional_id
        ).first()
        
        if existing_review:
            return jsonify({'error': 'You have already reviewed this service'}), 400
        
        # Create new service review
        new_review = ServiceReview(
            customer_id=customer.id,
            service_id=service_request.service_id,
            professional_id=service_request.professional_id,
            review_text=review_text,
            rating=rating
        )
        
        db.session.add(new_review)
        db.session.commit()
        
        return jsonify({
            'message': 'Review submitted successfully',
            'review': {
                'id': new_review.id,
                'rating': new_review.rating,
                'review_text': new_review.review_text,
                'service_name': service_request.service_name,
                'professional_name': service_request.professional.fullname
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'An error occurred while submitting the review',
            'details': str(e)
        }), 500

@app.route('/api/professional/<int:professional_id>/reviews', methods=['GET'])
def get_professional_reviews(professional_id):
    """
    Retrieve reviews for a specific professional
    """
    try:
        # Paginate reviews
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Query reviews with pagination
        reviews_query = ServiceReview.query.filter_by(professional_id=professional_id)
        pagination = reviews_query.paginate(page=page, per_page=per_page, error_out=False)
        
        review_list = [{
            'id': review.id,
            'customer_name': review.customer.fullname,  # Use customer's fullname
            'service_name': review.service.service_name,  # Use service_name from Services model
            'rating': review.rating,
            'review_text': review.review_text,
            'review_date': review.review_date.isoformat() if review.review_date else None
        } for review in pagination.items]
        
        return jsonify({
            'reviews': review_list,
            'total_reviews': pagination.total,
            'total_pages': pagination.pages,
            'current_page': page,
            'average_rating': reviews_query.with_entities(
                func.avg(ServiceReview.rating)
            ).scalar() or 0
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve reviews',
            'details': str(e)
        }), 500



@app.route('/api/user/<int:user_id>/professional', methods=['GET'])
def get_professional_by_user_id(user_id):
    """
    Retrieve professional ID for a given user ID
    """
    try:
        # Find the professional associated with the user
        professional = Professional.query.filter_by(user_id=user_id).first()
        
        if not professional:
            return jsonify({'error': 'No professional found for this user'}), 404
        
        return jsonify({
            'professional_id': professional.id,
            'fullname': professional.fullname
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve professional information',
            'details': str(e)
        }), 500




from celery.result import AsyncResult

@app.route('/api/export')
def export_csv():
    # Trigger the async task
    task = download_csv.delay()
    return jsonify({
        "id": task.id,
        "result": None,  # Initially None
    })

@app.route('/api/csv_result/<id>')
def csv_result(id):
    # Get the async result
    res = AsyncResult(id)
    
    # Wait for the task to complete (with a timeout)
    try:
        # Wait for the task to complete
        filename = res.get(timeout=30)  # 30-second timeout
        
        # Send the file
        return send_from_directory('static', filename)
    except Exception as e:
        # Handle any errors (timeout, task failure, etc.)
        return jsonify({"error": str(e)}), 500




@app.route('/api/stat', methods=['GET'])
def get_statistics():
    """
    Retrieve statistical data for users, service bookings, and request statuses
    """
    # Get user role counts
    roles_count = db.session.query(
        User.role,
        func.count(User.id)
    ).group_by(User.role).all()
    
    # Get service booking counts
    service_bookings = db.session.query(
        Services.service_name,
        func.count(ServiceRequest.id)
    ).join(
        ServiceRequest,
        Services.id == ServiceRequest.service_id
    ).group_by(
        Services.service_name
    ).all()
    
    # Get request status counts (open vs completed)
    status_counts = db.session.query(
        ServiceRequest.status,
        func.count(ServiceRequest.id)
    ).group_by(
        ServiceRequest.status
    ).all()
    
    return jsonify({
        'users': {role: count for role, count in roles_count},
        'service_bookings': {name: count for name, count in service_bookings},
        'request_status': {status: count for status, count in status_counts}
    })



@app.route('/api/profile/user/<int:user_id>', methods=['GET','PATCH'])
def get_user_profile(user_id):  # ✅ Correct name (applies to all users)
    user = User.query.get_or_404(user_id)
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "approved": user.approved
    })



@app.route('/api/professional/<int:user_id>', methods=['GET','PATCH'])
def get_professional_profile(user_id):
    professional = Professional.query.filter_by(user_id=user_id).first_or_404()
    return jsonify({
        "id": professional.id,
        "fullname": professional.fullname,
        "experience": professional.experience,
        "contact": professional.contact,
        "address": professional.address,
        "pin_code": professional.pin_code,
        "service_id": professional.service_id
    })

@app.route('/api/customer/<int:user_id>', methods=['GET','PATCH'])
def get_customer_profile(user_id):
    customer = Customer.query.filter_by(user_id=user_id).first_or_404()
    return jsonify({
        "id": customer.id,
        "fullname": customer.fullname,
        "contact": customer.contact,
        "address": customer.address,
        "pin_code": customer.pin_code
    })


from sqlalchemy.orm import joinedload
from sqlalchemy.sql import text

@app.route('/admin/professional/<int:user_id>/reviews', methods=['GET'])
@jwt_required()
def get_admin_professional_reviews(user_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized access'}), 403

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Fetch professional using user_id
        professional = Professional.query.filter_by(user_id=user_id).first()
        if not professional:
            return jsonify({'error': 'Professional not found'}), 404

        print(f"DEBUG: Found professional -> ID: {professional.id}, User ID: {user_id}")

        # Fetch reviews using correct professional_id
        reviews_query = ServiceReview.query.filter(ServiceReview.professional_id == professional.id)

        print(f"DEBUG: SQL Query -> {str(reviews_query.statement.compile(db.engine, compile_kwargs={'literal_binds': True}))}")

        pagination = reviews_query.order_by(ServiceReview.review_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        review_list = [{
            'rating': review.rating,
            'review_text': review.review_text,
            'review_date': review.review_date.isoformat() if review.review_date else None
        } for review in pagination.items]

        # Calculate average rating for this professional
        average_rating = db.session.query(func.avg(ServiceReview.rating)).filter(
            ServiceReview.professional_id == professional.id
        ).scalar() or 0

        return jsonify({
            'professional_details': {
                'id': professional.id,
                'fullname': professional.fullname
            },
            'reviews': review_list,
            'total_reviews': pagination.total,
            'total_pages': max(pagination.pages, 1),
            'current_page': page,
            'average_rating': round(average_rating, 1),
            'low_rating_threshold': 2
        }), 200

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve reviews',
            'details': str(e)

        }), 500




@app.route('/recommendations', methods=['GET'])
@jwt_required()  # Use Flask-JWT-Extended decorator
def get_recommendations():
    user_id = get_jwt_identity()  # Get user ID from JWT token

    customer = Customer.query.filter_by(user_id=user_id).first()
    if not customer:
        return jsonify({'error': 'Customer profile not found'}), 404

    pin_code = customer.pin_code

    professionals = Professional.query.join(Services).filter(Professional.pin_code == pin_code).all()

    data = []
    for pro in professionals:
        data.append({
            'professional_name': pro.fullname,
            'service_name': pro.service.service_name,
            'service_id': pro.service.id,
            'price': pro.service.base_price,
            'experience': pro.experience,
            'contact': pro.contact,
            'location': pro.address,
        })

    return jsonify({'recommendations': data})



if __name__ == "__main__":
    app.run(debug=True)