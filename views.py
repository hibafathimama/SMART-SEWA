from Demos.win32ts_logoff_disconnected import username
from django.http import JsonResponse
from django.shortcuts import render
from flask import redirect
from django.contrib.auth import authenticate,login

import os
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
from django.contrib import messages

from datetime import datetime

from numpy.core.defchararray import title

from myapp.models import *
# Create your views here.

from django.shortcuts import render


def admin_dashboard(request):
    # Fetching counts for the stat cards
    staff_count = staff_table.objects.count()
    services_count = service_table.objects.count()
    pending_complaints = Complaint_table.objects.filter(status='Pending').count()
    active_rules = rules_table.objects.filter(is_active=True).count()

    # Fetching the list of staff for the table
    all_staff = Staff.objects.all()

    context = {
        'staff_count': staff_count,
        'services_count': services_count,
        'pending_complaints': pending_complaints,
        'active_rules': active_rules,
        'all_staff': all_staff,
    }

    return render(request, 'your_template_name.html', context)

def login_get(request):
    return render(request,'Login.html')

def login_post(request):
    username=request.POST['uname']
    password=request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        if user.groups.filter(name="Admin").exists():
            login(request, user)
            return redirect('/myapp/homeget/')
        elif user.groups.filter(name="Staff").exists():
            login(request, user)
            return redirect('/myapp/staffhome/')
    else:
        messages.warning(request, "Invalid username or password")
        return redirect('/myapp/loginget/')


    return render(request, "Login.html")



def home_get(request):
    return render(request,'admin/Base.html')


def admin_add_dataset(request):
    return render(request,"admin/AddDataset.html")

def admin_add_dataset_post(request):
    question=request.POST['qstn']
    answer=request.POST['ans']
    a=dataset_table()
    a.question=question
    a.answer=answer
    a.save()
    return redirect('/myapp/admin_view_dataset/')


from django.shortcuts import render, redirect
from .models import service_table, service_document_table


def admin_add_document(request, id):
    service_data = service_table.objects.get(id=id)
    return render(request, "admin/AddDocument.html", {"service": service_data})


def admin_add_document_post(request,id):
    if request.method == 'POST':
        # Use request.FILES for the document
        doc_file = request.FILES.get('doc')
        det_text = request.POST.get('det')

        # Create and Save the record
        obj = service_document_table()
        obj.SERVICE = service_table.objects.get(id=id)
        obj.document = doc_file
        obj.details = det_text
        obj.save()

        return redirect('/myapp/admin_view_service/')

def admin_add_rules(request):
    return render(request,"admin/AddRules.html")
def admin_add_rules_post(request):
    rules = request.POST['rules']
    details = request.POST['det']
    a=rules_table()
    a.rules=rules
    a.details=details
    a.date=datetime.now().today()
    a.save()
    return redirect('/myapp/homeget/')


def admin_add_service(request):
    return render(request,"admin/AddService.html")
def admin_add_service_post(request):
    name = request.POST['name']
    details = request.POST['det']
    cost = request.POST['cost']
    estimated_time = request.POST['time']
    a=service_table()
    a.service=name
    a.details=details
    a.cost=cost
    a.date=datetime.now().today()
    a.time=estimated_time
    a.save()
    return redirect('/myapp/homeget/')


def admin_add_staff(request):
    return render(request,"admin/AddStaff.html")
def admin_add_staff_post(request):
    name=request.POST['name']
    gender=request.POST['gender']
    dob=request.POST['dob']
    phone=request.POST['phno']
    email=request.POST['email']
    photo=request.FILES['photo']
    username=request.POST['username']
    password=request.POST['password']

    user = User.objects.create_user(username=username, password=password)
    user.save()
    user.groups.add(Group.objects.get(name="Staff"))

    a=staff_table()
    a.name=name
    a.gender=gender
    a.dob=dob
    a.phoneno=phone
    a.email=email
    a.photo=photo
    a.LOGIN=user
    a.save()
    return redirect('/myapp/homeget/')




def admin_send_reply(request, id):
    return render(request, 'send reply.html', {"id": id})


def admin_send_reply_post(request):
    if request.method == 'POST':
        reply = request.POST['reply']
        complaint_id = request.POST['id']

        # Update the record
        Complaint_table.objects.filter(id=complaint_id).update(
            reply=reply,
            status='replied' # Matches the template check
        )
        return redirect('/myapp/admin_view_complaint/')

def admin_view_complaint(request):
    a=Complaint_table.objects.all()
    return render(request,"admin/ViewComplaint.html",{"data":a})

def admin_view_dataset(request):
    a=dataset_table.objects.all()
    return render(request,"admin/ViewDataset.html",{"data":a})
def admin_view_document(request, id):
    # Get the specific service
    service = service_table.objects.get(id=id)
    # Get all documents belonging to this service
    docs = service_document_table.objects.filter(SERVICE=service)
    return render(request, "admin/ViewDocuments.html", {"data": docs, "service": service})
def admin_view_rating(request):
    a=feedback_table.objects.all()
    return render(request,"admin/ViewRating.html",{"data":a})

def admin_view_rules(request):
    a=rules_table.objects.all()
    return render(request,"admin/ViewRules.html",{"data":a})

def admin_view_service(request):
    a=service_table.objects.all()
    return render(request,"admin/ViewService.html",{"data":a})

def admin_view_staff(request):
    a=staff_table.objects.all()
    return render(request,"admin/ViewStaff.html",{"data":a})

from django.shortcuts import render
from datetime import datetime
from .models import staff_timing, staff_table


def admin_view_staff_performance(request, id):
    performance_data = staff_timing.objects.filter(STAFF__id=id).select_related('BOOKING', 'STAFF')

    chart_labels = []
    chart_durations = []
    booking_ids = []
    total_minutes = 0
    valid_sessions = 0

    for entry in performance_data:
        duration_minutes = None
        try:
            fmt = "%H:%M:%S"
            start = datetime.strptime(entry.start_time.strip(), fmt)
            end = datetime.strptime(entry.end_time.strip(), fmt)
            diff = end - start
            duration_minutes = round(diff.total_seconds() / 60, 2)
            total_minutes += duration_minutes
            valid_sessions += 1
        except Exception:
            duration_minutes = 0

        booking_label = f"Booking #{entry.BOOKING.id}"
        chart_labels.append(booking_label)
        chart_durations.append(duration_minutes)
        booking_ids.append(entry.BOOKING.id)

    # Get staff info
    try:
        staff = staff_table.objects.get(id=id)
        staff_name = getattr(staff, 'name', f'Staff #{id}')
    except staff_table.DoesNotExist:
        staff_name = f'Staff #{id}'

    total_hours = round(total_minutes / 60, 2)
    avg_minutes = round(total_minutes / valid_sessions, 2) if valid_sessions > 0 else 0

    context = {
        "data": performance_data,
        "chart_labels": chart_labels,
        "chart_durations": chart_durations,
        "staff_name": staff_name,
        "staff_id": id,
        "total_bookings": len(performance_data),
        "total_hours": total_hours,
        "avg_minutes": avg_minutes,
    }

    return render(request, 'admin/staff perfomance.html', context)
def admin_edit_staff(request,id):
    a=staff_table.objects.get(id=id)
    return render(request,"admin/EditStaff.html",{"data":a})

def admin_edit_staff_post(request):
    name = request.POST['Name']
    gender = request.POST['gender']
    dob = request.POST['dob']
    phone = request.POST['number']
    email = request.POST['email']
    id = request.POST['id']

    a = staff_table.objects.get(id=id)
    a.name = name
    a.gender = gender
    a.dob = dob
    a.phone = phone
    a.email = email

    if 'photo' in request.FILES:
        a.photo = request.FILES['photo']
    a.save()
    return redirect('/myapp/admin_view_staff/')





def admin_edit_services(request,id):
    a=service_table.objects.get(id=id)
    request.session["service_id"] = id
    return render(request,"admin/EditServices.html",{"data":a})

def admin_edit_services_post(request):
    name=request.POST['name']
    details=request.POST['details']
    cost=request.POST['cost']
    time=request.POST['time']
    a=service_table.objects.get(id=request.session['service_id'])
    a.service=name
    a.details=details
    a.cost=cost
    a.time=time
    a.save()
    return redirect('/myapp/admin_view_service/')



def admin_edit_document(request,id):
    request.session["document_id"] = id
    a.service_table.objects.get(id=id)
    return render(request,"admin/EditDocument.html",{"data":a})
def admin_edit_document_post(request):
    document=request.POST['document']
    details=request.POST['details']
    a=service_document_table.objects.get(id=request.session['document_id'])
    a.document=document
    a.details=details
    a.save()
    return redirect('/myapp/admin_view_document/')

def admin_edit_dataset(request, id):
    request.session["dataset_id"] = id
    a = dataset_table.objects.get(id=id)
    return render(request, "admin/EditDataset.html", {
        "data": a,
    })


def admin_edit_dataset_post(request):


    question = request.POST['qstn']
    answer = request.POST['ans']

    a = dataset_table.objects.get(id=request.session['dataset_id'])
    a.question = question
    a.answer = answer  # Ensure this matches your model field name
    a.save()
    return redirect('/myapp/admin_view_dataset/')

def admin_delete_dataset(request, id):
    dataset_table.objects.filter(id=id).delete()
    return redirect('/myapp/admin_view_dataset/')


def admin_delete_document(request, id):
    # 1. Fetch the document record first
    document_record = service_document_table.objects.get(id=id)

    service_id = document_record.SERVICE.id

    document_record.delete()

    return redirect(f'/myapp/admin_view_document/{service_id}')
def admin_delete_staff(request, id):

    a=staff_table.objects.get(id=id)
    a.LOGIN.delete()

    return redirect('/myapp/admin_view_staff/')
def admin_delete_service(request, id):
    service_table.objects.get(id=id).delete()
    return redirect('/myapp/admin_view_service/')
def admin_delete_rules(request, id):
    rules_table.objects.get(id=id).delete()
    return redirect('/myapp/admin_view_rules/')

def admin_edit_rules(request,id):
    request.session["rule_id"] = id
    a=rules_table.objects.get(id=id)
    return render(request,"admin/EditRules.html",{"data":a})
def admin_edit_rules_post(request):
    rules=request.POST['rules']
    details=request.POST['details']
    a=rules_table.objects.get(id=request.session['rule_id'])
    a.rules=rules
    a.details=details
    a.save()
    return redirect('/myapp/admin_view_rules/')

def admin_view_leave(request):
    a=leave_table.objects.all()
    return render(request, "admin/View leave.html",{"data":a})

def admin_approve_leave(request, id):
    a=leave_table.objects.get(id=id)
    a.status="approved"
    a.save()
    return redirect('/myapp/admin_view_leave/')

def admin_reject_leave(request, id):
    a=leave_table.objects.get(id=id)
    a.status="rejected"
    a.save()
    return redirect('/myapp/admin_view_leave/')

###############################Staff##################################

def staffhome(request):
    return render(request, "staff/staffhome.html")
def staff_add_notification(request):
    return render(request,"staff/AddNotification.html")
def staff_add_notification_post(request):
    title=request.POST['title']
    details=request.POST['details']
    a=notification_table()
    a.notification=title
    a.details=details
    a.STAFF=staff_table.objects.get(LOGIN_id=request.user.id)
    a.date=datetime.now()
    a.save()
    return redirect('/myapp/staff_add_notification/')


from django.shortcuts import render
from django.utils import timezone
from .models import booking_details_table, staff_timing, staff_table


def staff_booking_details(request, id):
    request.session["bid"] = id

    b = booking_details_table.objects.filter(BOOKING__id=id)

    staff_id = staff_table.objects.get(LOGIN_id=request.user.id)

    a=staff_timing.objects.filter(BOOKING__id=id)

    if len(a)==0:
        staff_member = staff_id


        c=staff_timing()
        c.BOOKING=booking_table.objects.get(id=id)
        c.STAFF=staff_member
        c.start_time=datetime.now().strftime("%H:%M:%S")
        c.save()

    return render(request, "staff/BookingDetails.html", {"data": b})



def update_service_status(request):
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        status     = request.POST.get('status')           # 'completed' or 'rejected'
        booking_details_table.objects.filter(id=service_id).update(status=status)
        ob=booking_details_table.objects.get(id=service_id)
        obb=booking_details_table.objects.filter(BOOKING__id=ob.BOOKING.id,status="pending")
        if len(obb)==0:
            obb=ob.BOOKING
            obb.status="completed"
            obb.save()

            obj=staff_timing.objects.get(BOOKING__id=obb.id)
            obj.end_time=datetime.now().strftime("%H:%M:%S")
            obj.save()





        return redirect('/myapp/staff_booking_details/'+str(request.session["bid"]))    # adjust to your list URL

def user_documents(request):
    uid = request.session.get('lid')
    documents = document_table.objects.filter(USER__id=uid)
    return render(request, 'staff/upload_doc.html', {'documents': documents})

def user_add_document(request):
    if request.method == 'POST':
        uid = request.session.get('lid')
        user = user_table.objects.get(id=uid)
        document_table.objects.create(
            USER=user,
            document=request.FILES['document'],
            title=request.POST['title'],
            date=datetime.today()
        )
        return redirect('/myapp/user_documents/')
def que_process_table(request,id):

    request.session["bdid"] = id
    ob=booking_details_table.objects.get(id=id)

    request.session["lid"] = ob.BOOKING.USER.id
    return redirect("/myapp/user_documents/")
def user_delete_document(request, doc_id):
    uid = request.session.get('lid')
    document_table.objects.filter(id=doc_id, USER__id=uid).delete()
    return redirect('/myapp/user_documents/')

def staff_view_booking(request):
    a=booking_table.objects.filter(status="pending")
    return render(request,"staff/ViewBooking.html",{"data":a})

def staff_view_document(request,id):
    a=service_document_table.objects.filter(SERVICE__id=id)
    return render(request,"staff/ViewDocument.html",{"data":a})

def staff_view_notification(request):
    a=notification_table.objects.get(STAFF__LOGIN_id=request.user.id)
    return render(request,"staff/ViewNotification.html",{"data":a})

def staff_view_services(request):
    a=service_table.objects.all()
    return render(request,"staff/ViewServices.html",{"data":a})

def view_profile(request):
    a=staff_table.objects.get(LOGIN_id=request.user.id)
    return render(request,"staff/view profile.html",{"data":a})


def add_leave(request):
    return render(request,"staff/Addleave.html")
def add_leave_post(request):
    reason=request.POST['reason']
    applydate=request.POST['applydate']
    fromdate=request.POST['fromdate']
    todate=request.POST['todate']
    a=leave_table()
    a.reason=reason
    a.appldate=applydate
    a.fromdate=fromdate
    a.todate=todate
    a.status="pending"
    a.STAFF=staff_table.objects.get(LOGIN_id=request.user.id)
    a.save()
    return redirect('/myapp/staff_view_leave/')

def staff_view_leave(request):
    a=staff_table.objects.get(LOGIN_id=request.user.id)
    return render(request,"staff/View leave.html",{"data":a})
def edit_leave(request,id):
    request.session["LEAVE_ID"] = id
    a=leave_table.objects.get(id=id)
    return render(request,"staff/Editleave.html",{"data":a})

def edit_leave_post(request):
    reason=request.POST['reason']
    applydate=request.POST['applydate']
    fromdate=request.POST['fromdate']
    todate=request.POST['todate']
    a=leave_table.objects.get(id=request.session['LEAVE_ID'])
    a.reason=reason
    a.applydate=applydate
    a.fromdate=fromdate
    a.todate=todate
    a.save()
    return redirect('/myapp/staff_view_leave/')

def delete_leave(request,id):
    a=leave_table.objects.get(id=id)
    a.delete()
    return redirect('/myapp/staff_view_leave/')


from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from .models import user_table
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def user_registration(request):
    if request.method == 'POST':
        try:
            # 1. Data Extraction
            name = request.POST.get('name')
            gender = request.POST.get('gender')
            dob = request.POST.get('dob')
            phoneno = request.POST.get('phoneno')
            email = request.POST.get('email')
            place = request.POST.get('place')
            post = request.POST.get('post')
            pin = request.POST.get('pin')
            username = request.POST.get('username')
            password = request.POST.get('password')
            photo = request.FILES.get('photo')

            # 2. Check if Username already exists (Auth Table)
            if User.objects.filter(username=username).exists():
                return JsonResponse({"status": "exists", "msg": "Username already taken"})

            # 3. Check if Email already exists (User Table)
            if user_table.objects.filter(email=email).exists():
                return JsonResponse({"status": "exists", "msg": "Email already registered"})

            # 4. Check if Phone Number already exists (User Table)
            if user_table.objects.filter(phoneno=phoneno).exists():
                return JsonResponse({"status": "exists", "msg": "Phone number already registered"})

            # 5. Create Authentication User if all checks pass
            user = User.objects.create_user(username=username, password=password)
            group, created = Group.objects.get_or_create(name="User")
            user.groups.add(group)
            user.save()

            # 6. Save Profile Data
            obj = user_table()
            obj.name = name
            obj.gender = gender
            obj.dob = dob
            obj.phoneno = phoneno
            obj.email = email
            obj.photo = photo
            obj.place = place
            obj.post = post
            obj.pin = pin
            obj.LOGIN = user
            obj.save()

            return JsonResponse({"status": "ok"})

        except Exception as e:
            return JsonResponse({"status": "error", "msg": str(e)})

    return JsonResponse({"status": "invalid_method"})

def and_login(request):
    username = request.POST['username']
    password = request.POST.get('password')
    if not username or not password:
        return JsonResponse({"status": "no"})
    user = authenticate(request, username=username, password=password)
    if user is not None:

        if user.groups.filter(name="User"):
            wid = user_table.objects.get(LOGIN=user.id).id
            return JsonResponse({"status": "ok", "lid": user.id, "type": "User"})
        else:
            return JsonResponse({"status": "no"})


def view_profile_user(request):
    lid=request.POST['lid']
    a=user_table.objects.get(LOGIN_id=lid)
    return JsonResponse({"status":"ok",
                         "name":a.name,
                         "gender":a.gender,
                         "dob":a.dob,
                         "phoneno":str(a.phoneno),
                         "email":a.email,
                         "place":a.place,
                         "photo":str(a.photo.url),
                         "post":a.post,
                         "pin":a.pin
                         })

def edit_profile(request):
    name = request.POST['name']
    gender = request.POST['gender']
    dob = request.POST['dob']
    phoneno = request.POST['phoneno']
    email = request.POST['email']
    photo = request.FILES['photo']
    place = request.POST['place']
    post = request.POST['post']
    pin = request.POST['pin']
    lid=request.POST['lid']
    a=user_table.objects.get(LOGIN_id=lid)
    a.name=name
    a.gender=gender
    a.dob=dob
    a.phoneno=phoneno
    a.email=email
    a.photo=photo
    a.place=place
    a.post=post
    a.pin=pin
    a.save()
    return JsonResponse({"status":"ok"})

def user_view_services(request):
    a=service_table.objects.all()
    l=[]
    for i in a:
        ob=service_document_table.objects.filter(SERVICE__id=i.id)
        service_doc=[]
        for j in ob:
            service_doc.append({"details":j.details})
        l.append({"id":i.id,
                  "service":i.service,
                  "details":i.details,
                  "date":i.date,
                  "cost":i.cost,
                  "time":i.time,
                  "service_doc":service_doc
                  })
    return JsonResponse({"status":"ok","data":l})
def user_view_notification(request):
    a=notification_table.objects.all()
    l=[]
    for i in a:
        l.append({"id":i.id,
                  "notification":i.notification,
                  "details":i.details,
                  "date":i.date
                  })
    return JsonResponse({"status": "ok", "data": l})

def user_send_complaint(request):
    complaint=request.POST['complaint']
    lid=request.POST['lid']
    a=Complaint_table()
    a.complaint=complaint
    a.USER=user_table.objects.get(LOGIN_id=lid)
    a.reply='pending'
    a.status='pending'
    a.date=datetime.now().today()
    a.save()
    return JsonResponse({"status":"ok"})
def user_send_rating(request):
    lid=request.POST['lid']
    rating=request.POST['rating']
    feedback=request.POST['feedback']
    staff_id=request.POST['staff_id']
    a=feedback_table()
    a.feedback=feedback
    a.rating=rating
    a.USER=user_table.objects.get(LOGIN_id=lid)
    a.STAFF_id=staff_id
    a.date=datetime.now().today()
    a.save()
    return JsonResponse({"status":"ok"})

def user_view_feedback(request):
    lid = request.POST['lid']
    sid = request.POST['sid']
    # Changed .get() to .filter()
    a = feedback_table.objects.filter(STAFF__id=sid).order_by('-date')
    l = []
    for i in a:
        l.append({
            "id": i.id,
            "feedback": i.feedback,
            "rating": i.rating,
            "date": i.date.strftime("%Y-%m-%d")
        })
    return JsonResponse({"status": "ok", "data": l})
def user_view_reply(request):
    lid = request.POST['lid']
    # Use .filter() instead of .get()
    a = Complaint_table.objects.filter(USER__LOGIN_id=lid)
    l = []
    for i in a:
        l.append({"id": i.id, "complaint": i.complaint, "reply": i.reply, "date": i.date.strftime("%Y-%m-%d") })
    return JsonResponse({"status": "ok", "data": l})

import json
import google.generativeai as genai
from django.views.decorators.csrf import csrf_exempt

# Configure Google Gemini API
GOOGLE_API_KEY = 'AIzaSyArUYYh7JuHdgw7rH_WnqsbR1_T9mWYsUQ'  # Replace with your actual API key
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini Model
model = genai.GenerativeModel('gemini-2.5-flash')

#
# @csrf_exempt
# def chatbot_response(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body.decode('utf-8'))
#
#             user_message = data.get('message', '').strip()
#             lid = data.get('lid')
#
#             if not user_message:
#                 return JsonResponse({'response': 'Please enter a valid question.'})
#
#             if not lid:
#                 return JsonResponse({'response': 'User ID missing in request'}, status=400)
#
#             usertable = user_table.objects.get(LOGIN_id=lid)
#
#             # AI response
#             bot_response = model.generate_content(user_message).text.strip()
#
#             # Save to DB
#             Chatbot.objects.create(
#                 USER=usertable,
#                 date=datetime.now().today(),
#                 question=user_message,
#                 answer=bot_response
#             )
#
#             return JsonResponse({'response': bot_response})
#
#         except user_table.DoesNotExist:
#             return JsonResponse({'response': 'User not found'}, status=404)
#
#         except Exception as e:
#             print(e)
#             return JsonResponse({'response': str(e)}, status=500)
#
#     return JsonResponse({'response': 'Invalid method'}, status=405)
import json
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .models import user_table, Chatbot, dataset_table


# ── Build similarity index from DB ──────────────────────────────
def get_best_answer(user_message):
    """
    Fetch all Q&A pairs, vectorize them with TF-IDF,
    compute cosine similarity against the user message,
    return the best matching answer (or a fallback).
    """
    dataset = dataset_table.objects.all().values('question', 'answer')

    if not dataset:
        return "No dataset available to answer your question."

    questions = [row['question'] for row in dataset]
    answers = [row['answer'] for row in dataset]

    # TF-IDF vectorize: fit on all questions + user message together
    corpus = questions + [user_message]

    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',  # ignore common words
            ngram_range=(1, 2),  # unigrams + bigrams for better matching
            min_df=1
        )
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        return "I couldn't process your question. Please try rephrasing."

    # Last row is user message vector, rest are questions
    question_vectors = tfidf_matrix[:-1]
    user_vector = tfidf_matrix[-1]

    # Cosine similarity between user message and each question
    similarities = cosine_similarity(user_vector, question_vectors).flatten()

    best_index = int(np.argmax(similarities))
    best_score = float(similarities[best_index])

    # Threshold: reject if similarity is too low (no meaningful match)
    THRESHOLD = 0.2
    if best_score < THRESHOLD:
        return "I'm sorry, I don't have an answer for that. Please try asking differently."

    return answers[best_index]


# ── View ─────────────────────────────────────────────────────────
@csrf_exempt
def chatbot_response(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))

            user_message = data.get('message', '').strip()
            lid = data.get('lid')

            if not user_message:
                return JsonResponse({'response': 'Please enter a valid question.'})

            if not lid:
                return JsonResponse({'response': 'User ID missing in request'}, status=400)

            usertable = user_table.objects.get(LOGIN_id=lid)

            # ── Similarity match ──────────────────────────────
            bot_response = get_best_answer(user_message)

            # ── Save to DB ────────────────────────────────────
            Chatbot.objects.create(
                USER=usertable,
                date=datetime.now().today(),
                question=user_message,
                answer=bot_response
            )

            return JsonResponse({'response': bot_response})

        except user_table.DoesNotExist:
            return JsonResponse({'response': 'User not found'}, status=404)

        except Exception as e:
            print(e)
            return JsonResponse({'response': str(e)}, status=500)

    return JsonResponse({'response': 'Invalid method'}, status=405)

@csrf_exempt
def chat_history(request):
    try:
        lid = request.GET.get('lid')

        if not lid:
            return JsonResponse({'response': 'User ID missing'}, status=400)

        usertable = user_table.objects.get(LOGIN_id=lid)

        chats = Chatbot.objects.filter(USER=usertable).order_by('id')

        history = [{"question": c.question, "answer": c.answer} for c in chats]

        return JsonResponse(history, safe=False)

    except user_table.DoesNotExist:
        return JsonResponse({'response': 'User not found'}, status=404)






@csrf_exempt
def user_book_multiple_services(request):
    if request.method == 'POST':
        try:
            lid = request.POST.get('lid')
            # Flutter sends a list of IDs as a JSON string or comma-separated values
            service_ids_raw = request.POST.get('service_ids')
            service_ids = json.loads(service_ids_raw)  # Expecting [1, 4, 7]

            user_profile = user_table.objects.get(LOGIN_id=lid)

            # Calculate total amount
            total_amount = 0
            services_to_add = []
            for s_id in service_ids:
                service = service_table.objects.get(id=s_id)
                total_amount += int(service.cost)
                services_to_add.append(service)

            # 1. Create Main Booking
            main_booking = booking_table.objects.create(
                USER=user_profile,
                status='pending',
                date=datetime.now().date(),
                amount=total_amount
            )

            # 2. Create Booking Details for each service
            for service in services_to_add:
                booking_details_table.objects.create(
                    BOOKING=main_booking,
                    SERVICE=service,
                    status='pending'
                )

            return JsonResponse({"status": "ok", "msg": "Booking confirmed for multiple services"})

        except Exception as e:
            return JsonResponse({"status": "error", "msg": str(e)})

    return JsonResponse({"status": "invalid_method"})




@csrf_exempt
def user_view_bookings(request):
    if request.method == 'POST':
        try:
            lid = request.POST.get('lid')
            user_profile = user_table.objects.get(LOGIN_id=lid)

            # Fetch all bookings for this user, newest first
            bookings = booking_table.objects.filter(USER=user_profile).order_by('-date')

            results = []
            for b in bookings:
                # Find the specific services linked to this booking
                details = booking_details_table.objects.filter(BOOKING=b)
                service_list = []
                for d in details:
                    service_list.append({
                        "service_name": d.SERVICE.service,
                        "item_status": d.status
                    })

                results.append({
                    "booking_id": b.id,
                    "date": b.date.strftime("%Y-%m-%d"),
                    "total_amount": b.amount,
                    "overall_status": b.status,
                    "services": service_list
                })

            return JsonResponse({"status": "ok", "data": results})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "invalid_method"})


from django.db.models import Avg
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import staff_table, feedback_table


@csrf_exempt
def user_view_staff(request):
    try:
        # Fetch all staff records
        staff_members = staff_table.objects.all()

        data_list = []
        for staff in staff_members:
            # Calculate average rating from feedback_table for this staff
            # Based on your models: feedback_table has a foreign key 'STAFF'
            rating_stats = feedback_table.objects.filter(STAFF=staff).aggregate(Avg('rating'))
            avg_rating = rating_stats['rating__avg']

            # Format to 1 decimal place (e.g., 4.5), default to 0.0 if no ratings
            formatted_rating = round(avg_rating, 1) if avg_rating is not None else 0.0

            data_list.append({
                "id": staff.id,
                "name": staff.name,
                "gender": staff.gender,
                "dob": staff.dob.strftime("%Y-%m-%d"),
                "phone": str(staff.phoneno),
                "email": staff.email,
                "photo": staff.photo.url if staff.photo else "",
                "avg_rating": formatted_rating  # The new badge data
            })

        return JsonResponse({"status": "ok", "data": data_list})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})
#
# @csrf_exempt
# def user_view_staff(request):
#     try:
#         # Fetch all staff records
#         staff_members = staff_table.objects.all()
#
#         data_list = []
#         for staff in staff_members:
#             data_list.append({
#                 "id": staff.id,
#                 "name": staff.name,
#                 "gender": staff.gender,
#                 "dob": staff.dob.strftime("%Y-%m-%d"),
#                 "phone": str(staff.phoneno),
#                 "email": staff.email,
#                 "photo": staff.photo.url if staff.photo else ""
#             })
#
#         return JsonResponse({"status": "ok", "data": data_list})
#
#     except Exception as e:
#         return JsonResponse({"status": "error", "message": str(e)})





import math
from datetime import date

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg

from .models import booking_table, booking_details_table, service_table, staff_table


# ══════════════════════════════════════════════════════════
#  M/M/c Queue Engine  (Erlang-C formula)
# ══════════════════════════════════════════════════════════

def erlang_c(lam: float, mu: float, c: int) -> float:
    """
    Probability that an arriving customer must wait — C(c, rho).
      lam : arrival rate  (bookings / minute)
      mu  : service rate per server  (bookings / minute)
      c   : number of servers (staff)
    Returns 1.0 when system is unstable (rho >= 1).
    """
    if c <= 0 or mu <= 0:
        return 1.0

    rho = lam / (c * mu)
    if rho >= 1.0:
        return 1.0              # unstable — infinite wait

    a = lam / mu                # offered load in Erlangs

    # Erlang-C numerator:  (a^c / c!) × c / (c − a)
    numerator = (a ** c / math.factorial(c)) * (c / (c - a))

    # Σ_{k=0}^{c-1}  a^k / k!
    sum_terms = sum((a ** k) / math.factorial(k) for k in range(c))

    denominator = sum_terms + numerator
    if denominator == 0:
        return 1.0

    return numerator / denominator


def mmc_average_wait(lam: float, mu: float, c: int) -> float:
    """
    Average waiting time IN THE QUEUE  Wq  (minutes).
    Wq = C(c, a) / (c·μ − λ)
    Returns float('inf') when queue is unstable.
    """
    if c <= 0 or mu <= 0 or lam <= 0:
        return 0.0

    rho = lam / (c * mu)
    if rho >= 1.0:
        return float('inf')

    prob_wait = erlang_c(lam, mu, c)
    return prob_wait / (c * mu - lam)


def fmt_wait(minutes: float) -> str:
    if minutes == float('inf'):
        return "Very long (system at capacity)"
    if minutes < 1:
        return "< 1 min"
    h = int(minutes // 60)
    m = int(minutes % 60)
    if h > 0:
        return f"~{h}h {m}min"
    return f"~{m} min"


# ══════════════════════════════════════════════════════════
#  Helper — derive M/M/c inputs from the database
# ══════════════════════════════════════════════════════════

def get_queue_inputs(today: date, user_id: int):
    """
    Returns:
      lam                  – arrival rate (bookings/min)
      mu                   – service rate per server (bookings/min)
      c                    – number of active servers today (staff count)
      user_position        – how many bookings are ahead of this user
      user_service_minutes – total service time for this user's services
      avg_service_minutes  – system-wide average service time
      total_pending        – total pending bookings today
    """
    OPERATING_WINDOW_MINUTES = 8 * 60   # assume 8-hour working day

    # All pending / confirmed bookings today
    pending_bookings = booking_table.objects.filter(
        date=today,
        status__in=['pending', 'confirmed']
    )
    total_pending = pending_bookings.count()

    # λ — arrival rate (bookings per minute)
    lam = total_pending / OPERATING_WINDOW_MINUTES if OPERATING_WINDOW_MINUTES > 0 else 0.0

    # Average service time in minutes across all booked services today
    detail_service_ids = booking_details_table.objects.filter(
        BOOKING__in=pending_bookings,
        status__in=['pending', 'in_progress']
    ).values_list('SERVICE_id', flat=True)

    avg_result = service_table.objects.filter(
        id__in=detail_service_ids
    ).aggregate(avg=Avg('time'))

    avg_service_minutes = float(avg_result['avg']) if avg_result['avg'] else 30.0

    # μ — service rate per server
    mu = 1.0 / avg_service_minutes

    # c — number of servers (staff members)
    c = max(staff_table.objects.count(), 1)

    # User-specific queue position and total service time
    try:
        user_booking = booking_table.objects.filter(
            USER__LOGIN_id=user_id,
            date=today,
            status__in=['pending', 'confirmed']
        ).order_by('id').first()

        if user_booking:
            # Bookings created before this user's booking = users ahead
            user_position = pending_bookings.filter(id__lt=user_booking.id).count()

            # Sum of service times for this user's booked services
            user_svc_times = list(
                booking_details_table.objects.filter(
                    BOOKING=user_booking,
                    status__in=['pending', 'in_progress']
                ).select_related('SERVICE').values_list('SERVICE__time', flat=True)
            )
            user_service_minutes = float(sum(user_svc_times)) if user_svc_times else avg_service_minutes
        else:
            user_position = total_pending
            user_service_minutes = avg_service_minutes

    except Exception:
        user_position = 0
        user_service_minutes = avg_service_minutes

    return lam, mu, c, user_position, user_service_minutes, avg_service_minutes, total_pending


# ══════════════════════════════════════════════════════════
#  View — GET /api/queue-wait-time/?user_id=<id>
# ══════════════════════════════════════════════════════════

@csrf_exempt
def queue_wait_time(request):
    """
    GET /api/queue-wait-time/?user_id=<id>

    Query param:
      user_id  (int)  – the logged-in user's ID (send from Flutter after login)

    Success response:
    {
        "status": "ok",
        "data": {
            "average_system_wait_minutes": 12.5,
            "your_position_in_queue": 3,
            "your_estimated_wait_minutes": 22.0,
            "your_estimated_wait_label": "~22 min",
            "total_pending_today": 15,
            "active_servers": 2,
            "arrival_rate_per_min": 0.03125,
            "service_rate_per_min": 0.03333,
            "server_utilisation_pct": 46.9,
            "queue_stable": true
        }
    }
    """
    if request.method != 'GET':
        return JsonResponse({"status": "error", "message": "Only GET allowed"}, status=405)

    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({"status": "error", "message": "user_id is required"}, status=400)

    try:
        user_id = int(user_id)
    except ValueError:
        return JsonResponse({"status": "error", "message": "user_id must be an integer"}, status=400)

    today = date.today()

    try:
        lam, mu, c, position, user_svc_time, avg_svc_time, total_pending = get_queue_inputs(today, user_id)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

    # System-wide average queue wait  Wq
    Wq = mmc_average_wait(lam, mu, c)
    queue_stable = (Wq != float('inf'))

    # User personalised wait = Wq + (bookings ahead × avg service time per booking)
    if queue_stable:
        user_wait = Wq + (position * avg_svc_time)
    else:
        user_wait = position * avg_svc_time     # fallback when system is at capacity

    utilisation = (lam / (c * mu) * 100) if (c > 0 and mu > 0) else 0.0

    return JsonResponse({
        "status": "ok",
        "data": {
            "average_system_wait_minutes": round(Wq, 2) if queue_stable else None,
            "your_position_in_queue": position,
            "your_estimated_wait_minutes": round(user_wait, 2),
            "your_estimated_wait_label": fmt_wait(user_wait),
            "total_pending_today": total_pending,
            "active_servers": c,
            "arrival_rate_per_min": round(lam, 5),
            "service_rate_per_min": round(mu, 5),
            "server_utilisation_pct": round(utilisation, 1),
            "queue_stable": queue_stable,
        }
    })


def user_view_documents(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            lid = data.get('lid')

            if not lid:
                return JsonResponse({'status': 'error', 'message': 'User ID missing'}, status=400)

            usertable = user_table.objects.get(LOGIN__id=lid)
            documents = document_table.objects.filter(USER=usertable).order_by('-date')

            doc_list = []
            for doc in documents:
                doc_list.append({
                    'id':       doc.id,
                    'title':    doc.title,
                    'date':     str(doc.date),
                    'document': request.build_absolute_uri(doc.document.url),
                })

            return JsonResponse({'status': 'ok', 'data': doc_list})

        except user_table.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


import random
import os
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.models import User


def forgot_password_send_otp(request):
    if request.method == "POST":
        email = request.POST.get('email')
        is_app = request.POST.get('lid')  # Flag to check if request is from Flutter

        try:
            user = User.objects.get(email=email)
            otp = random.randint(100000, 999999)

            request.session['reset_otp'] = otp
            request.session['reset_email'] = email

            subject = 'Smartseva Security Authorization'
            html_content = render_to_string('email.html', {'otp': otp})
            text_content = strip_tags(html_content)

            msg = EmailMultiAlternatives(
                subject,
                text_content,
                settings.EMAIL_HOST_USER,
                [email]
            )
            msg.attach_alternative(html_content, "text/html")

            # Inline Logo logic
            img_path = os.path.join(settings.BASE_DIR, 'static/images/logo.png')
            if os.path.exists(img_path):
                with open(img_path, 'rb') as f:
                    logo_img = MIMEImage(f.read())
                    logo_img.add_header('Content-ID', '<logo_cid>')
                    msg.attach(logo_img)

            msg.send()

            if is_app:
                return JsonResponse({'status': 'ok', 'otp': str(otp)})

            messages.success(request, "OTP sent to your email.")
            return render(request, 'verify_otp.html')

        except User.DoesNotExist:
            if is_app:
                return JsonResponse({'status': 'error', 'msg': 'User not found'})
            messages.error(request, "Identity not found.")

        except Exception as e:
            # This captures the SMTPAuthenticationError or Connection issues
            print(f"Mail Error: {e}")
            if is_app:
                return JsonResponse({'status': 'error', 'msg': 'Email service failed. Check App Password.'})
            messages.error(request, "Connection Error. Check SMTP configuration.")

    return render(request, 'forgot_password_request.html')


def verify_otp_and_reset(request):
    if request.method == "POST":
        entered_otp = request.POST.get('otp')
        new_pass = request.POST.get('new_password')
        is_app = request.POST.get('lid')

        email = request.POST.get('email') if is_app else request.session.get('reset_email')
        saved_otp = request.POST.get('saved_otp') if is_app else request.session.get('reset_otp')

        if str(entered_otp) == str(saved_otp):
            user = User.objects.get(email=email)
            user.set_password(new_pass)
            user.save()

            if is_app:
                return JsonResponse({'status': 'ok'})

            if 'reset_otp' in request.session: del request.session['reset_otp']
            messages.success(request, "Password reset successfully.")
            return redirect('/myapp/loginget/')
        else:
            if is_app: return JsonResponse({'status': 'error', 'msg': 'Invalid OTP'})
            messages.error(request, "Invalid OTP code.")
            return render(request, 'verify_otp.html')
