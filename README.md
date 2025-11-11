
1. **Clone the Repository**
   ```bash
   git clone https://github.com/ashraya/dentalclinicms.git
   cd dental_clinic_fyp

2. **Set Up a Virtual Environment**
   ```bash
   python -m venv venv
   # On macOS/Linux
   source venv/bin/activate
   # On Windows
   venv\Scripts\activate
   
3. **Install Dependencies and Apply Migrations**
   ```bash
   pip install -r requirements.txt
   python manage.py makemigrations
   python manage.py migrate
4. **Create a Superuser (Admin Account)**
   ```bash
    python manage.py createsuperuser
   Follow the prompts to set up admin credentials.

5. **Run the Development Server**
   ```bash
   python manage.py runserver
By default, the site will be available at http://127.0.0.1:8000/
