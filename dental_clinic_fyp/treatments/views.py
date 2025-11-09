from django.shortcuts import render,redirect
from .models import Treatment
from users.models import Doctor,Patient
from django.contrib.auth.decorators import login_required

@login_required
def treatment_form(request):
    if request.method=='POST':
        patient_id=request.POST['patient']
        description=request.POST['description']
        Treatment.objects.create(
            patient=Patient.objects.get(id=patient_id),
            doctor=request.user.doctor,
            description=description
        )
        return redirect('treatment_history')
    return render(request,'treatments/treatment_form.html',{'patients':Patient.objects.all()})

@login_required
def treatment_history(request):
    if request.user.role=='doctor':
        treatments=Treatment.objects.filter(doctor=request.user.doctor)
    elif request.user.role=='patient':
        treatments=Treatment.objects.filter(patient=request.user.patient)
    else:
        treatments=Treatment.objects.all()
    return render(request,'treatments/treatment_history.html',{'treatments':treatments})
