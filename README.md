# BuyTech 
(http://shivanijoshi05.pythonanywhere.com/)

E-commerce website for Mobile/Laptop with following features:

- User Login/Register 
- Product Admin Login/Register 
- Product Category Filter/Search 
- Product Add/Delete/Update 
- Add to Cart 
- Coupon/Discount Options 
- Purchase/Receipt Options 
- Payment option with paypal

## Technology used:
- Python, Django, HTML, CSS, Jquery

## Installation

**Step 1:** Clone the repository.

```bash
git clone https://github.com/shivanijoshi05/buyTech.git 
```
**Step 2:**  Create virtual environment and install packages.

```bash
cd buyTech
python3 -m venv buytech_env
source buytech_env/bin/activate
pip install -r requirements.txt
```
**Step 3:**  Migrate database.
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```
**Step 4:** Create superuser
```bash
python3 manage.py createsuperuser
```
**Step 5:** Start server
```bash
python3 manage.py runserver
```

## Setting Environment Variables

This Django project relies on environment variables for configuration. Before you can run the application, make sure you have set the following environment variables in .env file:

```bash
DJANGO_ENV = 'development'
EMAIL_HOST_USER = 'example@gmail.com'
EMAIL_HOST_PASSWORD = 'password'
DEFAULT_FROM_EMAIL = 'example@gmail.com'
```

## Contributing

If you'd like to contribute, please follow these steps:

    Fork this repository on GitHub.
    Create a new branch for your changes.
    Commit your changes with clear messages.
    Push your branch to your forked repository.
    Create a pull request to the main branch of this repository.

