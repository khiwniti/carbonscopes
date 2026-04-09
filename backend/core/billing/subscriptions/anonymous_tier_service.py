from typing import Dict
from datetime import datetime
import uuid
from core.utils.logger import logger
from core.utils.distributed_lock import DistributedLock
from core.billing import repo as billing_repo
from ..shared.cache_utils import invalidate_account_state_cache


class AnonymousTierService:
    """
    Provisions billing for anonymous (guest) Supabase users.
    Skips Stripe, email, welcome notifications, and referrals entirely.
    Uses the 'anonymous' tier with 3-thread / 1-concurrent-run limits.
    """

    async def setup_anonymous_account(self, account_id: str) -> Dict:
        lock_key = f"anonymous_tier_setup:{account_id}"
        lock = DistributedLock(lock_key, timeout_seconds=30)
        acquired = await lock.acquire(wait=True, wait_timeout=10)
        if not acquired:
            logger.warning(f"[ANON TIER] Could not acquire lock for {account_id}")
            return {'success': False, 'message': 'Lock acquisition failed'}

        try:
            existing = await billing_repo.get_credit_account_for_free_tier(account_id)
            if existing:
                existing_tier = existing.get('tier')
                if existing_tier and existing_tier != 'none':
                    # Already provisioned with a real tier — don't downgrade
                    logger.info(f"[ANON TIER] {account_id} already has tier '{existing_tier}', skipping")
                    return {'success': False, 'message': 'Already initialized'}

            mock_sub_id = f"anon_{account_id[:8]}_{uuid.uuid4().hex[:12]}"

            await billing_repo.upsert_credit_account(account_id, {
                'tier': 'anonymous',
                'stripe_subscription_id': mock_sub_id,
                'last_grant_date': datetime.now().isoformat(),
                'balance': 0,
                'expiring_credits': 0,
                'non_expiring_credits': 0,
            })

            # Grant initial daily credits so the first agent run is not blocked
            try:
                from core.services.credits import credit_service
                await credit_service.check_and_refresh_daily_credits(account_id)
            except Exception as e:
                logger.warning(f"[ANON TIER] Could not grant initial credits to {account_id}: {e}")

            await invalidate_account_state_cache(account_id)

            logger.info(f"[ANON TIER] ✅ Initialized anonymous account {account_id}")
            return {'success': True, 'subscription_id': mock_sub_id}

        except Exception as e:
            logger.error(f"[ANON TIER] Error initializing {account_id}: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            await lock.release()


anonymous_tier_service = AnonymousTierService()
