import streamlit as st
import pandas as pd
from PIL import Image

# Define the Excel file path
excel_file_path = 'stock.xlsx'


# Function to load stock data from the Excel file
def load_stock_data():
    try:
        df = pd.read_excel(excel_file_path)
    except FileNotFoundError:
        # If the Excel file does not exist, create a new one with initial stock
        parts = {
            "Motor": 10,
            "Battery": 10,
            "Controller": 10,
            "Throttle": 10,
            "Brake": 10,
            "Frame": 10,
            "Wheels": 10,
            "Charger": 10,
            "Seat": 10,
            "Suspension": 10
        }
        df = pd.DataFrame(list(parts.items()), columns=['Part', 'Stock'])
        df.to_excel(excel_file_path, index=False)
    return df


# Function to save stock data to the Excel file
def save_stock_data(df):
    df.to_excel(excel_file_path, index=False)


# Function to decrement stock for custom number of rickshaws
def decrement_stock(df, selected_model):
    if selected_model:
        model_parts = {
            "Model A": {
                "Motor": 1,
                "Battery": 2,
                "Controller": 1,
                "Throttle": 1,
                "Brake": 2,
                "Frame": 1,
                "Wheels": 3,
                "Charger": 1,
                "Seat": 1,
                "Suspension": 1
            },
            "Model B": {
                "Motor": 1,
                "Battery": 1,
                "Controller": 1,
                "Throttle": 1,
                "Brake": 1,
                "Frame": 1,
                "Wheels": 4,
                "Charger": 1,
                "Seat": 1,
                "Suspension": 2
            }
        }

        parts_needed = model_parts[selected_model]
        for part, qty in parts_needed.items():
            if df.loc[df['Part'] == part, 'Stock'].values[0] < qty:
                return df, False
            df.loc[df['Part'] == part, 'Stock'] -= qty
        return df, True
    return df, False


# Load stock data
df = load_stock_data()

# Streamlit app
st.set_page_config(page_title="Electric Rickshaw Spare Parts Management", page_icon=":rickshaw:", layout="wide")

# Custom CSS styling
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    h1 {
        color: #007bff;
    }
    h2, h3 {
        color: #6c757d;
    }
    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 5px;
        font-size: 16px;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        color: white;
    }
    .stNumberInput>div>div>input {
        border-radius: 5px;
        border: 2px solid #007bff;
    }
    .stDataFrame {
        border: 2px solid #007bff;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Header section
st.image("https://www.bybyerickshaw.com/images/logo.png", width=200)
st.title("Electric Rickshaw Spare Parts Management")

# Display current stock
st.subheader("Current Stock of Parts")
st.dataframe(df)

# Section to decrement stock for custom number of rickshaws
st.subheader("Record New Rickshaws")
model_selection = st.selectbox('Select E-Rickshaw Model', ["Model A", "Model B"])
num_rickshaws = st.number_input('Number of Rickshaws to Record', min_value=1, step=1, key='num_rickshaws')
if st.button('Record Rickshaws Made'):
    df, success = decrement_stock(df, model_selection)
    if success:
        save_stock_data(df)
        st.success("Stock updated successfully!")
    else:
        st.error(f"Not enough stock to make {num_rickshaws} rickshaws!")
    st.dataframe(df)

# Section to increment stock
st.subheader("Increment Stock of Parts")
parts_list = ["All stock"] + df['Part'].tolist()
increment_parts = st.multiselect('Select Parts to Increment', parts_list)
quantity_increment = st.number_input('Quantity to Add', min_value=1, step=1, key='increment_qty')
if st.button('Increment Stock'):
    df = increment_stock(df, increment_parts, quantity_increment)
    save_stock_data(df)
    st.success("Stock updated successfully!")
    st.dataframe(df)

# Section to decrement custom stock
st.subheader("Decrement Stock of Parts")
decrement_parts = st.multiselect('Select Parts to Decrement', parts_list)
quantity_decrement = st.number_input('Quantity to Remove', min_value=1, step=1, key='decrement_qty')
if st.button('Decrement Stock'):
    df, success = decrement_custom_stock(df, decrement_parts, quantity_decrement)
    if success:
        save_stock_data(df)
        st.success("Stock updated successfully!")
    else:
        st.error(f"Not enough stock to remove {quantity_decrement} of one or more selected parts!")
    st.dataframe(df)
