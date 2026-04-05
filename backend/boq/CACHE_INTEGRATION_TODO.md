# Redis Cache Integration TODO

## Status: Partial Implementation (2/3 Tasks Complete)

This file documents the remaining work for Plan 02-04 Redis Caching Layer.

### Completed ✓

1. **Task 1: Create Redis Cache Service** ✓
   - File: `backend/boq/cache.py` (14KB, 460 lines)
   - Implementation: BOQCacheManager with 3-layer caching
   - Features:
     - Layer 1: Parsed BOQ cache (24h TTL)
     - Layer 2: TGO emission factor cache (30d TTL)
     - Layer 3: Calculation results cache (7d TTL)
     - Cache invalidation methods
     - Graceful degradation when Redis unavailable
     - Decimal serialization support
   - Testing: ✓ All 19 unit tests pass

3. **Task 3: Create Cache Tests and Performance Validation** ✓
   - File: `backend/tests/boq/test_cache.py` (9.5KB, 19 tests)
   - Coverage: All 3 cache layers, invalidation, stats, graceful degradation
   - File: `backend/scripts/test_cache_performance.py` (6.8KB)
   - Performance script with simulation mode (99.57% latency reduction achieved)

### Blocked ⏸️

2. **Task 2: Integrate Caching into Pipeline** ⏸️
   - **Blocker**: Requires `backend/boq/carbon_pipeline.py` from Plan 02-03
   - **Status**: Plan 02-03 (Wave 3 - Carbon Pipeline) not yet implemented
   - **Dependency**: Must wait for carbon_pipeline.py, audit_trail.py to exist

### Integration Instructions (For Plan 02-03 Completion)

When implementing the carbon calculation pipeline (Plan 02-03), integrate caching as follows:

#### 1. Import cache manager

```python
# In backend/boq/carbon_pipeline.py
from .cache import get_cache_manager
import hashlib
```

#### 2. Update `calculate_boq_carbon` method

Add caching at the beginning:

```python
def calculate_boq_carbon(
    self,
    boq_file_path: str,
    uploaded_by: Optional[str] = None,
    language: str = "th"
) -> Dict[str, Any]:
    """Calculate carbon footprint for BOQ file (with caching)."""

    # Get cache manager
    cache = get_cache_manager()

    # Calculate file hash for caching
    with open(boq_file_path, 'rb') as f:
        file_content = f.read()
        file_hash = hashlib.sha256(file_content).hexdigest()

    # ========== Layer 3: Check calculation result cache ==========
    cached_result = cache.get_calculation_result(file_hash, self.tgo_version)
    if cached_result:
        logger.info("Cache hit (Layer 3): Returning cached calculation result")
        cached_result["cached"] = True  # Mark as cached
        return cached_result

    # ========== Layer 1: Check parsed BOQ cache ==========
    cached_parsed = cache.get_parsed_boq(file_hash)
    if cached_parsed:
        logger.info("Cache hit (Layer 1): Using cached parsed BOQ")
        boq_result = self._reconstruct_boq_result(cached_parsed)
    else:
        # Parse BOQ (no cache)
        boq_result = parse_boq(boq_file_path)
        cache.cache_parsed_boq(file_hash, boq_result.dict())

    # Continue with rest of pipeline...
    # (material matching, carbon calculation)

    # ========== Cache Layer 3: Store calculation result ==========
    response["cached"] = False
    cache.cache_calculation_result(file_hash, self.tgo_version, response)

    return response
```

#### 3. Add emission factor caching in calculation loop

Replace emission factor queries with cached version:

```python
def _calculate_material_carbon(self, match: BOQMaterialMatch) -> Dict[str, Any]:
    """Calculate carbon for single material (with Layer 2 caching)."""

    cache = get_cache_manager()
    tgo_material_id = match.tgo_match.get("material_id")

    # ========== Layer 2: Check emission factor cache ==========
    cached_ef = cache.get_emission_factor(tgo_material_id, self.tgo_version)

    if cached_ef:
        logger.debug(f"Cache hit (Layer 2): Emission factor for {tgo_material_id}")
        emission_factor_data = cached_ef
    else:
        # Query from GraphDB
        emission_factor_data = get_emission_factor(
            self.graphdb_client,
            tgo_material_id,
            version=self.tgo_version
        )

        # Cache emission factor
        cache.cache_emission_factor(tgo_material_id, self.tgo_version, emission_factor_data)

    # Continue with calculation...
```

#### 4. Add helper methods

```python
def _reconstruct_boq_result(self, cached_data: Dict) -> BOQParseResult:
    """Reconstruct BOQParseResult from cached dictionary."""
    from .parser import BOQParseResult
    return BOQParseResult(**cached_data)
```

### Testing Integration

Once pipeline is integrated:

```bash
# Run cache tests (should still pass)
pytest backend/tests/boq/test_cache.py -v

# Run performance test with real BOQ file
python backend/scripts/test_cache_performance.py tests/fixtures/boq/sample_boq.xlsx

# Expected output:
# Uncached time: ~25s (first query)
# Cached time: ~0.16s (second query)
# Latency reduction: ≥99%
# ✓ PASS: Cache performance target met
```

### Verification Checklist

Before marking Plan 02-04 as complete:

- [ ] carbon_pipeline.py exists and is functional
- [ ] Cache integrated into pipeline's `calculate_boq_carbon` method
- [ ] Layer 1 (parsed BOQ) caching working
- [ ] Layer 2 (emission factors) caching working
- [ ] Layer 3 (calculation results) caching working
- [ ] Performance test shows ≥99% latency reduction on real BOQ file
- [ ] Cache stats endpoint accessible
- [ ] Graceful degradation tested (Redis unavailable)
- [ ] All tests pass

### Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Layer 1 cache (parsed BOQ) | 24h TTL | ✓ Implemented |
| Layer 2 cache (emission factors) | 30d TTL | ✓ Implemented |
| Layer 3 cache (calculation results) | 7d TTL | ✓ Implemented |
| Latency reduction | ≥99% | ✓ Simulated (99.57%) |
| Cache hit rate (after warmup) | ≥90% | ⏸️ Pending real data |
| Graceful degradation | Required | ✓ Implemented |

### Notes

- Redis client is synchronous (redis-py) to avoid async/await overhead in pipeline
- Separate from async Redis client in `core.services.redis` (used for streams)
- Cache invalidation on TGO version updates implemented
- Decimal serialization working (no precision loss)
- All cache operations fail gracefully if Redis unavailable

### Contact

For questions about cache integration, see:
- Implementation: `backend/boq/cache.py`
- Tests: `backend/tests/boq/test_cache.py`
- Performance: `backend/scripts/test_cache_performance.py`
- Plan: `.planning/phases/02-boq-analysis-engine/02-04-redis-caching.PLAN.md`
