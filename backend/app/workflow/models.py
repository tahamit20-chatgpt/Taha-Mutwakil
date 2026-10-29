from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,model_validator
from datetime import date
class Strict(BaseModel): model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)
Product=Literal['Pump / Pump Set','Valve','Spare Parts','Mixed Package']
class Classification(Strict):
    product_category: Product
    market_area: str=Field(min_length=1,max_length=100)
    application: str=Field(min_length=1,max_length=100)
    customer_profile: str=Field(default='Other / General Customer',max_length=160)
    customer: str=Field(min_length=1,max_length=160)
    end_user: str=Field(default='',max_length=160)
    contractor: str=Field(default='',max_length=160)
    location: str=Field(default='',max_length=160)
    country: str=Field(default='',max_length=80)
    rfq_reference: str=Field(default='',max_length=100)
    submission_deadline: date|None=None
    assigned_engineer: str=Field(default='',max_length=160)
class Equipment(Strict):
    tag: str=Field(pattern=r'^[A-Za-z0-9_-]{1,40}$')
    product_category: Literal['Pump / Pump Set','Valve','Spare Parts']
    description: str=Field(default='',max_length=300)
    quantity: int|None=Field(default=None,ge=1,le=100000)
class CreateRFQ(Strict):
    name: str=Field(min_length=1,max_length=160)
    classification: Classification
    equipment: list[Equipment]=Field(min_length=1,max_length=20)
    synthetic: Literal[True]=True
class EditClassification(CreateRFQ): expected_version:int
class ReviewSummary(Strict):
    expected_version:int
    summary_hash:str
    reason:str=Field(min_length=3,max_length=1500)
class StandardInput(Strict):
    code:str=Field(min_length=2,max_length=150)
    edition:str|None=Field(default=None,max_length=80)
    category:str=Field(default='Customer',max_length=80)
    products:list[str]=[]
    source_reference:str=Field(min_length=3,max_length=1000)
    reason:str=Field(default='Engineering confirmation required',max_length=1000)
class Applicability(Strict):
    expected_version:int
    tag:str
    code:str=Field(min_length=2,max_length=150)
    edition:str|None=None
    disposition:Literal['APPLICABLE','NOT_APPLICABLE','NEEDS_REVIEW']
    reason:str=Field(min_length=3,max_length=1500)
class RuleInput(Strict):
    criterion_id:str=Field(pattern=r'^[A-Z][A-Z0-9_-]{1,39}$')
    name:str=Field(min_length=3,max_length=150)
    field:str
    product_category:Literal['Pump / Pump Set','Valve','Spare Parts']
    operator:Literal['range','enum_in','present']
    minimum:float|None=Field(default=None,allow_inf_nan=False)
    maximum:float|None=Field(default=None,allow_inf_nan=False)
    allowed_values:list[str]=[]
    units:str=''
    severity:Literal['HARD STOP','CRITICAL','MAJOR','MINOR','INFORMATIONAL']='MAJOR'
    waiver_policy:Literal['NON_WAIVABLE','WAIVABLE']='NON_WAIVABLE'
    scope:Literal['project','candidate']='candidate'
    project_prohibition:bool=False
    confirmed_prohibition_value:str|None=None
    standard_id:str|None=None
    standard_edition:str|None=None
    clause_reference:str|None=None
    market_area:str|None=None
    application:str|None=None
    customer:str|None=None
    source_reference:str=Field(min_length=5,max_length=1000)
    capability_reference:str|None=Field(default=None,max_length=1000)
    effective_date:date
    pressure_basis:Literal['gauge','absolute','differential']|None=None
    namespace:Literal['synthetic-demo-v2']='synthetic-demo-v2'
    @model_validator(mode='after')
    def validate_operator(self):
        from app.extraction.service import FIELDS
        if self.field not in FIELDS: raise ValueError('Unsupported input parameter')
        if self.operator=='range':
            if self.minimum is None and self.maximum is None: raise ValueError('Range requires a bound')
            if self.minimum is not None and self.maximum is not None and self.minimum>self.maximum: raise ValueError('Invalid bounds')
            if FIELDS[self.field] is None: raise ValueError('Range requires numeric field')
            if self.units != FIELDS[self.field][1]: raise ValueError('Rule bounds must use canonical SI units')
        if self.operator=='enum_in' and FIELDS[self.field] is not None:raise ValueError('Enum operator requires a text field')
        if self.field in ('pressure','suction_pressure','discharge_pressure','differential_pressure','vapor_pressure') and self.operator=='range' and not self.pressure_basis:raise ValueError('Pressure comparison requires explicit gauge/absolute/differential basis')
        if self.operator=='enum_in' and not self.allowed_values: raise ValueError('Enum requires allowed values')
        if self.project_prohibition and (self.scope!='project' or self.waiver_policy!='NON_WAIVABLE'): raise ValueError('Project prohibition must be project-scoped and non-waivable')
        if self.project_prohibition and (self.operator!='enum_in' or self.confirmed_prohibition_value in self.allowed_values):raise ValueError('Project prohibition requires a text enum with an explicit excluded value')
        if self.project_prohibition and not self.confirmed_prohibition_value: raise ValueError('Explicit confirmed prohibition value required')
        if self.severity=='HARD STOP' and not self.project_prohibition: raise ValueError('Hard stop requires explicit approved project prohibition')
        if self.standard_id and (not self.standard_edition or not self.clause_reference): raise ValueError('Standard-bound rule requires edition and verified source clause identifier')
        return self
class Reason(Strict): reason:str=Field(min_length=5,max_length=1500)
class FamilyInput(Strict):
    name:str=Field(min_length=2,max_length=150)
    product_category:Literal['Pump / Pump Set','Valve','Spare Parts']
    source_reference:str=Field(min_length=5,max_length=1000)
    source_revision:str=Field(min_length=1,max_length=80)
class CandidateInput(Strict):
    expected_version:int
    tag:str
    family_id:str
    model_reference:str=Field(default='',max_length=160)
    evidence_reference:str=Field(min_length=5,max_length=1500)
    notes:str=Field(default='',max_length=2000)
class PriceInput(Strict):
    expected_version:int
    tag:str
    price_kind:Literal['Base Product Price','Factory Cost','Local Industrial Cost','Landed Cost','Total Estimated Cost','Target Selling Price','Approved Selling Price']
    amount:float|None=Field(default=None,ge=0,allow_inf_nan=False)
    currency:str=Field(pattern=r'^[A-Z]{3}$')
    valid_until:date
    source_reference:str=Field(min_length=5,max_length=1000)
    source_revision:str=Field(min_length=1,max_length=100)
class QuoteInput(Strict):
    expected_version:int
    evaluation_id:str
    template_id:str
    notes:str=Field(default='',max_length=2000)
class DocumentMetadata(Strict):
    expected_version:int
    document_number:str=Field(default='',max_length=100)
    revision:str=Field(default='',max_length=80)
    category:str=Field(max_length=100)
    reason:str=Field(min_length=3,max_length=1000)
