import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

def main():
    st.set_page_config(page_title="Financial Ledger", layout="wide")
    
    # Sidebar for navigation
    st.sidebar.title("Financial Ledger")
    page = st.sidebar.selectbox("Navigation", ["Dashboard", "Transactions", "Reports"])
    
    # Initialize session state for storing transactions
    if 'transactions' not in st.session_state:
        st.session_state.transactions = pd.DataFrame(
            columns=['Date', 'Description', 'Category', 'Debit', 'Credit', 'Balance']
        )

    if page == "Dashboard":
        show_dashboard()
    elif page == "Transactions":
        show_transactions()
    else:
        show_reports()

def show_dashboard():
    st.title("Financial Dashboard")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Balance",
            value=f"${st.session_state.transactions['Balance'].iloc[-1] if len(st.session_state.transactions) > 0 else 0:,.2f}"
        )
    
    with col2:
        total_debits = st.session_state.transactions['Debit'].sum()
        st.metric(label="Total Debits", value=f"${total_debits:,.2f}")
    
    with col3:
        total_credits = st.session_state.transactions['Credit'].sum()
        st.metric(label="Total Credits", value=f"${total_credits:,.2f}")
    
    # Transaction trends
    if len(st.session_state.transactions) > 0:
        st.subheader("Balance Trend")
        fig = px.line(
            st.session_state.transactions,
            x='Date',
            y='Balance',
            title='Balance Over Time'
        )
        st.plotly_chart(fig, use_container_width=True)

def show_transactions():
    st.title("Transaction Management")
    
    # Transaction input form
    with st.form("transaction_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date = st.date_input("Date", datetime.today())
            description = st.text_input("Description")
        
        with col2:
            category = st.selectbox(
                "Category",
                ["Income", "Expenses", "Transfer", "Investment"]
            )
        
        with col3:
            transaction_type = st.selectbox("Type", ["Debit", "Credit"])
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        
        submitted = st.form_submit_button("Add Transaction")
        
        if submitted:
            debit = amount if transaction_type == "Debit" else 0
            credit = amount if transaction_type == "Credit" else 0
            
            # Calculate new balance
            current_balance = (
                st.session_state.transactions['Balance'].iloc[-1]
                if len(st.session_state.transactions) > 0
                else 0
            )
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
            
            st.session_state.transactions = pd.concat(
                [st.session_state.transactions, new_transaction],
                ignore_index=True
            )
            st.success("Transaction added successfully!")

    # Display transactions table
    st.subheader("Transaction History")
    st.dataframe(
        st.session_state.transactions.style.format({
            'Debit': '${:,.2f}',
            'Credit': '${:,.2f}',
            'Balance': '${:,.2f}'
        }),
        use_container_width=True
    )

def show_reports():
    st.title("Financial Reports")
    
    if len(st.session_state.transactions) > 0:
        # Category breakdown
        st.subheader("Category Analysis")
        fig_category = px.pie(
            st.session_state.transactions,
            values='Debit',
            names='Category',
            title='Expenses by Category'
        )
        st.plotly_chart(fig_category, use_container_width=True)
        
        # Monthly trends
        st.subheader("Monthly Trends")
        monthly_data = st.session_state.transactions.copy()
        monthly_data['Month'] = pd.to_datetime(monthly_data['Date']).dt.strftime('%Y-%m')
        monthly_summary = monthly_data.groupby('Month').agg({
            'Debit': 'sum',
            'Credit': 'sum'
        }).reset_index()
        
        fig_monthly = px.bar(
            monthly_summary,
            x='Month',
            y=['Debit', 'Credit'],
            title='Monthly Debit vs Credit',
            barmode='group'
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
    else:
        st.info("No transactions available for reporting.")

if __name__ == "__main__":
    main()
