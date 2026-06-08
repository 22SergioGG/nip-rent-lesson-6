from src.manager import Manager
from src.models import Parameters


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
