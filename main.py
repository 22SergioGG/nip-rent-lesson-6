import sys

from src.manager import Manager
from src.models import Parameters


def print_section_header(title: str):
    """Print a formatted section header"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def print_subsection_header(title: str):
    """Print a formatted subsection header"""
    print(f"\n  {title}")
    print(f"  {'-' * 40}")


def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"{amount:,.2f} PLN"


def display_apartments(manager):
    """Display all apartments with their rooms and bills"""
    print_section_header("APARTMENTS")
    
    for apartment in manager.apartments.values():
        print(f"\n📍 {apartment.name} ({apartment.key})")
        print(f"   Location: {apartment.location}")
        print(f"   Total Area: {apartment.area_m2} m²")
        
        print_subsection_header("Rooms")
        for room in apartment.rooms.values():
            print(f"      • {room.name:<25} {room.area_m2:>6} m²")
        
        # Find bills for this apartment
        apartment_bills = [bill for bill in manager.bills if bill.apartment == apartment.key]
        if apartment_bills:
            print_subsection_header("Bills")
            for bill in apartment_bills:
                month_year = f"{bill.settlement_month}/{bill.settlement_year}" if bill.settlement_month and bill.settlement_year else "N/A"
                print(f"      • {bill.type:<15} {format_currency(bill.amount_pln):>15}  Due: {bill.date_due}  Period: {month_year}")


def display_tenants(manager):
    """Display all tenants with their details and transfers"""
    print_section_header("TENANTS")
    
    for tenant in manager.tenants.values():
        print(f"\n👤 {tenant.name}")
        print(f"   Apartment: {tenant.apartment}")
        print(f"   Room: {tenant.room}")
        print(f"   Rent: {format_currency(tenant.rent_pln)}/month")
        print(f"   Deposit: {format_currency(tenant.deposit_pln)}")
        print(f"   Agreement: {tenant.date_agreement_from} to {tenant.date_agreement_to}")
        
        # Find transfers for this tenant
        tenant_transfers = [transfer for transfer in manager.transfers if transfer.tenant == tenant.name]
        if tenant_transfers:
            print_subsection_header("Transfers")
            for transfer in tenant_transfers:
                month_year = f"{transfer.settlement_month}/{transfer.settlement_year}" if transfer.settlement_month and transfer.settlement_year else "N/A"
                print(f"      • {format_currency(transfer.amount_pln):>15}  Date: {transfer.date}  Period: {month_year}")


def print_usage():
    print("Usage: python main.py <apartment_key> <year> <month>")
    print("Example: python main.py apart-polanka 2025 1")


if __name__ == '__main__':
    parameters = Parameters()
    manager = Manager(parameters)

    if len(sys.argv) == 4:
        apartment_key = sys.argv[1]
        try:
            year = int(sys.argv[2])
            month = int(sys.argv[3])
        except ValueError:
            print("Error: year and month must be integers.")
            print_usage()
            sys.exit(1)

        print_section_header("APARTMENT SETTLEMENT")
        print(f"Apartment: {apartment_key}")
        print(f"Period: {month}/{year}")

        apartment_costs = manager.get_apartment_costs(apartment_key, year, month)
        if apartment_costs is None:
            print(f"No apartment found with key '{apartment_key}' or no bills for this period.")
            sys.exit(1)

        print(f"Total apartment costs: {format_currency(apartment_costs)}")

        debtors = manager.get_debtors(apartment_key, year, month)
        print_subsection_header("Debtors")
        if debtors:
            for debtor in debtors:
                print(f"  - {debtor}")
        else:
            print("  None")

        tax = manager.get_tax(year, month, 0.085)
        total_revenue = sum(
            transfer.amount_pln
            for transfer in manager.transfers
            if transfer.settlement_year == year and transfer.settlement_month == month
        )
        print_subsection_header("Tax")
        print(f"  Taxable revenue: {format_currency(total_revenue)}")
        print(f"  Tax at 8.5%: {tax} PLN")
    else:
        if len(sys.argv) > 1:
            print("Error: invalid number of arguments.")
            print_usage()
            sys.exit(1)

        display_apartments(manager)
        display_tenants(manager)

    print(f"\n{'=' * 70}\n")