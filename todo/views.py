from django.db import IntegrityError
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.forms import User
from django.contrib.auth import login,logout,authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request,'todo/home.html')

def user_signUp(request):
    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            try:
                user=User.objects.create_user(request.POST['username'],password=request.POST['password1'])
                user.save()
                login(request,user)
                return redirect( 'current_todos')
            except IntegrityError:
                return render(request, 'todo/User_SignUp.html',
                              {'form': UserCreationForm, 'error': 'This Username already taken.Please try another username'})

        else:
            return render(request,'todo/User_SignUp.html',{'form':UserCreationForm,'error':'Password did not Matched'})
    else:
        return render(request,'todo/User_SignUp.html',{'form':UserCreationForm})
@login_required
def current_todos(request):
    todos=Todo.objects.filter(user=request.user,datecompleted__isnull=True)
    return render(request,'todo/Currrent_Todos.html',{'todos':todos})
@login_required
def create_todo(request):
    if request.method =='POST':
        try:
            form=TodoForm(request.POST)
            newtodo=form.save(commit=False)
            newtodo.user=request.user
            newtodo.save()
            return redirect('current_todos')
        except ValueError:
            return render(request,'todo/Create_Todo.html',{'form':TodoForm(),'error':'Bad Data Passed in.Please Try Again'})
    else:
        return render(request,'todo/Create_Todo.html',{'form':TodoForm()})
@login_required
def view_todo(request,todo_pk):
    todo=get_object_or_404(Todo,pk=todo_pk,user=request.user)
    if request.method =='GET':
        form=TodoForm(instance=todo)
        return render(request,'todo/View_Todo.html',{'todo':todo,'form':form})
    else:
        try:
            form=TodoForm(request.POST,instance=todo)
            form.save()
            return redirect('current_todos')
        except ValueError:
            return render(request, 'todo/View_Todo.html', {'todo': todo, 'form': form,'error':'Bad Data Passed in...Please Try Again'})
@login_required
def complete_todo(request,todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted =timezone.now()
        todo.save()
        return redirect('current_todos')
@login_required
def delete_todo(request,todo_pk):
    # todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    todo=Todo.objects.get(pk=todo_pk,user=request.user)
    if request.method =='POST':
        todo.delete()
        return redirect('current_todos')
    else:
        return render(request,'todo/home.html',{'error':'Data not Deleted'})
@login_required
def completed_todos(request):
    todos=Todo.objects.filter(user=request.user,datecompleted__isnull=False).order_by('-datecompleted')
    return render(request,'todo/Completed_Todos.html',{'todos':todos})



@login_required
def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

def login_user(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/Login_User.html', {'form': AuthenticationForm,'error':'Username and Password did not Match'})
        else:
            login(request,user)
            return redirect('current_todos')
    else:
        return render(request, 'todo/Login_User.html', {'form': AuthenticationForm})
