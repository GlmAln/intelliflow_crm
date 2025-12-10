from .models import Campaign, PRODUCT_DATA
from .event_bus import event_bus

class CampaignManager:
    """
    This module is the main Subscriber to customer events.
    It is responsible for creating and updating campaigns and their metrics.
    """
    def __init__(self):
        self.campaigns = {}
        self.product_map = {p.product_id: p for p in PRODUCT_DATA}

    def create_campaign(self, name: str, target_segment: str, budget: float, product_ids: list) -> Campaign:
        """
        Creates and registers a new campaign.
        """
        new_campaign = Campaign(name, target_segment, budget, product_ids)
        self.campaigns[new_campaign.campaign_id] = new_campaign
        print(f"\n[MANAGER] Campaign created: {new_campaign.name}")
        return new_campaign

    # Subscription logic

    def _update_on_purchase(self, data: dict):
        """
        Handles the 'Purchase' event. Updates Conversion Rate and ROI.
        """
        campaign_id = data.get('campaign_id')
        product_id = data.get('product_id')
        
        if campaign_id in self.campaigns:
            campaign = self.campaigns[campaign_id]
            product = self.product_map.get(product_id)
            
            campaign.total_conversions += 1
            if product:
                campaign.revenue_generated += product.base_price
                
            if campaign.total_impressions > 0:
                campaign.conversion_rate = (campaign.total_conversions / campaign.total_impressions) * 100
                
            cost_factor = 0.05 
            cost = campaign.budget * cost_factor
            if cost > 0:
                campaign.roi = (campaign.revenue_generated - cost) / cost
            
            print(f"[MANAGER] Purchase processed for campaign '{campaign.name}'. ROI: {campaign.roi:.2f}")
            print(f"[MANAGER] **Updated Campaign/Ad Conversion Rate & ROI**")
        
    def _reduce_on_cancel(self, data: dict):
        """
        Handles the 'Cancel' or 'Ignore' event. Reduces Campaign Effectiveness.
        """
        campaign_id = data.get('campaign_id')
        if campaign_id in self.campaigns:
            campaign = self.campaigns[campaign_id]
            campaign.effectiveness -= 5
            campaign.effectiveness = max(0, campaign.effectiveness)
            
            print(f"[MANAGER] Cancel/Ignore processed for '{campaign.name}'. Effectiveness reduced to: {campaign.effectiveness:.1f}%")
            print(f"[MANAGER] **Reduced Campaign Effectiveness**")

    def _advance_on_ad_interaction(self, data: dict):
        """
        Handles the 'AdInteraction' event. Tracks impressions (engagement).
        """
        campaign_id = data.get('campaign_id')
        if campaign_id in self.campaigns:
            campaign = self.campaigns[campaign_id]
            campaign.total_impressions += 1
            print(f"[MANAGER] AdInteraction processed for '{campaign.name}'. Impression tracked.")
            print(f"[MANAGER] **Advanced to Next Step in Campaign Journey**")

    def setup_subscriptions(self):
        """
        Subscribes this module to relevant events from the Event Bus.
        """
        event_bus.subscribe("Purchase", self._update_on_purchase)
        event_bus.subscribe("Cancel", self._reduce_on_cancel)
        event_bus.subscribe("AdInteraction", self._advance_on_ad_interaction)

campaign_manager = CampaignManager()