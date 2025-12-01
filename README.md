# Hospital Management System (HMS)

A comprehensive web-based hospital management system built with Flask (Python) for the backend and Vue.js for the frontend. This system provides a complete solution for managing hospital operations including patient appointments, doctor schedules, medical records, and administrative tasks.

## 🏥 Features

### User Roles
- **Admin**: Full system management capabilities
- **Doctor**: Patient management, appointment handling, prescription creation
- **Patient**: Appointment booking, medical history access, document management

### Core Functionality

#### Admin Dashboard
- System statistics and analytics
- Doctor and patient management
- Account flagging and reactivation
- Appointment oversight
- User search and management

#### Doctor Portal
- Appointment scheduling and management
- Patient history and treatment records
- Prescription creation and email delivery
- Dashboard analytics
- Patient communication

#### Patient Portal
- Doctor search and appointment booking
- Medical history access
- Document upload and management
- Prescription viewing
- Appointment management

### 🛠️ Technical Features

#### Background Jobs & Automation
- **Daily Reminders**: Automatic appointment reminders sent to patients
- **Monthly Reports**: Activity reports generated and sent to administrators
- **Email Notifications**: Automated email system for prescriptions, account flags, and history exports
- **CSV Exports**: Patient history and doctor data exports with email delivery

#### Security
- Role-based access control
- JWT authentication
- Password hashing
- CSRF protection disabled for API compatibility

#### Data Management
- SQLite database for development
- SQLAlchemy ORM
- Data validation and sanitization
- File upload capabilities

## 🏗️ Architecture

### Backend (Flask/Python)
- **Framework**: Flask 2.3.3
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Security-Too with JWT
- **Background Jobs**: Celery with Redis
- **Email**: Flask-Mail with Gmail SMTP
- **API**: RESTful endpoints with JSON responses

### Frontend (Vue.js)
- **Framework**: Vue 3 with Vite
- **State Management**: Pinia
- **Routing**: Vue Router
- **UI Components**: Bootstrap 5
- **HTTP Client**: Axios

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- Redis server (for background jobs)
- Gmail account (for email functionality)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the Flask development server:
   ```bash
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

### Background Jobs Setup

1. Start Redis server (Windows):
   ```bash
   redis-server
   ```

2. Start Celery worker:
   ```bash
   celery -A celery_app worker --loglevel=info
   ```

3. Start Celery beat scheduler (for periodic tasks):
   ```bash
   celery -A celery_beat beat --schedule-file=celerybeat-schedule
   ```

## 📁 Project Structure

```
HMS/
├── backend/
│   ├── app.py              # Flask application entry point
│   ├── config.py           # Configuration settings
│   ├── models.py           # Database models
│   ├── routes/             # API endpoints
│   ├── services/           # Business logic
│   ├── tasks/              # Background jobs
│   ├── utils/              # Utility functions
│   └── requirements.txt    # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── views/          # Page views
│   │   ├── stores/         # Pinia stores
│   │   ├── services/       # API service layer
│   │   └── router/         # Vue router
│   ├── package.json        # Node dependencies
│   └── vite.config.js      # Vite configuration
```

## 🔧 Key Components

### Database Models
- **User Management**: Users, Roles, Doctors, Patients
- **Medical Records**: Appointments, Treatments, Prescriptions
- **Activity Logs**: Doctor and Patient activity tracking
- **Documents**: Patient document management

### Background Tasks
- `export_tasks.py`: Patient history exports to CSV
- `notification_tasks.py`: Email notifications for flags and prescriptions
- `reminder_tasks.py`: Daily appointment reminders
- `report_tasks.py`: Monthly activity reports

### API Endpoints
- **Auth**: `/auth/login`, `/auth/register`, `/auth/refresh`
- **Admin**: `/admin/doctors`, `/admin/patients`, `/admin/appointments`
- **Doctor**: `/doctor/appointments`, `/doctor/prescriptions`, `/doctor/patients`
- **Patient**: `/patient/doctors`, `/patient/appointments`, `/patient/history`

## 📧 Email Configuration

The system is configured to use Gmail SMTP for sending emails. Update the following settings in `config.py`:
- `MAIL_USERNAME`: Your Gmail address
- `MAIL_PASSWORD`: Your Gmail app password
- `MAIL_DEFAULT_SENDER`: Default sender email

## 📈 Background Jobs

All background jobs are implemented using Celery with Redis:
- **Eager Mode**: For development (tasks execute synchronously)
- **Worker Mode**: For production (tasks execute asynchronously)
- **Retry Logic**: Automatic retry with exponential backoff
- **Task Monitoring**: Built-in task status tracking

## 🛡️ Security Features

- JWT-based authentication
- Role-based access control
- Input sanitization and validation
- Password hashing with bcrypt
- Secure file uploads

## 📊 Analytics & Reporting

- Real-time dashboard statistics
- Appointment trends and analytics
- Doctor and patient activity reports
- Custom export capabilities

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Flask community for the excellent web framework
- Vue.js team for the progressive frontend framework
- Celery for robust background job processing
- All contributors to the open-source libraries used