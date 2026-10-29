from datetime import date
from typing import Literal
from pydantic import Field, model_validator
from app.workflow.models import Strict

class EvidenceInput(Strict):
    title:str=Field(min_length=3,max_length=300)
    reference:str=Field(min_length=3,max_length=300)
    source_date:date|None=None
    source_revision:str|None=Field(default=None,max_length=100)
    source_type:Literal['HISTORICAL_LETTER','INTERNAL_PORTFOLIO','CURRENT_CUSTOMER_SOURCE','SYNTHETIC_TEST']
    authority:str=Field(min_length=3,max_length=300)
    notes:str=Field(min_length=5,max_length=2000)

class CommodityInput(Strict):
    profile_id:str
    commodity_code:str=Field(pattern=r'^\d{10}$')
    commodity_description:str=Field(min_length=5,max_length=500)
    product_category:Literal['Pump / Pump Set','Valve','Spare Parts']
    evidence_id:str
    original_approval_date:date|None=None
    valid_from:date|None=None
    valid_until:date|None=None
    page:int|None=Field(default=None,ge=1)
    restrictions:str=Field(default='',max_length=2000)
    expected_version:int|None=None
    reason:str=Field(min_length=5,max_length=1500)
    @model_validator(mode='after')
    def dates(self):
        if self.valid_from and self.valid_until and self.valid_until<self.valid_from:raise ValueError('Validity end precedes start')
        return self

class SeriesInput(Strict):
    name:str=Field(min_length=2,max_length=100)
    product_category:Literal['Pump / Pump Set','Valve','Spare Parts']
    classification:str=Field(min_length=2,max_length=300)
    api_classification:str|None=Field(default=None,max_length=40)
    design_standards:list[str]=Field(default=[],max_length=20)
    manufacturing_reference:str|None=Field(default=None,max_length=1000)
    engineering_notes:str=Field(default='',max_length=2000)
    expected_version:int|None=None
    reason:str=Field(min_length=5,max_length=1500)

class MappingInput(Strict):
    product_series_id:str
    commodity_id:str
    evidence_id:str
    slide:int|None=Field(default=None,ge=1,le=10000)
    engineering_notes:str=Field(default='',max_length=2000)
    expected_version:int|None=None
    reason:str=Field(min_length=5,max_length=1500)

class VerificationInput(Strict):
    evidence_id:str
    status:Literal['REQUIRES_VERIFICATION','VERIFIED','CONDITIONAL','SUSPENDED','REVOKED','SUPERSEDED']
    verification_date:date
    valid_from:date|None=None
    valid_until:date|None=None
    authorized_current_source:bool=False
    restrictions:str=Field(default='',max_length=2000)
    reviewer_notes:str=Field(min_length=5,max_length=2000)
    supersedes_verification_id:str|None=None
    @model_validator(mode='after')
    def dates(self):
        if self.verification_date>date.today():raise ValueError('Verification cannot be future-dated')
        if self.valid_from and self.valid_until and self.valid_until<self.valid_from:raise ValueError('Validity end precedes start')
        if self.status=='CONDITIONAL' and len(self.restrictions)<5:raise ValueError('Conditional evidence requires explicit restrictions')
        return self

class AssignmentInput(Strict):
    expected_version:int
    tag:str
    product_series_id:str|None=None
    proposed_vendor_code:str|None=Field(default=None,max_length=40,pattern=r'^[A-Za-z0-9_-]+$')
    proposed_plant_id:str|None=Field(default=None,max_length=40,pattern=r'^[A-Za-z0-9_-]+$')
    component_approval:Literal['PENDING','NOT_APPLICABLE','VERIFIED']='PENDING'
    component_evidence:str=Field(default='',max_length=1500)
    reason:str=Field(min_length=5,max_length=1500)
    @model_validator(mode='after')
    def component(self):
        if self.component_approval in ('NOT_APPLICABLE','VERIFIED') and len(self.component_evidence)<5:raise ValueError('Component disposition requires supporting evidence/reason')
        return self

class PolicyInput(Strict):
    expected_version:int
    unresolved_design_deviation:Literal['INSUFFICIENT DATA','CONDITIONAL GO']='INSUFFICIENT DATA'
    rationale:str=Field(min_length=10,max_length=1500)
