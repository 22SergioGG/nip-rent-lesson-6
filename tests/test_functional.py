from src.manager import Manager
from src.models import Parameters, Transfer


def test_total_due_pln_sum_matches_apartment_costs():
    parameters = Parameters(
        apartments_json_path='data/apartments.json',
        tenants_json_path='data/tenants.json',
        transfers_json_path='data/transfers.json',
        bills_json_path='data/bills.json'
    )
    manager = Manager(parameters)

    apartment_key = 'apart-polanka'
    year = 2025
    month = 1

    apartment_costs = manager.get_apartment_costs(apartment_key, year, month)
    apartment_settlement = manager.get_settlement(apartment_key, year, month)
    tenant_settlements = manager.create_tenants_settlements(apartment_settlement)

    assert apartment_costs is not None
    assert apartment_settlement is not None
    assert tenant_settlements is not None

    total_due_sum = sum(settlement.total_due_pln for settlement in tenant_settlements)

    assert total_due_sum == apartment_costs
    assert total_due_sum == apartment_settlement.total_due_pln


def test_get_debtors_returns_tenants_with_insufficient_transfers():
    parameters = Parameters(
        apartments_json_path='data/apartments.json',
        tenants_json_path='data/tenants.json',
        transfers_json_path='data/transfers.json',
        bills_json_path='data/bills.json'
    )
    manager = Manager(parameters)

    manager.transfers = [
        Transfer(amount_pln=1000, date='2025-01-01', settlement_year=2025, settlement_month=1, tenant='tenant-1'),
        Transfer(amount_pln=2000, date='2025-01-02', settlement_year=2025, settlement_month=1, tenant='tenant-2'),
        Transfer(amount_pln=3000, date='2025-01-03', settlement_year=2025, settlement_month=1, tenant='tenant-3'),
    ]

    debtors = manager.get_debtors('apart-polanka', 2025, 1)

    assert debtors == ['Jan Nowak']


def test_get_tax_calculates_total_tax_for_month():
    parameters = Parameters(
        apartments_json_path='data/apartments.json',
        tenants_json_path='data/tenants.json',
        transfers_json_path='data/transfers.json',
        bills_json_path='data/bills.json'
    )
    manager = Manager(parameters)

    tax = manager.get_tax(2025, 1, 0.085)

    assert tax == 638
