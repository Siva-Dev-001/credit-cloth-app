# credit-cloth-app
cloth-credit-manager – clearly conveys it's for managing clothing sales with credit and payments.

**credit-based clothing retail management system** using Django

# Cloth Credit Manager 👗💳

A Django-based web application to manage credit-based clothing retail businesses. This app allows customer account creation, item purchases on down payment, installment tracking, inventory management, and flexible return/exchange policies.

---

## 🚀 Features

### 🛍️ Customer & Purchase Management
- Register customers with contact and address details.
- Track multiple dress material purchases per customer.
- Record down payments and calculate remaining balances dynamically.
- Associate items with individual purchases (with quantity and price/unit).

### 💰 Payment Tracking
- Weekly/Monthly repayment plans.
- Collect installment payments and update customer dues.
- View payment history and due summaries.
- Merge additional item costs into ongoing dues.

### 📦 Inventory System
- Add/edit dress material items with:
  - Item name, description
  - HSN/SAC code
  - Actual cost and markup price
  - Units
- Manage and display inventory dynamically.

### 🔄 Returns & Exchange
- **Returns** allowed only if product is damaged and purchased within 7 days.
- **Exchange** allowed only if item is unused and in original packaging.
- Refunds are not allowed.

### 📊 Dashboard & Reporting
- Admin dashboard for customer dues, total paid, first purchase date, last payment date.
- Paginated views for payments and inventories.

---

## 🛠️ Tech Stack

- **Backend:** Django (MVT)
- **Frontend:** HTML5, Bootstrap 5, jQuery
- **Database:** SQLite / PostgreSQL
- **Timezone:** Asia/Kolkata (IST)
- **Deployment Ready:** Gunicorn, Nginx, Docker (optional)

---

## 🔧 Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/cloth-credit-manager.git
   cd cloth-credit-manager
````

2. **Create & activate virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # on Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**

   ```bash
   python manage.py migrate
   ```

5. **Run development server**

   ```bash
   python manage.py runserver
   ```

6. **Create superuser (optional)**

   ```bash
   python manage.py createsuperuser
   ```

---

## 📂 Project Structure

```
cloth_credit_manager/
├── customers/
├── inventory/
├── payments/
├── templates/
├── static/
├── manage.py
└── requirements.txt
```

---

## ✍️ Developer Notes

* Ensure Django timezone setting is UTC. Displayed in **Asia/Kolkata** using custom template filter `to_ist`.
* Payments are tracked and grouped per customer dynamically.
* Ajax has been removed for simplicity—uses full HTML forms and POST.

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 🙌 Acknowledgements

* Django Project
* Bootstrap Framework
* Indian GST HSN/SAC Code Guidelines

---

```

Let me know if you want a version of this README with badges (build status, license, Python version), or if you're using Docker and want that setup included too.
```
