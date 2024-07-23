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
            ("Motor", "Blue"): 10,
            ("Motor", "Red"): 10,
            ("Battery", "Blue"): 10,
            ("Battery", "Red"): 10,
            ("Controller", "Blue"): 10,
            ("Controller", "Red"): 10,
            ("Throttle", "Blue"): 10,
            ("Throttle", "Red"): 10,
            ("Brake", "Blue"): 10,
            ("Brake", "Red"): 10,
            ("Frame", "Blue"): 10,
            ("Frame", "Red"): 10,
            ("Wheels", "Blue"): 40,
            ("Wheels", "Red"): 40,
            ("Charger", "Blue"): 10,
            ("Charger", "Red"): 10,
            ("Seat", "Blue"): 10,
            ("Seat", "Red"): 10,
            ("Suspension", "Blue"): 10,
            ("Suspension", "Red"): 10,
        }
        df = pd.DataFrame(list(parts.items()), columns=['Part_Color', 'Stock'])
        df[['Part', 'Color']] = pd.DataFrame(df['Part_Color'].tolist(), index=df.index)
        df = df.drop(columns=['Part_Color'])
        df.to_excel(excel_file_path, index=False)
    return df


# Function to save stock data to the Excel file
def save_stock_data(df):
    df.to_excel(excel_file_path, index=False)


# Function to decrement stock for custom number of rickshaws
def decrement_stock(df, num_rickshaws, color):
    required_parts = {
        "Motor": 1,
        "Battery": 1,
        "Controller": 1,
        "Throttle": 1,
        "Brake": 1,
        "Frame": 1,
        "Wheels": 4,
        "Charger": 1,
        "Seat": 1,
        "Suspension": 1
    }

    for part, qty in required_parts.items():
        part_stock = df.loc[(df['Part'] == part) & (df['Color'] == color), 'Stock'].values[0]
        if part_stock < qty * num_rickshaws:
            return df, False

    for part, qty in required_parts.items():
        df.loc[(df['Part'] == part) & (df['Color'] == color), 'Stock'] -= qty * num_rickshaws

    return df, True


# Function to increment stock
def increment_stock(df, selected_parts, quantity, color):
    if "All stock" in selected_parts:
        df.loc[df['Color'] == color, 'Stock'] += quantity
    else:
        for part in selected_parts:
            df.loc[(df['Part'] == part) & (df['Color'] == color), 'Stock'] += quantity
    return df


# Function to decrement custom stock
def decrement_custom_stock(df, selected_parts, quantity, color):
    if "All stock" in selected_parts:
        part_color = df.loc[df['Color'] == color, 'Stock']
        if (part_color >= quantity).all():
            df.loc[df['Color'] == color, 'Stock'] = part_color - quantity
        else:
            return df, False
    else:
        for part in selected_parts:
            part_stock = df.loc[(df['Part'] == part) & (df['Color'] == color), 'Stock'].values[0]
            if part_stock >= quantity:
                df.loc[(df['Part'] == part) & (df['Color'] == color), 'Stock'] -= quantity
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
color = st.selectbox('Select Rickshaw Color', ['Blue', 'Red'], key='rickshaw_color')
num_rickshaws = st.number_input('Number of Rickshaws to Record', min_value=1, step=1, key='num_rickshaws')
if st.button('Record Rickshaws Made'):
    df, success = decrement_stock(df, num_rickshaws, color)
    if success:
        save_stock_data(df)
        st.success("Stock updated successfully!")
    else:
        st.error(f"Not enough stock to make {num_rickshaws} {color} rickshaws!")
    st.dataframe(df)

# Section to increment stock
st.subheader("Increment Stock of Parts")
parts_list = ["All stock"] + df['Part'].unique().tolist()
increment_parts = st.multiselect('Select Parts to Increment', parts_list, key='increment_parts')
color = st.selectbox('Select Part Color', ['Blue', 'Red'], key='increment_color')
quantity_increment = st.number_input('Quantity to Add', min_value=1, step=1, key='increment_qty')
if st.button('Increment Stock'):
    df = increment_stock(df, increment_parts, quantity_increment, color)
    save_stock_data(df)
    st.success("Stock updated successfully!")
    st.dataframe(df)

# Section to decrement custom stock
st.subheader("Decrement Stock of Parts")
decrement_parts = st.multiselect('Select Parts to Decrement', parts_list, key='decrement_parts')
color = st.selectbox('Select Part Color', ['Blue', 'Red'], key='decrement_color')
quantity_decrement = st.number_input('Quantity to Remove', min_value=1, step=1, key='decrement_qty')
if st.button('Decrement Stock'):
    df, success = decrement_custom_stock(df, decrement_parts, quantity_decrement, color)
    if success:
        save_stock_data(df)
        st.success("Stock updated successfully!")
    else:
        st.error(f"Not enough stock to remove {quantity_decrement} of one or more selected parts!")
    st.dataframe(df)
