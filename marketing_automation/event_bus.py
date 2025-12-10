class EventBus:
    """
    Implementation of the Publish/Subscribe pattern.
    This is the central connector of our architecture.
    """
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type: str, callback):
        """
        Allows a module (Subscriber) to subscribe to a specific event type.
        The 'callback' is the function that will be called when the event occurs.
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        print(f"--> [BUS] Subscription successful for event: {event_type}")

    def publish(self, event_type: str, data: dict):
        """
        Allows a client (Publisher) to publish an event to the bus.
        """
        print(f"\n<<< [BUS] Event Published: {event_type} >>>")
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback(data)
        else:
            print(f"--- No subscribers for event {event_type}. ---")

event_bus = EventBus()