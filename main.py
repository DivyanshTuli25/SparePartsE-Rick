import streamlit as st
import pandas as pd
from PIL import Image
# Define the Excel file path
excel_file_path = 'stock.xlsx'

# Define parts requirements for each e-rickshaw model
model_parts_requirements = {
    "Model A": {
        "Motor": 1,
        "Battery": 1,
        "Controller": 1,
        "Throttle": 1,
        "Brake": 1,
        "Frame": 1,
        "Wheels": 2,
        "Charger": 1,
        "Seat": 1,
        "Suspension": 1
    },
    "Model B": {
        "Motor": 1,
        "Battery": 2,
        "Controller": 1,
        "Throttle": 1,
        "Brake": 2,
        "Frame": 1,
        "Wheels": 3,
        "Charger": 1,
        "Seat": 1,
        "Suspension": 2
    }
}


# Function to load stock data from the Excel file
def load_stock_data():
    try:
        df = pd.read_excel(excel_file_path)
    except FileNotFoundError:
        # If the Excel file does not exist, create a new one with initial stock
        parts = {
            "Motor": [10, 10],
            "Battery": [10, 10],
            "Controller": [10, 10],
            "Throttle": [10, 10],
            "Brake": [10, 10],
            "Frame": [10, 10],
            "Wheels": [10, 10],
            "Charger": [10, 10],
            "Seat": [10, 10],
            "Suspension": [10, 10]
        }
        df = pd.DataFrame(parts).T.reset_index()
        df.columns = ['Part', 'Stock_Blue', 'Stock_Red']
        df.to_excel(excel_file_path, index=False)
    return df


# Function to save stock data to the Excel file
def save_stock_data(df):
    df.to_excel(excel_file_path, index=False)


# Function to decrement stock for custom number of rickshaws
def decrement_stock(df, num_rickshaws, color, model):
    stock_column = f'Stock_{color}'
    requirements = model_parts_requirements[model]

    for part, qty in requirements.items():
        if (df.loc[df['Part'] == part, stock_column] < qty * num_rickshaws).any():
            return df, False

    for part, qty in requirements.items():
        df.loc[df['Part'] == part, stock_column] -= qty * num_rickshaws

    return df, True


# Function to increment stock
def increment_stock(df, selected_parts, quantity, color):
    stock_column = f'Stock_{color}'
    if "All stock" in selected_parts:
        df[stock_column] += quantity
    else:
        for part in selected_parts:
            df.loc[df['Part'] == part, stock_column] += quantity
    return df


# Function to decrement custom stock
def decrement_custom_stock(df, selected_parts, quantity, color):
    stock_column = f'Stock_{color}'
    if "All stock" in selected_parts:
        if (df[stock_column] >= quantity).all():
            df[stock_column] -= quantity
        else:
            return df, False
    else:
        for part in selected_parts:
            if df.loc[df['Part'] == part, stock_column].values[0] >= quantity:
                df.loc[df['Part'] == part, stock_column] -= quantity
            else:
                return df, False
    return df, True


# Load stock data
df = load_stock_data()

# Streamlit app
st.set_page_config(page_title="Electric Rickshaw Spare Parts Management", page_icon=":rickshaw:", layout="wide")

# Custom CSS styling
st.markdown("""
    <style>
    .main {
        background-color: #85C227;
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
model = st.selectbox('Select Rickshaw Model', ['Model A', 'Model B'], key='model')
num_rickshaws = st.number_input('Number of Rickshaws to Record', min_value=1, step=1, key='num_rickshaws')
rickshaw_color = st.selectbox('Select Rickshaw Color', ['Blue', 'Red'], key='rickshaw_color')
if st.button('Record Rickshaws Made'):
    df, success = decrement_stock(df, num_rickshaws, rickshaw_color, model)
    if success:
        save_stock_data(df)
        st.success(f"Stock updated successfully for {num_rickshaws} {rickshaw_color} rickshaw(s) of {model}!")
    else:
        st.error(f"Not enough stock to make {num_rickshaws} {rickshaw_color} rickshaw(s) of {model}!")
    st.dataframe(df)

# Section to increment stock
st.subheader("Increment Stock of Parts")
parts_list = ["All stock"] + df['Part'].tolist()
increment_parts = st.multiselect('Select Parts to Increment', parts_list)
quantity_increment = st.number_input('Quantity to Add', min_value=1, step=1, key='increment_qty')
increment_color = st.selectbox('Select Part Color', ['Blue', 'Red'], key='increment_color')
if st.button('Increment Stock'):
    df = increment_stock(df, increment_parts, quantity_increment, increment_color)
    save_stock_data(df)
    st.success(f"Stock updated successfully for {increment_color} parts!")
    st.dataframe(df)

# Section to decrement custom stock
st.subheader("Decrement Stock of Parts")
decrement_parts = st.multiselect('Select Parts to Decrement', parts_list)
quantity_decrement = st.number_input('Quantity to Remove', min_value=1, step=1, key='decrement_qty')
decrement_color = st.selectbox('Select Part Color', ['Blue', 'Red'], key='decrement_color')
if st.button('Decrement Stock'):
    df, success = decrement_custom_stock(df, decrement_parts, quantity_decrement, decrement_color)
    if success:
        save_stock_data(df)
        st.success(f"Stock updated successfully for {decrement_color} parts!")
    else:
        st.error(f"Not enough stock to remove {quantity_decrement} of one or more selected {decrement_color} parts!")
    st.dataframe(df)
