#!/bin/bash

# Black Box Challenge - Reimbursement Calculation Implementation
# This script calculates travel reimbursements based on reverse-engineered patterns
# Usage: ./run.sh <trip_duration_days> <miles_traveled> <total_receipts_amount>

python3 calculate_reimbursement.py "$1" "$2" "$3" 