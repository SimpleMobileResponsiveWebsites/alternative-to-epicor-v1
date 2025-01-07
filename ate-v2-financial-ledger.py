import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import os
import io

# Persistent storage for transactions
DATA_FILE = "transactions.csv"

# Column definitions with their types
COLUMN_TYPES = {
    'Date': 'datetime64[ns]',
    'Description': 'string',
    'Category': 'string',
    'Debit': 'float64',
    'Credit': 'float64',
    'Balance': 'float64'
}

# Load or initialize transaction data
def load_transactions():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        # Convert columns to proper types
        for col, dtype in COLUMN_TYPES.items():
            if col == 'Date':
                df[col] = pd.to_datetime(df[col])
            else:
                df[col] = df[col].astype(dtype)
        return df
    else:
        return pd.DataFrame(columns=COLUMN_TYPES.keys())

# Save transaction data
def save_transactions(transactions):
    transactions.to_csv(DATA_FILE, index=False)

# Validate uploaded file
def validate_upload(df):
    errors = []
    
    # Check for required columns
    missing_cols = set(COLUMN_TYPES.keys()) - set(df.columns)
    if missing_cols:
        errors.append(f"Missing required columns: {', '.join(missing_cols)}")
        return False, errors
    
    # Validate data types
    try:
        for col, dtype in COLUMN_TYPES.items():
            if col == 'Date':
                df[col] = pd.to_datetime(df[col])
            else:
                df[col] = df[col].astype(dtype)
    except Exception as e:
        errors.append(f"Error converting data types: {str(e)}")
        return False, errors
    
    return True, errors

def recalculate_balance(df):
    balance = 0
    for idx in range(len(df)):
        balance += (df.iloc[idx]['Credit'] - df.iloc[idx]['Debit'])
        df.iloc[idx, df.columns.get_loc('Balance')] = balance
    return df

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
    
    if st.session_state.transactions.empty:
        st.info("No transactions available. Please add transactions to view the dashboard.")
        return

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
    st.subheader("Balance Trend")
    try:
        fig = px.line(
            transactions,
            x='Date',
            y='Balance',
            title='Balance Over Time',
            labels={'Balance': 'Balance ($)', 'Date': 'Date'}
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error displaying balance trend: {str(e)}")

def show_transactions():
    st.title("Transaction Management")

    # Add tabs for different transaction management features
    tab1, tab2, tab3 = st.tabs(["Add Transaction", "Remove Transactions", "Upload Transactions"])
    
    with tab1:
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
                if not description:
                    st.error("Please enter a description")
                    return

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

    with tab2:
        st.subheader("Remove Transactions")
        if not st.session_state.transactions.empty:
            # Allow multiple selection of transactions to remove
            transactions_to_remove = st.multiselect(
                "Select transactions to remove",
                range(len(st.session_state.transactions)),
                format_func=lambda x: f"{st.session_state.transactions.iloc[x]['Date'].strftime('%Y-%m-%d')} - {st.session_state.transactions.iloc[x]['Description']} - ${st.session_state.transactions.iloc[x]['Debit'] or st.session_state.transactions.iloc[x]['Credit']:,.2f}"
            )
            
            if st.button("Remove Selected Transactions"):
                if transactions_to_remove:
                    # Remove selected transactions
                    st.session_state.transactions = st.session_state.transactions.drop(transactions_to_remove).reset_index(drop=True)
                    # Recalculate balances
                    st.session_state.transactions = recalculate_balance(st.session_state.transactions)
                    save_transactions(st.session_state.transactions)
                    st.success(f"Removed {len(transactions_to_remove)} transaction(s)")
                    st.rerun()
        else:
            st.info("No transactions available to remove")

    with tab3:
        st.subheader("Upload Transactions")
        st.markdown("""
        Please ensure your CSV file has the following columns:
        - Date (YYYY-MM-DD)
        - Description (text)
        - Category (text)
        - Debit (number)
        - Credit (number)
        - Balance (number)
        """)
        
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            try:
                # Read the uploaded file
                df = pd.read_csv(uploaded_file)
                
                # Validate the uploaded data
                is_valid, errors = validate_upload(df)
                
                if is_valid:
                    # Recalculate balances
                    df = recalculate_balance(df)
                    
                    # Update transactions
                    st.session_state.transactions = df
                    save_transactions(st.session_state.transactions)
                    st.success("Transactions uploaded successfully!")
                else:
                    for error in errors:
                        st.error(error)
            except Exception as e:
                st.error(f"Error uploading file: {str(e)}")

    # Display transactions table
    st.subheader("Transaction History")
    transactions = st.session_state.transactions
    if not transactions.empty:
        st.dataframe(
            transactions.style.format({
                'Date': lambda x: x.strftime('%Y-%m-%d'),
                'Debit': '${:,.2f}',
                'Credit': '${:,.2f}',
                'Balance': '${:,.2f}'
            }),
            use_container_width=True
        )
    else:
        st.info("No transactions available")

def show_reports():
    st.title("Financial Reports")
    
    # Check if there are any transactions
    if len(st.session_state.transactions) == 0:
        st.warning("No transactions available for reporting.")
        return
    
    try:
        monthly_data = st.session_state.transactions.copy()
        
        # Create month column
        monthly_data['Month'] = monthly_data['Date'].dt.strftime('%Y-%m')
        
        # Calculate monthly summaries
        monthly_summary = monthly_data.groupby('Month').agg({
            'Debit': 'sum',
            'Credit': 'sum'
        }).reset_index()
        
        # Convert wide to long format for plotting
        monthly_plot_data = pd.melt(
            monthly_summary,
            id_vars=['Month'],
            value_vars=['Debit', 'Credit'],
            var_name='Type',
            value_name='Amount'
        )
        
        # Display monthly trends
        st.subheader("Monthly Trends")
        fig_monthly = px.bar(
            monthly_plot_data,
            x='Month',
            y='Amount',
            color='Type',
            title='Monthly Debit vs Credit',
            labels={'Amount': 'Amount ($)', 'Month': 'Month'},
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
        
        # Category breakdown
        st.subheader("Category Analysis")
        category_summary = monthly_data.groupby('Category')['Debit'].sum().reset_index()
        if not category_summary.empty:
            fig_category = px.pie(
                category_summary,
                values='Debit',
                names='Category',
                title='Expenses by Category'
            )
            st.plotly_chart(fig_category, use_container_width=True)
            
        # Export functionality
        st.subheader("Export Data")
        if st.button("Export to CSV"):
            try:
                monthly_data.to_csv("transaction_report.csv", index=False)
                st.success("Report exported successfully!")
            except Exception as e:
                st.error(f"Error exporting data: {e}")
                
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        return

if __name__ == "__main__":
    main()
