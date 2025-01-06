import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import os

# Persistent storage for transactions
DATA_FILE = "transactions.csv"

# Load or initialize transaction data
def load_transactions():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=['Date', 'Description', 'Category', 'Debit', 'Credit', 'Balance'])

# Save transaction data
def save_transactions(transactions):
    transactions.to_csv(DATA_FILE, index=False)

def main():
    st.set_page_config(page_title="Financial Ledger", layout="wide")

    # Sidebar for navigation
    st.sidebar.title("Financial Ledger")
    page = st.sidebar.selectbox("Navigation", ["Dashboard", "Transactions", "Reports"])

    # Load transactions into session state
    if 'transactions' not in st.session_state:
        st.session_state.transactions = load_transactions()

    if page == "Dashboard":
        show_dashboard()
    elif page == "Transactions":
        show_transactions()
    else:
        show_reports()

def show_dashboard():
    st.title("Financial Dashboard")

    transactions = st.session_state.transactions

    # Summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        total_balance = transactions['Balance'].iloc[-1] if not transactions.empty else 0
        st.metric(label="Total Balance", value=f"${total_balance:,.2f}")

    with col2:
        total_debits = transactions['Debit'].sum()
        st.metric(label="Total Debits", value=f"${total_debits:,.2f}")

    with col3:
        total_credits = transactions['Credit'].sum()
        st.metric(label="Total Credits", value=f"${total_credits:,.2f}")

    # Transaction trends
    if not transactions.empty:
        st.subheader("Balance Trend")
        fig = px.line(transactions, x='Date', y='Balance', title='Balance Over Time')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No transactions available to display.")

def show_transactions():
    st.title("Transaction Management")

    # Transaction input form
    with st.form("transaction_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            date = st.date_input("Date", datetime.today())
            description = st.text_input("Description")

        with col2:
            category = st.selectbox("Category", ["Income", "Expenses", "Transfer", "Investment"])

        with col3:
            transaction_type = st.selectbox("Type", ["Debit", "Credit"])
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")

        submitted = st.form_submit_button("Add Transaction")

        if submitted:
            debit = amount if transaction_type == "Debit" else 0
            credit = amount if transaction_type == "Credit" else 0

            # Calculate new balance
            transactions = st.session_state.transactions
            current_balance = transactions['Balance'].iloc[-1] if not transactions.empty else 0
            new_balance = current_balance + credit - debit

            # Add new transaction
            new_transaction = pd.DataFrame({
                'Date': [date],
                'Description': [description],
                'Category': [category],
                'Debit': [debit],
                'Credit': [credit],
                'Balance': [new_balance]
            })

            st.session_state.transactions = pd.concat([transactions, new_transaction], ignore_index=True)
            save_transactions(st.session_state.transactions)
            st.success("Transaction added successfully!")

    # Display transactions table
    st.subheader("Transaction History")
    transactions = st.session_state.transactions
    st.dataframe(transactions.style.format({'Debit': '${:,.2f}', 'Credit': '${:,.2f}', 'Balance': '${:,.2f}'}), use_container_width=True)

def show_reports():
    st.title("Financial Reports")

    transactions = st.session_state.transactions

    if not transactions.empty:
        # Filter options
        st.subheader("Filter Transactions")
        date_range = st.date_input("Select Date Range", [datetime(2023, 1, 1), datetime.today()])

        filtered_transactions = transactions[
            (pd.to_datetime(transactions['Date']) >= pd.to_datetime(date_range[0])) &
            (pd.to_datetime(transactions['Date']) <= pd.to_datetime(date_range[1]))
        ]

        # Category breakdown
        st.subheader("Category Analysis")
        fig_category = px.pie(
            filtered_transactions, values='Debit', names='Category', title='Expenses by Category'
        )
        st.plotly_chart(fig_category, use_container_width=True)

        # Monthly trends
        st.subheader("Monthly Trends")
        filtered_transactions['Month'] = pd.to_datetime(filtered_transactions['Date']).dt.strftime('%Y-%m')
        monthly_summary = filtered_transactions.groupby('Month').agg({'Debit': 'sum', 'Credit': 'sum'}).reset_index()

        fig_monthly = px.bar(
            monthly_summary, x='Month', y=['Debit', 'Credit'], title='Monthly Debit vs Credit', barmode='group'
        )
        st.plotly_chart(fig_monthly, use_container_width=True)

        # Export option
        st.subheader("Export Filtered Transactions")
        if st.button("Export to CSV"):
            filtered_transactions.to_csv("filtered_transactions.csv", index=False)
            st.success("Filtered transactions exported successfully!")
    else:
        st.info("No transactions available for reporting.")

if __name__ == "__main__":
    main()
