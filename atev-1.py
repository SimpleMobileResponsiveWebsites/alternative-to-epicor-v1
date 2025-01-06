import streamlit as st

def main():
    st.title("Project Management Application")
    st.subheader("Explore Tools and Solutions for Efficient Project Management")

    # Sidebar for navigation
    menu = ["Home", "Product Categories", "Solution Guidance", "Contact Sales"]
    choice = st.sidebar.selectbox("Navigation", menu)

    if choice == "Home":
        home_page()
    elif choice == "Product Categories":
        product_categories()
    elif choice == "Solution Guidance":
        solution_guidance()
    elif choice == "Contact Sales":
        contact_sales()

def home_page():
    st.write("Welcome to the Project Management Application. This platform provides you with tools and solutions to take your business to the next level. Browse our product categories or get customized guidance to streamline your operations.")
    st.image("https://via.placeholder.com/800x400", caption="Streamline Your Business Processes", use_column_width=True)

def product_categories():
    st.header("Product Categories")
    st.write("Browse our comprehensive list of categories to find the perfect solution for your project management needs.")

    categories = {
        "AI-Powered Applications": "Amplify your team’s capabilities with AI tools built on industry-focused ERP and data platforms.",
        "Business Intelligence Software": "Centralize insights and transform them into actionable financial goals.",
        "Data Management and Integration": "Aggregate, normalize, and integrate data for higher productivity.",
        "Digital Commerce": "Boost sales and enhance customer experience with advanced commerce solutions.",
        "EDI Integrations": "Seamlessly connect your EDI data for streamlined operations.",
        "Enterprise Content Management": "Improve efficiency with integrated content management and automation tools.",
        "Enterprise Resource Planning (ERP)": "Strengthen supply chains and build better processes.",
        "Epicor Financials": "Modernize financial management with secure, cloud-based systems.",
        "Manufacturing Execution Software (MES)": "Boost accountability and responsiveness with real-time shop floor data.",
        "Retail Management Systems (RMS)": "Streamline operations and build customer loyalty.",
        "Service Management Software": "Deliver proactive, profitable customer service.",
        "Supply Chain Management": "Avoid disruptions with real-time supply chain insights.",
        "Time and Expense Management Mobile Apps": "Track tasks and expenses on the go."
    }

    for category, description in categories.items():
        with st.expander(category):
            st.write(description)


def solution_guidance():
    st.header("Solution Guidance")
    st.write("Let us guide you to the best solutions for your needs. Select the area you want to improve, and we’ll suggest relevant tools and strategies.")

    improvement_areas = ["Financial Management", "Supply Chain Efficiency", "Customer Experience", "Shop Floor Operations"]
    selected_area = st.selectbox("Select an Area to Improve", improvement_areas)

    if selected_area == "Financial Management":
        st.write("Epicor Financials and Business Intelligence Software are tailored to help you modernize and optimize financial operations.")
    elif selected_area == "Supply Chain Efficiency":
        st.write("Streamline your operations with our Supply Chain Management and EDI Integration solutions.")
    elif selected_area == "Customer Experience":
        st.write("Enhance customer loyalty and sales with Retail Management Systems and Digital Commerce tools.")
    elif selected_area == "Shop Floor Operations":
        st.write("Empower your workforce with Manufacturing Execution Software and real-time data capture tools.")

def contact_sales():
    st.header("Contact Sales")
    st.write("Have questions or need more information? Connect with our sales team for personalized assistance.")

    with st.form("contact_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        message = st.text_area("Message")
        submitted = st.form_submit_button("Submit")

        if submitted:
            st.success(f"Thank you {name}, your message has been sent! We will contact you at {email}.")

if __name__ == "__main__":
    main()
