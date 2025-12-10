# 📊 IntelliFlow CRM - Marketing Automation Module

## CS411 Software Architecture Design (2025-2026 Fall)

This project implements the Marketing Automation Module (MA) for a unified CRM system, focusing on software design principles, the **Publish/Subscribe (Pub-Sub)** architecture, and quality attributes (Performance, Security).

The system is built upon the secure login infrastructure from Project \#1.

## 🎯 MA Module Overview (Project \#2 Requirements)

The Marketing Automation Module (MA) is responsible for the design, execution, and measurement of targeted campaigns, and for nurturing leads to sales-ready opportunities.

### 🚀 Key Features Implemented

| Feature | Description | Architectural Evidence |
| :--- | :--- | :--- |
| **Segmentation** | Personalizes product display by placing the article targeted in the first position for customers in the relevant segment (`Male`, `Female`, `Senior Male`). | **Module Styles** (Decoupling UI / Targeting Logic) |
| **Campaign Management** | Allows campaign creation with a defined budget and target segment. | **Module Styles** (Centralized Management Logic) |
| **Marketing Analytics** | Calculates and displays real-time metrics: **Conversion Rate**, **ROI**, and **Campaign Effectiveness**. | **Component & Connector** (via Pub-Sub) |
| **Action Simulation** | Simulates customer behavior (`Purchase`, `Cancel`, `AdInteraction`) to publish events. | **Component & Connector** (The client acts as the **Publisher**). |
| **Security (Inherited)** | Integration of the secure login page from Project \#1 (Password Hashing, Brute Force Protection, Rate Limiting). | **Quality Attributes** (Security, Reliability). |

-----

## 📊 Architectural Patterns and Quality Attributes

### 1\. Architectural Styles

  * **Primary Pattern : Publish/Subscribe (Pub-Sub)**: Used as the central connector (`EventBus`). It decouples the client's action (Publisher) from the analytical reaction (Campaign Manager Subscriber). This ensures near real-time **Performance** and high **Modifiability**.
  * **Module Styles**: Separation of concerns: UI/Routing (`login_app.py`), Data Model (`models.py`), and Core Business Logic (`campaign_manager.py`).
  * **Allocation Styles**: The code is in Python, and module states are maintained in memory (in-memory storage) to simulate fast data access, which is essential for **High Performance** requirements.

### 2\. Quality Attributes

  * **Performance (Real-Time Response)**: Assured by the Pub-Sub architecture which processes client events immediately, allowing metric updates without visible latency.
  * **Security and Data Privacy**: Inherited from Project \#1, fulfilling customer demands for security and data privacy.
  * **Reliability**: The `CampaignManager` ensures the logging of every event (`Purchase`, `Cancel`) to maintain the integrity of financial data (ROI, Conversion Rate).

-----

## 🛠️ Installation and Setup

### 📋 Prerequisites

  * Python 3.10+
  * `pip` (Python package manager)

### 1\. Install Dependencies

Create the virtual environment and install the dependencies listed in `requirements.txt`.

```bash
# Ensure you are in the project root (intelliflow_crm/)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2\. Run the Application

The entry point is the `marketing_automation/login_app.py` file (Flask application).

```bash
# Navigate to the project root
export FLASK_APP=marketing_automation.login_app
flask run
```

The server will be accessible at: **`http://127.0.0.1:5000`**

-----

## 👥 Demonstration Users (Exhaustiveness)

The system includes 6 profiles to demonstrate the robustness of segment targeting.

| Segment | Username | Password | Role in Testing |
| :--- | :--- | :--- | :--- |
| Male | `leo.dupont` | `crmpassword` | Agent / Publisher (Targeted) |
| Male | `victor.moreau` | `crmpassword` | Publisher (Proves targeting robustness) |
| Female | `mia.dubois` | `crmpassword` | Agent / Non-Targeted (Baseline) |
| Female | `sophie.leroux` | `crmpassword` | Non-Targeted (Baseline) |
| Senior Male | `jean.petit` | `crmpassword` | Admin / Publisher |
| Senior Male | `marc.durand` | `crmpassword` | Publisher |

-----

## 🧪 Demonstration Test Scenarios

Executing these tests proves the functionality of the Pub-Sub architecture and Segmentation.

### Scenario 1: Proof of Segmentation and Logic

1.  **Preparation:** Login (`leo.dupont`). Go to **"📊 Campaign Analytics"**. Create Campaign: `Smartwatch Promo` (target `Male`).
2.  **Verification Targeted (Leo):** Go to **"🛒 Product Listing"**. **Result:** The alert is **GREEN** (`Targeting ACTIVE`), and the `Smartwatch` is **🎯 TARGETED**.
3.  **Verification Coherent (Victor):** Log out, log in with **`victor.moreau`** (Male). Go to `/dashboard`. **Result:** The alert is **GREEN** and the `Smartwatch` is **🎯 TARGETED** (Proves N-to-1 targeting).
4.  **Verification Non-Targeted:** Log out, log in with **`sophie.leroux`** (Female). Go to `/dashboard`. **Result:** The alert is **ORANGE** (`Targeting INACTIVE`).

### Scenario 2: Proof of Pub-Sub Architecture (Real-Time Analytics)

1.  **Action 1 (Positive - Publisher 1):** Logged in (`leo.dupont`). Select `Smartwatch`. Action: **`💰 Purchase`**.
      * **Result Console:** Log `Event Published: Purchase`.
      * **Result UI (`/campaigns`)**: `Conversion Rate` updates, `ROI` becomes positive.
2.  **Action 2 (Negative - Effectiveness):** Select `Smartwatch`. Action: **`❌ Cancel / Remove`**.
      * **Result Console:** Log `Event Published: Cancel` and `Reduced Campaign Effectiveness`.
      * **Result UI (`/campaigns`)**: The `Effectiveness` drops by **5%** (Prouves the system reacts to negative signals).
3.  **Action 3 (Consolidation - Publisher 2):** Log out, log in with **`victor.moreau`**. Select `Smartwatch`. Action: **`💰 Purchase`**.
      * **Result UI (`/campaigns`)**: The `ROI` increases, proving the `Campaign Manager` (Subscriber) consolidated the purchases from two distinct publishers.

-----

## 👨‍💻 Authors

PRISO TOTTO Guillaume-Alain: 22501093

Ahmed Hatem A.R. Abdelwahab Haikal: 22001482

Amir hossein Ahani: 22101535

Mehmet Enim Avşar: 22202995