from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_SERVICE_KEY
        )
        self.anon_client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
    
    def get_client(self, use_service_key: bool = True) -> Client:
        """Get Supabase client"""
        if use_service_key:
            return self.client
        return self.anon_client
    
    async def health_check(self) -> bool:
        """Check database connection"""
        try:
            response = self.client.table('chapters').select('id').limit(1).execute()
            return len(response.data) >= 0
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

# Global instance
supabase_client = SupabaseClient()