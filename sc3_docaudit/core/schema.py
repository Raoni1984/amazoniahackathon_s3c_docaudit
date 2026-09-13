"""
SC3 DocAudit - Schema Definition
Strict Pydantic models conforming to schema.md and extending the SC3 Protocol.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator


class DocumentType(str, Enum):
    FINDING_NOTICE = "finding_notice"                 # Termo de Constatação
    INFRACTION_NOTICE = "infraction_notice"           # Auto de Infração
    EMBARGO_NOTICE = "embargo_notice"                 # Termo / Auto de Embargo
    SEIZURE_NOTICE = "seizure_notice"                 # Termo de Apreensão
    NOTIFICATION = "notification"                     # Notificação
    INSPECTION_ORDER = "inspection_order"             # Ordem de Fiscalização
    COMPLAINT_RECORD = "complaint_record"             # Registro de Denúncia
    INSPECTION_REPORT = "inspection_report"           # Relatório de Fiscalização
    CASE_FILE_COVER = "case_file_cover"               # Capa do Processo
    DEFORESTATION_VALIDATION = "deforestation_validation" # Validação de Desmatamento (SAD/PRODES)


class PartyRole(str, Enum):
    CITED_PARTY = "cited_party"       # Autuado / Notificado
    ISSUER = "issuer"                 # Agente Autuante / Fiscal
    WITNESS = "witness"               # Testemunha
    FOUND_ON_SITE = "found_on_site"   # Pessoa encontrada no local
    REPRESENTATIVE = "representative" # Representante Legal / Advogado


class Party(BaseModel):
    role: Union[PartyRole, str] = Field(..., description="Role of the involved party")
    name: Optional[str] = Field(None, description="Full name or company name as printed")
    document_id: Optional[str] = Field(None, description="CPF or CNPJ as printed")
    address: Optional[str] = Field(None, description="Address if present")


class DocumentReference(BaseModel):
    document_type: str = Field(..., description="Referenced document type (e.g., finding_notice)")
    number: str = Field(..., description="Document number referenced, preserving leading zeros")
    year: Optional[str] = Field(None, description="Year of the referenced document")


class ForensicAuditSC3(BaseModel):
    """
    SC3 Protocol - Selo Criptográfico de Cadeia de Custódia (Forensic Extension)
    """
    evidence_hash: str = Field(..., description="SHA-256 Merkle root of photo, text and geospatial data")
    temporal_match: Optional[str] = Field(None, description="Temporal consistency audit status")
    spatial_match: Optional[str] = Field(None, description="Geospatial polygon consistency audit status")
    car_audit_status: Optional[str] = Field(None, description="CAR overlap / registration audit status")
    blockchain_ready: bool = Field(True, description="Ready for zero-cost batch notarization")


class EnforcementDocument(BaseModel):
    """
    Standardized Environmental Enforcement Document Schema.
    Strictly compatible with schema.md.
    """
    document_type: Union[DocumentType, str] = Field(..., description="Type of environmental document")
    number: Optional[str] = Field(None, description="Document number as printed, keeping leading zeros")
    series: Optional[str] = Field(None, description="Series identifier if present, else null")
    year: Optional[str] = Field(None, description="Year of issuance (e.g. '2026')")
    issued_date: Optional[str] = Field(None, description="Date of issuance as printed (DD/MM/YYYY)")
    issued_time: Optional[str] = Field(None, description="Time of issuance as printed (HH:MM)")
    municipality: Optional[str] = Field(None, description="Municipality name as printed")
    agency: Optional[str] = Field(None, description="Issuing agency (e.g. SEMMA, SEMAS)")
    parties: List[Party] = Field(default_factory=list, description="Parties cited, issuer, witnesses")
    property_name: Optional[str] = Field(None, description="Name of the rural property / farm")
    car: Optional[str] = Field(None, description="Rural property registry code (CAR) as printed")
    area_ha: Optional[float] = Field(None, description="Impacted area in hectares (decimal point)")
    coordinates: List[str] = Field(default_factory=list, description="Coordinates exactly as printed, one per vertex")
    legal_basis: List[str] = Field(default_factory=list, description="Articles, decrees, laws cited (e.g. Art. 50 Dec 6514/2008)")
    fine_brl: Optional[float] = Field(None, description="Fine amount in Brazilian Reais (BRL)")
    references: List[DocumentReference] = Field(default_factory=list, description="Prior documents in the custody chain")
    officer_registration: Optional[str] = Field(None, description="Staff badge/registration number of the inspector")
    signatures: Dict[str, Any] = Field(default_factory=dict, description="Signature status: issuer, cited_party (e.g. signed, refused, absent)")
    fields: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Free-form numbered fields verbatim (optional)")
    confidence: Dict[str, float] = Field(default_factory=dict, description="Confidence score per field (0.0 to 1.0)")
    forensic_audit: Optional[ForensicAuditSC3] = Field(None, description="SC3 Protocol Forensic Audit & Cryptographic Seal")

    @field_validator("area_ha", mode="before")
    def parse_area_ha(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, str):
            clean = v.replace("ha", "").replace("hectares", "").replace(" ", "").replace(",", ".")
            try:
                return float(clean)
            except ValueError:
                return None
        return float(v) if isinstance(v, (int, float)) else None

    @field_validator("fine_brl", mode="before")
    def parse_fine_brl(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, str):
            clean = v.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
            try:
                return float(clean)
            except ValueError:
                return None
        return float(v) if isinstance(v, (int, float)) else None
