from django.shortcuts import render,redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib.messages.api import success
from django.http import HttpResponse
from django.contrib import auth, messages
#login
from django.contrib.auth.decorators import login_required
#activation 
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
#cart to user
from carts.models import Cart, CartItem
from carts.views import _cart_id
#dynmic routing
import requests


# Create your views here.accounts
def register(request):
    if request.method=='POST':
        form=RegistrationForm(request.POST)
        if form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            phone_number=form.cleaned_data['phone_number']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            user_name=email.split('@')[0]

            user=Account.objects.create_user(first_name=first_name,email=email,last_name=last_name,username=user_name,password=password)
            user.phone_number=phone_number
            user.save()

            #USer Activation
            current_site=get_current_site(request)
            mail_subject='Please activate your account'
            message=render_to_string('accounts/account_verification_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)), #encoding no one can see that
                'token':default_token_generator.make_token(user),
            })
            to_email=email
            send_email=EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            # messages=success(request,'Thank you for registering with us we have sent you an email, please verify successFull.')
            return redirect('/accounts/login/?command=verification&email='+email)#comes to browser url

    else:
        form=RegistrationForm()
    context={
        'form':form,
    }
    return render(request,'accounts/register.html',context)
def login(request):
    if request.method=="POST":
        email=request.POST['email']
        password=request.POST['password']
        
        user=auth.authenticate(email=email,password=password)

        if user is not None:
            try:
               # print('entering inside try')
                cart=Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists=CartItem.objects.filter(cart=cart).exists()
                #print(is_cart_item_exists)
                if is_cart_item_exists:
                    cart_item=CartItem.objects.filter(cart=cart)

                    product_variation=[]
# getting product variation by cart id
                    for item in cart_item:
                        variation=item.variations.all()
                        product_variation.append(list(variation))

                # Get the cart items from the user to access his product variation
                    cart_item=CartItem.objects.filter(user=user)
                    ex_var_list=[]
                    id=[]
                    for item in cart_item:
                        existing_variation=item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                    
                    # product_variation=[1,2,3,4]
                    # existing_variation=[6,4,2]---  get commomn from both

                    for pr in product_variation:
                        if pr in existing_variation:
                            index=ex_var_list.index(pr)
                            item_id=id[index]
                            item=CartItem.objects.get(id=item_id)
                            item.quantity+=1
                            item.user=user
                            item.save()
                        else:
                            cart_item=CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user=user
                                item.save()

            except:
                #print("except block")
                pass
            auth.login(request,user)
            #messages.success(request,'You are now logged in.')
            url=request.META.get('HTTP_REFERER')
            try:
                query=requests.utils.urlparse(url).query
                params=dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage=params['next']
                    return redirect(nextPage)
                
            except:
                return redirect('home')
        else:
            messages.error(request,'Invalid login credentials')
            redirect('login')
    
    return render(request,'accounts/login.html')

@login_required(login_url=('login'))
def logout(request):
    auth.logout(request)
    messages.success(request,'You are logged out')
    return redirect('login')

def activate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()#decode uidb --give pk of user
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        messages.success(request,'Congratulations!! Your account is activated')
        return redirect('login')
    else:
        messages.success(request,'Invalid registration')
        return redirect('register')

@login_required(login_url=('login'))
def dashboard(request):
    return render(request,'accounts/dashboard.html')

def forgotPassword(request):
    if request.method=='POST':
        email=request.POST['email']
        if Account.objects.filter(email=email).exists():
            user=Account.objects.get(email__exact=email)#email__iexact to case sensitive

    #password Reset
            current_site=get_current_site(request)
            mail_subject='Reset your password'
            message=render_to_string('accounts/reset_password_email.html',{
                        'user':user,
                        'domain':current_site,
                        'uid':urlsafe_base64_encode(force_bytes(user.pk)), #encoding no one can see that
                        'token':default_token_generator.make_token(user),
                    })
            to_email=email
            send_email=EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request,"password reset email has beeen sent to your email address.")
            return redirect('login')

        else:
            messages.error(request,'Account does not exist')  
            return redirect('forgotPassword')  
    return render(request,'accounts/forgotPassword.html')


def resetpassword_validate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()#decode uidb --give pk of user
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid']=uid
        messages.success(request,'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.success(request,'Link expire')
        return redirect('login')

def resetPassword(request):
    if request.method=='POST':
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']

        if password== confirm_password:
            uid=request.session.get('uid')
            user=Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset successful')
            return redirect('login')

        else:
            messages.error(request,'Password not matching')
            return redirect('login')
    else:
        return render(request,'accounts/resetPassword.html')   