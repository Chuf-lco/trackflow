# backend/app/services/notifications.py
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Simulates WhatsApp/SMS notifications.
    In production, integrate with Twilio or Africa's Talking API.
    """
    
    @staticmethod
    def send_whatsapp_alert(phone: str, message: str):
        """
        Send WhatsApp message (simulated)
        """
        logger.info(f"📱 WhatsApp to {phone}: {message}")
        
        # Simulate API delay
        import time
        time.sleep(0.5)
        
        # In production, you would use:
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # client.messages.create(body=message, from_='whatsapp:+14155238886', to=f'whatsapp:+254{phone}')
        
        return {
            "status": "sent",
            "phone": phone,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def get_status_message(shipment):
        """
        Generate contextual WhatsApp message based on shipment status
        """
        messages = {
            "vessel_arrival": f"🚢 Your shipment {shipment.bl_number} has arrived at Mombasa Port. Manifest processed.",
            "customs_declaration": f"📋 {shipment.bl_number} is at Customs Declaration. KRA assessment in progress.",
            "physical_verification": f"🔍 {shipment.bl_number} is undergoing physical verification at Mombasa Port.",
            "inland_transit": f"🚛 {shipment.bl_number} is in transit to destination. Track via GPS.",
            "delivered": f"✅ {shipment.bl_number} has been delivered. Thank you for using TrackFlow!"
        }
        
        return messages.get(shipment.current_status, f"Status update for {shipment.bl_number}")

# Global instance
notification_service = NotificationService()