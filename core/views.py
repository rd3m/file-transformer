from django.shortcuts import render

from core.models import ProcessedFile
from .forms import UploadFileForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.conf import settings
from .forms import SignUpForm
import pandas as pd
from io import BytesIO
import openai
import os
import ast


openai.api_key = os.environ["OPENAI_API_KEY"]


def is_valid_python_code(code):
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def generate_prompt(user_prompt):
    # Prepend a general instruction to the user's prompt
    general_instruction = "Generate only Python code to perform the following operation on a pandas DataFrame 'df':\n"

    # Add extra context to clarify the input
    context = "\nPlease note that the DataFrame 'df' is a pandas DataFrame, and the columns should be accessed using pandas methods and attributes."

    data_type_instruction = "\nConsider different data types in the DataFrame's columns and handle them appropriately."

    # Append a specific instruction to guide the output format
    output_instruction = "\n\nReturn only the Python code without explanations or comments, this will be executed automatically so don't use values that need to be changed before executing."

    # Combine the instructions and the user's prompt
    modified_prompt = (
        general_instruction
        + user_prompt
        + context
        + data_type_instruction
        + output_instruction
    )

    return modified_prompt


def call_openai_api(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.2,
    )

    return response.choices[0].text.strip()  # type: ignore


def process_file(prompt, file, user):
    # Read the uploaded file
    file.seek(0)  # Reset the file pointer to the beginning
    file_extension = file.name.split(".")[-1].lower()

    if file_extension == "csv":
        df = pd.read_csv(file)
    elif file_extension == "xlsx":
        df = pd.read_excel(file)
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")

    # Generate the modified prompt using the user's prompt
    modified_prompt = generate_prompt(prompt)

    # Fetch the generated code from the OpenAI API using the modified prompt
    generated_code = call_openai_api(modified_prompt)

    print(f"User prompt: {prompt}")
    print(f"Generated code: {generated_code}")

    # Save the modified prompt and file name in the database
    processed_file_record = ProcessedFile(
        user=user, prompt=prompt, file_name=file.name, generated_code=generated_code
    )
    processed_file_record.save()

    # Execute the generated code on the DataFrame `df`
    try:
        if is_valid_python_code(generated_code):
            exec(generated_code, {"df": df})
        else:
            raise ValueError("Generated code is not valid Python code")
    except Exception as e:
        raise ValueError(f"Error executing generated code: {str(e)}")

    # Save the modified DataFrame to a new file-like buffer
    output_buffer = BytesIO()
    if file_extension == "csv":
        df.to_csv(output_buffer, index=False)
    elif file_extension == "xlsx":
        df.to_excel(output_buffer, index=False)

    # Set the buffer's pointer to the beginning and return it
    output_buffer.seek(0)
    return output_buffer


@login_required
def upload_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save()
            try:
                processed_file = process_file(
                    uploaded_file.prompt, uploaded_file.file, request.user
                )

                response = HttpResponse(
                    processed_file, content_type="application/vnd.ms-excel"
                )
                response[
                    "Content-Disposition"
                ] = f'attachment; filename="{uploaded_file.file.name}"'

                # Delete the file from the media/uploads folder
                uploaded_file.file.delete()

            except ValueError as e:
                # Delete the file from the media/uploads folder
                uploaded_file.file.delete()

                # Add the error to the form
                form.add_error("prompt", str(e))

                # Render the form with the error
                return render(request, "core/upload.html", {"form": form})

            # Clear form errors
            form.errors.clear()

            return response
    else:
        form = UploadFileForm()

    return render(request, "core/upload.html", {"form": form})


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
    else:
        form = SignUpForm()
    return render(request, "core/signup.html", {"form": form})
