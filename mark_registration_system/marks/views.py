import csv
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages  # Import messages
from .forms import MarkEntryForm
from .models import Marks  # Import the Marks model
from django.conf import settings
from django.db.models import Sum
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pandas as pd

import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend


# Helper function to save data to a CSV file
def save_to_csv():
    csv_file = os.path.join(settings.MEDIA_ROOT, 'marks_entries.csv')  # Save in media folder
    
    # Open CSV to rewrite with the updated records
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Student ID', 'Student Name', 'Module Code', 'Module Name', 'CW1 Marks', 'CW2 Marks', 'CW3 Marks', 'Total Marks'])
        
        # Write each record to the CSV (including updated records)
        for mark in Marks.objects.all():  # Fetch all records from the database
            total_marks = mark.cw1_marks + mark.cw2_marks + mark.cw3_marks  # Calculate total marks
            writer.writerow([
                mark.student_id,
                mark.student_name,
                mark.module_code,
                mark.module_name,
                mark.cw1_marks,
                mark.cw2_marks,
                mark.cw3_marks,
                total_marks
            ])

# Helper function to generate charts as Base64 strings
def generate_chart(plt):
    """Convert a Matplotlib plot to a Base64 image."""
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()  # Close the plot to avoid overlapping visuals
    return image_base64

# Home page view
def home(request):
    # Fetch counts for records display
    student_count = Marks.objects.values('student_id').distinct().count()
    module_count = Marks.objects.values('module_code').distinct().count()
    context = {
        'student_count': student_count,
        'module_count': module_count,
    }
    return render(request, 'marks/home.html', context)

# Input marks page view
def input_marks(request):
    if request.method == 'POST':
        form = MarkEntryForm(request.POST)
        if form.is_valid():
            # Save form data to the database
            new_mark = Marks.objects.create(
                module_code=form.cleaned_data['module_code'],
                module_name=form.cleaned_data['module_name'],
                cw1_marks=form.cleaned_data['cw1_marks'],
                cw2_marks=form.cleaned_data['cw2_marks'],
                cw3_marks=form.cleaned_data['cw3_marks'],
                student_id=form.cleaned_data['student_id'],
                student_name=form.cleaned_data['student_name'],
                gender=form.cleaned_data['gender'],
                date_of_entry=form.cleaned_data['date_of_entry'],
            )

            # Save the new entry to CSV
            save_to_csv()  # Rewrite the CSV with the latest data

            # Add a success message
            messages.success(request, 'Marks have been successfully recorded.')
            # Redirect to the same page to display the message and reset the form
            return redirect('input_marks')
    else:
        form = MarkEntryForm()
    return render(request, 'marks/input_marks.html', {'form': form})

# Update marks page view
def update_marks(request):
    records = None
    module_code = request.GET.get('module_code')  # Get module_code from the query parameter
    student_id = request.GET.get('student_id')  # Get student_id if modifying a specific student's marks

    if request.method == 'POST' and student_id:
        # Fetch the student record to update
        student = get_object_or_404(Marks, id=student_id)

        # Update the marks based on the form input
        student.cw1_marks = request.POST.get('cw1_marks')
        student.cw2_marks = request.POST.get('cw2_marks')
        student.cw3_marks = request.POST.get('cw3_marks')
        student.save()  # Save the updated record

        # After updating the marks, save the updated data to CSV
        save_to_csv()  # Rewrite the entire CSV file with updated records

        messages.success(request, 'Marks updated successfully.')
        return redirect('update_marks')  # Redirect back to the same page

    if module_code:
        # Fetch all records with the given module_code
        records = Marks.objects.filter(module_code=module_code)

        # Calculate the total marks for each record and add it to the record object
        for record in records:
            record.total_marks = record.cw1_marks + record.cw2_marks + record.cw3_marks

    return render(request, 'marks/update_marks.html', {'records': records, 'module_code': module_code, 'student_id': student_id})

# View marks page view
def view_marks(request):
    module_code = request.GET.get('module_code')
    records = None
    if module_code:
        records = Marks.objects.filter(module_code=module_code)
    return render(request, 'marks/view_marks.html', {'records': records, 'module_code': module_code})


custom_colors = [
    #'red', 'coral', 'orange', 'gold', 'yellow', 'greenyellow', 'lime',
    'aquamarine', 'turquoise', 'cyan', 'deepskyblue', 'royalblue', 
    'blue'#, 'navy', 'blueviolet', 'violet', 'fuchsia', 'deeppink', 'pink'
]

# Visualization page view
def visualization(request):
    # Fetch data
    marks = Marks.objects.all().values('module_name', 'cw1_marks', 'cw2_marks', 'cw3_marks')
    df = pd.DataFrame(marks)

    charts = {}

    if not df.empty:
        # 1. Pie Chart: Distribution of CW1, CW2, CW3 Marks
        total_cw1 = df['cw1_marks'].sum()
        total_cw2 = df['cw2_marks'].sum()
        total_cw3 = df['cw3_marks'].sum()
        plt.figure(figsize=(6, 6))
        plt.pie([total_cw1, total_cw2, total_cw3], labels=['CW1', 'CW2', 'CW3'], autopct='%1.1f%%', startangle=90, colors=custom_colors[1:4])  # Limit to 3 colors(3CW))
        plt.title('Marks Distribution')
        charts['pie_chart'] = generate_chart(plt)

        # 2. Bar Chart: Average Marks by Module
        avg_marks = df.groupby('module_name')[['cw1_marks', 'cw2_marks', 'cw3_marks']].mean()
        avg_marks.plot(kind='bar', figsize=(9, 7), color=custom_colors[:len(avg_marks)]) # Limit to the number of bars
        plt.title('Average Marks per Module')
        plt.xlabel('Modules')
        plt.ylabel('Average Marks')
        plt.xticks(rotation=45)  # Rotate labels
        plt.tight_layout()  # Adjust layout to prevent overlap
        charts['bar_chart'] = generate_chart(plt)

        # 3. Scatter Plot: CW1 vs. CW2 Marks
        plt.figure(figsize=(8, 6))
        plt.scatter(df['cw1_marks'], df['cw2_marks'], alpha=0.7, color=custom_colors[5])  # Use the first color in the list
        plt.title('CW1 vs. CW2 Marks')
        plt.xlabel('CW1 Marks')
        plt.ylabel('CW2 Marks')
        charts['scatter_plot'] = generate_chart(plt)

    return render(request, 'marks/visualization.html', {'charts': charts})
