from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import logout as auth_logout
import numpy as np
import joblib
from .forms import RegisterForm, LoginForm, UpdateUserForm, UpdateProfileForm
from . models import UserPredictModel
from .forms import UserPredictDataForm

import firebase_admin
from firebase_admin import credentials, db
from django.http import JsonResponse

cred = credentials.Certificate("C:/Users/DELL/OneDrive/Desktop/project2/ITPML37-FINAL CODING/Deployment/users/machine-c5407-firebase-adminsdk-fbsvc-5a9d1801f5.json")

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://machine-c5407-default-rtdb.firebaseio.com/'
    })

from django.http import JsonResponse

def fetch_firebase_data(request):
    ref1 = db.reference('/Python/Temp1')
    ref2 = db.reference('/Python/Temp2')
    data = ref1.get()
    data2 = ref2.get()

    if data:
        print('Data from /Python/Temp1:', data)
        try:
            data = float(data)  
        except ValueError:
            return JsonResponse({'error': 'Data in /Python/Hum is not a valid integer'}, status=400)

    if data2:
        print('Data from /Python/Temp2:', data2)
        try:
            data2 = float(data2)
        except ValueError:
            return JsonResponse({'error': 'Data in /Python/Temp is not a valid integer'}, status=400)
    else:
        print('No data found in /Python/Temp')
        data2 = None

    if data and data2 is not None:
        return render(request, 'app/model.html', {'data': data, 'data2': data2})
    else:
        return JsonResponse({'error': 'No data found in one or both references'}, status=404)

def home(request):
    return render(request, 'users/home.html')

@login_required(login_url='users-register')

def index(request):
    return render(request, 'app/index.html')

class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register.html'

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')

            return redirect(to='login')

        return render(request, self.template_name, {'form': form})


# Class based view that extends from the built in login view to add a remember me functionality
class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('users-home')

class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('users-home')

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='users-profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form})

Model = joblib.load('users/Model1.pkl')
def model(request):
    if request.method == 'POST':
        fields =['Air_temperature', 'Process_temperature', 'Rotational_speed', 'Torque', 'Tool_wear']
        
        form = UserPredictDataForm(request.POST)
        features = []
        for i in fields:
            info = float(request.POST[i])
            features.append(info)
           
        Final_features = [np.array(features, dtype=int)]
        
        prediction = Model.predict(Final_features)
        actual_output = prediction[0]
        print(actual_output)

        if actual_output == 0:
            actual_output1 = 'Heat Dissipation Failure'
            
        elif actual_output == 1:
            actual_output1 = 'No Failure'
        
        elif actual_output == 2:
            actual_output1 = 'Overstrain Failure'

        elif actual_output == 3:
            actual_output1 = 'Power Failure'

        elif actual_output == 4:
            actual_output1 = 'Random Failures'

        elif actual_output == 5:
            actual_output1 = 'Tool Wear Failure'
 
        print("output",actual_output1)
        if form.is_valid():
            print('Saving data in Form')
            form_instance = form.save()  # Save form data but don't commit to DB yet
            form_instance.save()
        data = UserPredictModel.objects.latest('id')
        data.Label = actual_output1
        data.save()
        return render(request, 'app/result.html', {'form':form, 'prediction_text':actual_output1})
    else:
        print('Else working')
        form = UserPredictDataForm(request.POST)    
    return render(request, 'app/model.html', {'form':form})

from .models import Profile
def profile_database(request):

    data=Profile.objects.all()
    
    return render(request,'app/profile_list.html',{'database':data})


import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO
from django.shortcuts import render

def Basic_report(request):
    return render(request,'app/Basic_report.html')

def Metrics_report(request):
    return render(request,'app/Metrics_report.html')

def model_db(request):
    data = UserPredictModel.objects.all()
    return render(request, 'app/model_db.html', {'data': data})

from django.shortcuts import render
from django.http import JsonResponse
# import random
# import json
import numpy as np
# from nltk.tokenize import word_tokenize
# from nltk.stem import WordNetLemmatizer
#from .models import Response, models
from Chatbot.processor import chatbot_response
# Remove the comments to download additional nltk packages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
@require_POST
@csrf_exempt
def chatbot_response_view(request):
    if request.method == 'POST':
        the_question = request.POST.get('question', '')

        response = chatbot_response(the_question)
        print(response)

        return JsonResponse({"response": response})
    else:
        
        return JsonResponse({"message": "This endpoint only accepts POST requests."})             
def bott(request):
    return render(request, 'app/bott.html')

def logout_view(request):  
    auth_logout(request)
    return redirect('/')