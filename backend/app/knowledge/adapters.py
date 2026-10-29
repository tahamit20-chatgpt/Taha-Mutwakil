"""Future approved sources: explicit contracts, never proprietary browser dependence."""
from typing import Protocol
class NotConfigured(RuntimeError): pass
class SelectionReferenceAdapter(Protocol):
    def approved_performance(self, reference_id:str, conditions:dict) -> dict: ...
class ICAPAdapter(Protocol):
    def approved_cost_context(self, configuration_id:str, revision:str) -> dict: ...
class UnconfiguredSelection:
    def approved_performance(self, reference_id, conditions):raise NotConfigured('Pending authorized product curves and engineering validation')
class UnconfiguredICAP:
    def approved_cost_context(self, configuration_id, revision):raise NotConfigured('ICAP requires approved configuration and cost data')
