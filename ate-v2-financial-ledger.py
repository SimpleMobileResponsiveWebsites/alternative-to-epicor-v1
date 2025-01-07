import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import os

DATA_FILE = "transactions.csv"
COLUMNS = ['Date', 'Description', 'Category', 'Debit', 'Credit', 'Balance']
COLUMN_TYPES = {
    'Date': 'datetime64[ns]',
    'Description': 'string',
    'Category': 'string',
    'Debit': 'float64',
    'Credit': 'float64',
    'Balance': 'float64'
}

# Utility functions
def load_transactions():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df['Date'] = pd.to_datetime(df['Date'])
        return df.astype(COLUMN_TYPES)
    return pd.DataFrame(columns=COLUMNS)

def save_transactions(df):
    df.to_csv(DATA_FILE, index=False)

def recalculate_balance(df):
    df['Balance'] = (df['Credit'] - df['Debit']).cumsum()
    return df

def validate_upload(df):
    missing_cols = set(COLUMNS) - set(df.columns)
    if missing_cols:
        return False, f"Missing columns: {', '.join(missing_cols)}"
    try:
        df['Date'] = pd.to_datetime(df['Date'])
        return True, ""
    except Exception as e:
        return False, f"Invalid data format: {e}"

def main():
    st.set_page_config(page_title="Financial Ledger", layout="wide")

    # Load transactions
    if 'transactions' not in st.session_state:
        st.session_state.transactions = load_transactions()

    # Sidebar navigation
    page = st.sidebar.selectbox("Navigation", ["Dashboard", "Transactions", "Reports"])
    if page == "Dashboard":
        show_dashboard()
    elif page == "Transactions":
        show_transactions()
    else:
        show_reports()

def show_dashboard():
    st.title("Dashboard")
    transactions = st.session_state.transactions

    if transactions.empty:
        st.info("No transactions available.")
        return

    # Summary metrics
    st.metric("Total Balance", f"${transactions['Balance'].iloc[-1]:,.2f}")
    st.metric("Total Debits", f"${transactions['Debit'].sum():,.2f}")
    st.metric("Total Credits", f"${transactions['Credit'].sum():,.2f}")

    # Balance trend
    fig = px.line(transactions, x='Date', y='Balance', title='Balance Over Time')
    st.plotly_chart(fig, use_container_width=True)

def show_transactions():
    st.title("Transactions")
    transactions = st.session_state.transactions

    # Add transaction form
    with st.form("add_transaction"):
        date = st.date_input("Date", datetime.today())
        description = st.text_input("Description")
        category = st.selectbox("Category", ["Income", "Expenses", "Transfer", "Investment"])
        transaction_type = st.selectbox("Type", ["Debit", "Credit"])
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("Add Transaction")

        if submitted:
            if description:
                debit, credit = (amount, 0) if transaction_type == "Debit" else (0, amount)
                new_transaction = pd.DataFrame({
                    'Date': [date],
                    'Description': [description],
                    'Category': [category],
                    'Debit': [debit],
                    'Credit': [credit],
                    'Balance': [0]  # Placeholder for balance
                })
                st.session_state.transactions = pd.concat(
                    [transactions, recalculate_balance(new_transaction)], ignore_index=True
                )
                save_transactions(st.session_state.transactions)
                st.success("Transaction added successfully!")
            else:
                st.error("Description is required.")

    # Upload transactions
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        valid, error = validate_upload(df)
        if valid:
            st.session_state.transactions = recalculate_balance(df)
            save_transactions(st.session_state.transactions)
            st.success("Transactions uploaded successfully!")
        else:
            st.error(error)

    # Display transactions
    st.dataframe(transactions.style.format({
        'Date': lambda x: x.strftime('%Y-%m-%d'),
        'Debit': '${:,.2f}',
        'Credit': '${:,.2f}',
        'Balance': '${:,.2f}'
    }), use_container_width=True)

def show_reports():
    st.title("Reports")
    transactions = st.session_state.transactions

    if transactions.empty:
        st.warning("No data for reports.")
        return

    # Monthly summary
    transactions['Month'] = transactions['Date'].dt.to_period('M').astype(str)
    monthly_summary = transactions.groupby('Month').agg({'Debit': 'sum', 'Credit': 'sum'}).reset_index()
    fig = px.bar(monthly_summary, x='Month', y=['Debit', 'Credit'], barmode='group', title='Monthly Summary')
    st.plotly_chart(fig, use_container_width=True)

    # Category analysis
    category_summary = transactions.groupby('Category')['Debit'].sum().reset_index()
    fig = px.pie(category_summary, names='Category', values='Debit', title='Expenses by Category')
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
