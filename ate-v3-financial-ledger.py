import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import os

DATA_FILE = "transactions.csv"

COLUMN_TYPES = {
    'Date': 'datetime64[ns]',
    'Description': 'string',
    'Category': 'string',
    'Debit': 'float64',
    'Credit': 'float64',
    'Balance': 'float64'
}

# Load transactions
@st.cache_data
def load_transactions():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df = df.astype(COLUMN_TYPES, errors='ignore')
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        return df
    return pd.DataFrame(columns=COLUMN_TYPES.keys())

# Save transactions
def save_transactions(transactions):
    transactions.to_csv(DATA_FILE, index=False)

# Recalculate balance
def recalculate_balance(df):
    df['Balance'] = df['Credit'].cumsum() - df['Debit'].cumsum()
    return df

def main():
    st.set_page_config(page_title="Financial Ledger", layout="wide")
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Transactions", "Reports"])

    if 'transactions' not in st.session_state:
        st.session_state.transactions = load_transactions()

    if page == "Dashboard":
        show_dashboard()
    elif page == "Transactions":
        show_transactions()
    elif page == "Reports":
        show_reports()

def show_dashboard():
    st.title("Dashboard")
    transactions = st.session_state.transactions
    if transactions.empty:
        st.info("No transactions available.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Balance", f"${transactions['Balance'].iloc[-1]:,.2f}")
    with col2:
        st.metric("Total Debits", f"${transactions['Debit'].sum():,.2f}")
    with col3:
        st.metric("Total Credits", f"${transactions['Credit'].sum():,.2f}")

    st.subheader("Balance Over Time")
    fig = px.line(transactions, x='Date', y='Balance', title='Balance Over Time')
    st.plotly_chart(fig, use_container_width=True)

def show_transactions():
    st.title("Manage Transactions")
    tab1, tab2 = st.tabs(["Add Transactions", "View Transactions"])

    with tab1:
        with st.form("add_transaction_form"):
            date = st.date_input("Date", datetime.today())
            description = st.text_input("Description")
            category = st.selectbox("Category", ["Income", "Expense", "Investment", "Other"])
            transaction_type = st.selectbox("Type", ["Debit", "Credit"])
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
            submitted = st.form_submit_button("Add Transaction")

            if submitted:
                debit, credit = (amount, 0) if transaction_type == "Debit" else (0, amount)
                new_transaction = pd.DataFrame({
                    'Date': [date],
                    'Description': [description],
                    'Category': [category],
                    'Debit': [debit],
                    'Credit': [credit],
                    'Balance': [0]
                })
                st.session_state.transactions = pd.concat([st.session_state.transactions, new_transaction], ignore_index=True)
                st.session_state.transactions = recalculate_balance(st.session_state.transactions)
                save_transactions(st.session_state.transactions)
                st.success("Transaction added successfully!")

    with tab2:
        transactions = st.session_state.transactions
        if not transactions.empty:
            # Display the transactions with delete button inline with the record
            for index, row in transactions.iterrows():
                col1, col2, col3, col4 = st.columns([3, 4, 2, 1])
                with col1:
                    st.write(row['Date'].strftime('%Y-%m-%d'))
                with col2:
                    st.write(f"{row['Description']} - {row['Category']}")
                with col3:
                    # Display debit/credit as needed
                    st.write(f"${row['Debit'] if row['Debit'] > 0 else row['Credit']:.2f}")
                with col4:
                    # Add delete button in the last column
                    delete_button = st.button(f"Delete", key=f"delete_{index}")

                    if delete_button:
                        # Remove transaction from DataFrame
                        st.session_state.transactions = st.session_state.transactions.drop(index)
                        st.session_state.transactions = recalculate_balance(st.session_state.transactions)
                        save_transactions(st.session_state.transactions)
                        st.success("Transaction deleted successfully!")
                        break  # Exit the loop after deletion to avoid errors

            # Display the updated DataFrame
            st.dataframe(transactions.style.format({
                'Date': lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '',
                'Debit': '${:,.2f}',
                'Credit': '${:,.2f}',
                'Balance': '${:,.2f}'
            }), use_container_width=True)
        else:
            st.info("No transactions available.")

def show_reports():
    st.title("Reports")
    transactions = st.session_state.transactions
    if transactions.empty:
        st.warning("No transactions available for reports.")
        return

    # Ensure 'Date' column is in datetime format
    if not pd.api.types.is_datetime64_any_dtype(transactions['Date']):
        transactions['Date'] = pd.to_datetime(transactions['Date'], errors='coerce')

    # Drop rows with invalid dates (NaT)
    transactions = transactions.dropna(subset=['Date'])

    # Extract the month as a period
    transactions['Month'] = transactions['Date'].dt.to_period('M').astype(str)

    # Monthly summary report
    monthly_summary = transactions.groupby('Month').agg({
        'Debit': 'sum',
        'Credit': 'sum'
    }).reset_index()

    st.subheader("Monthly Trends")
    fig = px.bar(monthly_summary, x='Month', y=['Debit', 'Credit'], barmode='group', title='Monthly Debit vs Credit')
    st.plotly_chart(fig, use_container_width=True)

    # Category breakdown report
    st.subheader("Category Breakdown")
    category_summary = transactions.groupby('Category')['Debit'].sum().reset_index()
    fig = px.pie(category_summary, values='Debit', names='Category', title='Expenses by Category')
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
