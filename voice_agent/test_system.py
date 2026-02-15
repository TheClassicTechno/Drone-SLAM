"""
Quick test script for Medical Drone Voice Agent

This utility script tests all system components without requiring an actual phone call.
It provides commands to:
- Test environment variable configuration
- Check webhook server connectivity
- Verify Vapi API connection
- Simulate medication orders
- View system status

Usage:
    python test_system.py env        # Test environment variables
    python test_system.py server     # Test webhook server
    python test_system.py vapi       # Test Vapi connection
    python test_system.py simulate   # Simulate an order
    python test_system.py status     # View system status
    python test_system.py all        # Run all tests
"""

import os
import sys
import json
import time
import requests
from dotenv import load_dotenv

# Rich library for beautiful terminal output
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout

# Load environment variables from .env file
load_dotenv()

# Initialize rich console for styled output
console = Console()


def test_environment():
    """
    Check if all required and optional environment variables are properly set

    This function verifies that:
    - Required API keys (Vapi, Groq) are present
    - Optional keys (Deepgram, Webhook URL) are noted if missing

    Returns:
        bool: True if all required variables are set, False otherwise
    """
    console.print("\n[bold blue] Testing Environment Setup[/bold blue]\n")

    # Required API keys that must be present for system to function
    required_vars = {
        "VAPI_API_KEY": "Vapi API Key",
        "GROQ_API_KEY": "Groq API Key",
    }

    # Optional configurations that enhance but aren't critical
    optional_vars = {
        "DEEPGRAM_API_KEY": "Deepgram API Key (recommended)",
        "WEBHOOK_BASE_URL": "Webhook Base URL (for Vapi callbacks)",
    }

    all_good = True

    # Check all required variables
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            console.print(f" {description}: {value[:20]}...")
        else:
            console.print(f" {description}: NOT SET", style="bold red")
            all_good = False

    # Check optional
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            console.print(f" {description}: {value[:40]}...")
        else:
            console.print(f"  {description}: Not set (optional)", style="yellow")

    if all_good:
        console.print("\n[bold green] Environment configured correctly![/bold green]\n")
        return True
    else:
        console.print("\n[bold red] Please set missing environment variables in .env file[/bold red]\n")
        return False


def test_webhook_server():
    """Test if webhook server is running"""
    console.print("\n[bold blue] Testing Webhook Server[/bold blue]\n")

    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        if response.status_code == 200:
            data = response.json()
            console.print(" Webhook server is running!")
            console.print(f"   Active Orders: {data.get('active_orders', 0)}")
            console.print(f"   Available Drones: {data.get('available_drones', 0)}")
            return True
    except requests.exceptions.ConnectionError:
        console.print(" Webhook server is NOT running!", style="bold red")
        console.print("\n   Start it with:")
        console.print("   [yellow]python voice_agent/webhook_server.py[/yellow]\n")
        return False
    except Exception as e:
        console.print(f" Error connecting to webhook server: {e}", style="bold red")
        return False


def test_vapi_connection():
    """Test Vapi API connection"""
    console.print("\n[bold blue] Testing Vapi API Connection[/bold blue]\n")

    try:
        from vapi_python import Vapi
        vapi = Vapi(api_key=os.getenv('VAPI_API_KEY'))

        # Try to list assistants (will work even if none exist)
        assistants = vapi.assistants.list()
        console.print(f" Vapi API connected successfully!")
        console.print(f"   Total Assistants: {len(assistants)}")

        # Check if our assistant exists
        try:
            with open('/Users/julih/Drone-SLAM/voice_agent/assistant_id.txt', 'r') as f:
                assistant_id = f.read().strip()
                assistant = vapi.assistants.get(assistant_id)
                console.print(f"   Medical Drone Assistant:  Found (ID: {assistant_id[:20]}...)")
                return True
        except FileNotFoundError:
            console.print("   Medical Drone Assistant:   Not created yet", style="yellow")
            console.print("\n   Create it with:")
            console.print("   [yellow]python voice_agent/vapi_setup.py create[/yellow]\n")
            return False

    except Exception as e:
        console.print(f" Vapi API connection failed: {e}", style="bold red")
        return False


def simulate_order():
    """Simulate a medication order"""
    console.print("\n[bold blue] Simulating Medication Order[/bold blue]\n")

    test_order = {
        "caller_name": "Dr. Sarah Chen",
        "facility": "City General Hospital",
        "department": "Emergency Department",
        "medications": [
            {
                "name": "Amoxicillin",
                "dosage": "500mg",
                "quantity": 20,
                "form": "tablet"
            },
            {
                "name": "Epinephrine",
                "dosage": "0.3mg",
                "quantity": 3,
                "form": "auto-injector"
            }
        ],
        "urgency": "STAT",
        "delivery_location": {
            "building": "Main Hospital",
            "floor": "1",
            "specific_area": "ER Trauma Bay 2",
            "access_instructions": "Rooftop helipad"
        }
    }

    console.print("[bold]Order Details:[/bold]")
    console.print(json.dumps(test_order, indent=2))

    try:
        response = requests.post(
            "http://localhost:8000/simulate-order",
            json=test_order,
            timeout=5
        )

        if response.status_code == 200:
            result = response.json()
            console.print("\n[bold green] Order dispatched successfully![/bold green]\n")

            # Create result table
            table = Table(title="Dispatch Result")
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Status", result.get("status", "N/A"))
            table.add_row("Drone ID", str(result.get("drone_id", "N/A")))
            table.add_row("Order ID", result.get("order_id", "N/A")[:30] + "...")
            table.add_row("ETA (minutes)", str(result.get("eta_minutes", "N/A")))
            table.add_row("Tracking Code", result.get("confirmation_code", "N/A"))

            console.print(table)
            return True
        else:
            console.print(f" Order failed: {response.status_code}", style="bold red")
            console.print(response.text)
            return False

    except requests.exceptions.ConnectionError:
        console.print(" Cannot connect to webhook server!", style="bold red")
        return False
    except Exception as e:
        console.print(f" Error: {e}", style="bold red")
        return False


def view_system_status():
    """View current system status"""
    console.print("\n[bold blue] System Status[/bold blue]\n")

    try:
        # Get orders
        orders_response = requests.get("http://localhost:8000/orders", timeout=2)
        orders_data = orders_response.json()

        # Get drones
        drones_response = requests.get("http://localhost:8000/drones", timeout=2)
        drones_data = drones_response.json()

        # Orders table
        if orders_data["total_orders"] > 0:
            orders_table = Table(title="Active Orders")
            orders_table.add_column("Order ID", style="cyan")
            orders_table.add_column("Facility", style="green")
            orders_table.add_column("Urgency", style="red")
            orders_table.add_column("Drone", style="yellow")
            orders_table.add_column("Status", style="blue")

            for order in orders_data["orders"]:
                orders_table.add_row(
                    order["order_id"][:10] + "...",
                    order["facility"],
                    order["urgency"],
                    f"Unit {order['drone_id']}",
                    order["status"]
                )

            console.print(orders_table)
        else:
            console.print(" No active orders")

        # Drones table
        console.print()
        drones_table = Table(title=f"Drone Fleet ({drones_data['available']} available)")
        drones_table.add_column("Drone ID", style="cyan")
        drones_table.add_column("Status", style="green")
        drones_table.add_column("Battery", style="yellow")
        drones_table.add_column("Location", style="blue")

        for drone_id, drone_info in drones_data["drones"].items():
            status_color = "green" if drone_info["status"] == "available" else "red"
            drones_table.add_row(
                f"Unit {drone_id}",
                f"[{status_color}]{drone_info['status']}[/{status_color}]",
                f"{drone_info['battery']}%",
                drone_info["location"]
            )

        console.print(drones_table)

        return True

    except Exception as e:
        console.print(f" Error fetching status: {e}", style="bold red")
        return False


def run_full_test():
    """Run all tests"""
    console.print(Panel.fit(
        "[bold cyan]Medical Drone Voice Agent - System Test[/bold cyan]\n"
        "Testing all components...",
        border_style="blue"
    ))

    tests = [
        ("Environment", test_environment),
        ("Webhook Server", test_webhook_server),
        ("Vapi Connection", test_vapi_connection),
    ]

    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
        time.sleep(0.5)

    # Summary
    console.print("\n" + "="*60)
    console.print("\n[bold blue] Test Summary[/bold blue]\n")

    summary_table = Table()
    summary_table.add_column("Test", style="cyan")
    summary_table.add_column("Result", style="bold")

    all_passed = True
    for test_name, passed in results:
        status = "[green] PASS[/green]" if passed else "[red] FAIL[/red]"
        summary_table.add_row(test_name, status)
        if not passed:
            all_passed = False

    console.print(summary_table)

    if all_passed:
        console.print("\n[bold green] All tests passed! Ready to test order simulation.[/bold green]")
        console.print("\nRun: [yellow]python voice_agent/test_system.py simulate[/yellow]")
    else:
        console.print("\n[bold red]  Some tests failed. Fix issues above before proceeding.[/bold red]")


def main():
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "env":
            test_environment()
        elif command == "server":
            test_webhook_server()
        elif command == "vapi":
            test_vapi_connection()
        elif command == "simulate":
            simulate_order()
        elif command == "status":
            view_system_status()
        elif command == "all":
            run_full_test()
        else:
            console.print(f"Unknown command: {command}", style="bold red")
            console.print("\nAvailable commands:")
            console.print("  env      - Test environment variables")
            console.print("  server   - Test webhook server")
            console.print("  vapi     - Test Vapi connection")
            console.print("  simulate - Simulate a medication order")
            console.print("  status   - View system status")
            console.print("  all      - Run all tests (default)")
    else:
        # Default: run all tests
        run_full_test()


if __name__ == "__main__":
    main()
