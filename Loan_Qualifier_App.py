from pathlib import Path
import fire
import questionary

from qualifier.utils.fileio import load_csv, save_csv

from qualifier.utils.calculators import (
    calculate_monthly_debt_ratio,
    calculate_loan_to_value_ratio
)

from qualifier.filters.max_loan_size import filter_max_loan_size
from qualifier.filters.credit_score import filter_credit_score
from qualifier.filters.debt_to_income import filter_debt_to_income
from qualifier.filters.loan_to_value import filter_loan_to_value

def load_bank_data():
    """Ask for the file path to the latest banking data and load the CSV file.

    Returns:
        The bank data from the data rate sheet CSV file.
    """

    csvpath = questionary.text("Enter a file path to a rate-sheet (.csv):").ask()
    csvpath = Path(csvpath)

    return load_csv(csvpath)

def get_applicant_info():
    """Prompts the user for their loan information"""

    credit_score = questionary.text("What's your credit score?").ask()
    debt = questionary.text("What is your monthly debt?").ask()
    income = questionary.text("What is your monthly income?").ask()
    loan_amount = questionary.text("What is the total loan amount?").ask()
    home_value = questionary.text("What is the value of the home you are looking to purchase?").ask()

    credit_score = int(credit_score)
    debt = float(debt)
    income = float(income)
    loan_amount = float(loan_amount)
    home_value = float(home_value)

    return credit_score, debt, income, loan_amount, home_value

def find_qualifying_loans(bank_data, credit_score, debt, income, loan, home_value):
    """Determine which loans the user qualifies for.

    Loan qualification criteria is based on:
        - Credit Score
        - Loan Size
        - Debit to Income ratio (calculated)
        - Loan to Value ratio (calculated)

    Args:
        bank_data (list): A list of bank data.
        credit_score (int): The applicant's current credit score.
        debt (float): The applicant's total monthly debt payments.
        income (float): The applicant's total monthly income.
        loan (float): The total loan amount applied for.
        home_value (float): The estimated home value.

    Returns:
        A list of the banks willing to underwrite the loan.

    """
    # Calculate the monthly debt ratio
    monthly_debt_ratio = calculate_monthly_debt_ratio(debt, income)
    print(f"The monthly debt to income ratio is {monthly_debt_ratio:.02f}")

    # Calculate loan to value ratio
    loan_to_value_ratio = calculate_loan_to_value_ratio(loan, home_value)
    print(f"The loan to value ratio is {loan_to_value_ratio:.02f}.")

    # Run qualification filters
    bank_data_filtered = filter_max_loan_size(loan, bank_data)
    bank_data_filtered = filter_credit_score(credit_score, bank_data_filtered)
    bank_data_filtered = filter_debt_to_income(monthly_debt_ratio, bank_data_filtered)
    bank_data_filtered = filter_loan_to_value(loan_to_value_ratio, bank_data_filtered)

    print(f"Found {len(bank_data_filtered)} qualifying loans")

    return bank_data_filtered

def save_qualifying_loans(qualifying_loans):
    
    """User dialog"""
     # Ask the user if they want to save the list of loans - Acceptance Criteria #1 and #3
    user_save_decision = questionary.confirm("Do you want to save the list of qualifying loans?").ask()
        
    if user_save_decision == True:

        # If the user does not qualify for any loans, program notifies user and exits - Acceptance Criteria #2
        if not qualifying_loans:
            print("You do not currently qualify for any available loans.")
        # If the user qualifies for loans and chooses to save the file, the program asks for the file path - Acceptance Criteria #4
        else:
            user_save_path = questionary.path("Where do you want to save the list of qualifying loans? (enter file path that ends in .csv)").ask()
            save_csv(qualifying_loans, user_save_path)
  

    else:

        # If the user does not choose to save the file, the program checks to see if the user qualified for any loans, if not then informs the user and exits
        if not qualifying_loans:
            print("You do not currently qualify for any available loans.")
            
        # If the user does not choose to save the file, but qualifies for loans, the program will return the list of qualifying loans in a table format
        else:
            print(f"Here are the loans you qualify for:")
            print(tabulate(qualifying_loans, headers = [
                "Loan Name", 
                "Max Loan Amounts", 
                "Loan to Value Ratio", 
                "Debt to Income Ratio",
                "Credit Score",
                "Interest Rate"
            ]))

def run():
    """The main function for running the script."""

    # Load the latest Bank data
    bank_data = load_bank_data()

    # Get the applicant's information
    credit_score, debt, income, loan_amount, home_value = get_applicant_info()

    # Find qualifying loans
    qualifying_loans = find_qualifying_loans(
        bank_data, credit_score, debt, income, loan_amount, home_value
    )

    # Save qualifying loans
    save_qualifying_loans(qualifying_loans)


if __name__ == "__main__":
    fire.Fire(run)
