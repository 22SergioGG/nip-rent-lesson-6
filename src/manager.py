from decimal import Decimal, ROUND_HALF_UP

from src.models import Apartment, Bill, Parameters, Tenant, TenantSettlement, Transfer, ApartmentSettlement
from typing import List, Tuple

class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True

    def get_apartment_costs(self, apartment_key: str, year: int = None, month: int = None) -> float | None:
        if month is not None and (month < 1 or month > 12):
            raise ValueError("Month must be between 1 and 12")
        if apartment_key not in self.apartments:
            return None
        total_cost = 0.0
        for bill in self.bills:
            if bill.apartment == apartment_key and (year is None or bill.settlement_year == year) and (month is None or bill.settlement_month == month):
                total_cost += bill.amount_pln
        return total_cost

    def get_settlement(self, apartment_key: str, year: int, month: int) -> ApartmentSettlement | None:
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")
        if apartment_key not in self.apartments:
            return None
        total_cost = self.get_apartment_costs(apartment_key, year, month)
        if total_cost is None:
            return None
        
        return ApartmentSettlement(
            key=f"{apartment_key}-{year}-{month}",
            apartment=apartment_key,
            year=year,
            month=month,
            total_due_pln=total_cost
        )
    
    def get_debtors(self, apartment_key: str, year: int, month: int) -> List[str] | None:
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")
        if apartment_key not in self.apartments:
            return None

        tenants_in_apartment = [
            (tenant_key, tenant)
            for tenant_key, tenant in self.tenants.items()
            if tenant.apartment == apartment_key
        ]
        if not tenants_in_apartment:
            return []

        transfers_by_tenant = {}
        for transfer in self.transfers:
            if transfer.settlement_year == year and transfer.settlement_month == month:
                transfers_by_tenant[transfer.tenant] = transfers_by_tenant.get(transfer.tenant, 0.0) + transfer.amount_pln

        return [
            tenant.name
            for tenant_key, tenant in tenants_in_apartment
            if transfers_by_tenant.get(tenant_key, 0.0) < tenant.rent_pln
        ]

    def get_tax(self, year: int, month: int, tax_rate: float) -> int:
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")

        total_revenue = sum(
            transfer.amount_pln
            for transfer in self.transfers
            if transfer.settlement_year == year and transfer.settlement_month == month
        )
        tax_amount = Decimal(str(total_revenue)) * Decimal(str(tax_rate))
        return int(tax_amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    def create_tenants_settlements(self, apartment_settlement: ApartmentSettlement) -> List[TenantSettlement] | None:
        if apartment_settlement.month < 1 or apartment_settlement.month > 12:
            raise ValueError("Month must be between 1 and 12")
        if apartment_settlement.apartment not in self.apartments:
            return None
        tenants_in_apartment = [tenant for tenant in self.tenants.values() if tenant.apartment == apartment_settlement.apartment]
        if not tenants_in_apartment:
            return []
        
        return [
            TenantSettlement(
                tenant=tenant.name,
                apartment_settlement=apartment_settlement.key,
                month=apartment_settlement.month,
                year=apartment_settlement.year,
                total_due_pln=apartment_settlement.total_due_pln / len(tenants_in_apartment)
            )
        for tenant in tenants_in_apartment ] 
    
    