import uuid

def short_uuid():
    """Helper to shorten UUID display for readability."""
    return str(uuid.uuid4())[:8]

class Product:
    def __init__(self, name: str, category: str, base_price: float, targeting_segment: str):
        """
        Represents a product in the CRM.
        """
        self.product_id = uuid.uuid4()
        self.name = name
        self.category = category
        self.base_price = base_price
        # 'Male', 'Female', 'Senior Male'
        self.targeting_segment = targeting_segment 

    def __str__(self):
        return f"Product: {self.name} (ID: {short_uuid()}) - Targets: {self.targeting_segment}"

class Customer:
    def __init__(self, name: str, age: int, gender: str, segment: str, preferred_channel: str = 'Email'):
        """
        Represents a customer, acting as the 'Publisher' in our Pub/Sub architecture.
        """
        self.customer_id = uuid.uuid4()
        self.name = name
        self.age = age
        self.gender = gender
        # 'Male', 'Female', 'Senior Male'
        self.segment = segment 
        self.preferred_channel = preferred_channel 
        self.clv_score = 0.0

    def __str__(self):
        return f"Customer: {self.name} (Segment: {self.segment}, CLV: {self.clv_score:.2f})"

class Campaign:
    def __init__(self, name: str, target_segment: str, budget: float, product_ids: list):
        """
        Represents a Marketing Campaign.
        """
        self.campaign_id = uuid.uuid4()
        self.name = name
        self.target_segment = target_segment
        self.budget = budget
        self.product_ids = product_ids

        self.conversion_rate = 0.0
        self.roi = 0.0
        self.effectiveness = 100.0

        self.total_impressions = 0
        self.total_conversions = 0
        self.revenue_generated = 0.0

    def __str__(self):
        return f"Campaign: {self.name} (Target: {self.target_segment}, Budget: ${self.budget:,.2f})"

CUSTOMER_DATA = [
    Customer("Leo Dupont", 35, "Male", "Male"),
    Customer("Victor Moreau", 40, "Male", "Male"),
    
    Customer("Mia Dubois", 28, "Female", "Female", preferred_channel='Notification'),
    Customer("Sophie Leroux", 25, "Female", "Female"),
    
    Customer("Jean Petit", 68, "Male", "Senior Male", preferred_channel='Phone Call'),
    Customer("Marc Durand", 65, "Male", "Senior Male")
]

PRODUCT_DATA = [
    Product("Smartwatch", "Accessories", 199.99, "Male"),
    Product("Beauty Kit", "Cosmetics", 55.50, "Female"),
    Product("Reading Subscription", "Services", 15.00, "Senior Male")
]