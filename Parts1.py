import streamlit as st
import pandas as pd
from PIL import Image

# Define the Excel file paths
stock_file_path = 'Parts.xlsx'
parts_file_path = 'Parts.xlsx'

# Function to load parts requirements from the Excel file
def load_parts_requirements():
    df = pd.read_excel(parts_file_path)
    model_parts_requirements = {}
    for model in df.columns[4:]:  # Assuming 'Parts' is the first column and models start from the second column
        model_parts_requirements[model] = df.set_index('Parts')[model].to_dict()
    return model_parts_requirements

# Function to load stock data from the Excel file
def load_stock_data():
    try:
        df = pd.read_excel(stock_file_path)
    except FileNotFoundError:
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
        df = pd.DataFrame(parts.items(), columns=['Parts', 'Stock'])
        df.to_excel(stock_file_path, index=False)
    return df

# Function to save stock data to the Excel file
def save_stock_data(df):
    df.to_excel(stock_file_path, index=False)

# Function to calculate how many models can be made with the current stock
def calculate_producible(df, parts_requirements):
    producible_dict = {}
    for model, requirements in parts_requirements.items():
        min_producible = float('inf')
        for part, qty in requirements.items():
            stock_qty = df.loc[df['Parts'] == part, 'Stock'].values[0]
            if qty > 0:  # Avoid division by zero
                producible = stock_qty // qty
                if producible < min_producible:
                    min_producible = producible
        df[model + 's that can be made'] = min_producible
        producible_dict[model] = min_producible
    return df, producible_dict

# Function to find parts needed for replenishment
def find_parts_to_replenish(df, parts_requirements, producible_dict, threshold=100):
    replenishment_list = []
    for model, producible_qty in producible_dict.items():
        if producible_qty < threshold:
            for part, qty in parts_requirements[model].items():
                stock_qty = df.loc[df['Parts'] == part, 'Stock'].values[0]
                required_qty = (threshold - producible_qty) * qty
                if required_qty > 0:
                    replenishment_list.append((model, part, required_qty))
    return replenishment_list

# Function to decrement stock for custom number of rickshaws
def decrement_stock(df, num_rickshaws, model, parts_requirements):
    requirements = parts_requirements[model]

    for part, qty in requirements.items():
        if (df.loc[df['Parts'] == part, 'Stock'] < qty * num_rickshaws).any():
            return df, False

    for part, qty in requirements.items():
        df.loc[df['Parts'] == part, 'Stock'] -= qty * num_rickshaws

    return df, True

# Function to increment stock
def increment_stock(df, selected_parts, quantity):
    if "All stock" in selected_parts:
        df['Stock'] += quantity
    else:
        for part in selected_parts:
            df.loc[df['Parts'] == part, 'Stock'] += quantity
    return df

# Function to decrement custom stock
def decrement_custom_stock(df, selected_parts, quantity):
    if "All stock" in selected_parts:
        if (df['Stock'] >= quantity).all():
            df['Stock'] -= quantity
        else:
            return df, False
    else:
        for part in selected_parts:
            if df.loc[df['Parts'] == part, 'Stock'].values[0] >= quantity:
                df.loc[df['Parts'] == part, 'Stock'] -= quantity
            else:
                return df, False
    return df, True

# Load parts requirements and stock data
parts_requirements = load_parts_requirements()
df = load_stock_data()

# Calculate producible quantities
df, producible_dict = calculate_producible(df, parts_requirements)

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
df_print = df[['Parts', 'Stock']]
st.subheader("Current Stock of Parts")
st.dataframe(df_print)

# Display producible quantities
st.subheader("Producible Rickshaws")
producible_text = ", ".join([f"{model}: {qty}" for model, qty in producible_dict.items()])
st.write(f"Number of producible models: {producible_text}")

# Check for parts replenishment
replenishment_list = find_parts_to_replenish(df, parts_requirements, producible_dict)
if replenishment_list:
    st.warning("Some parts need to be replenished:")
    for model, part, required_qty in replenishment_list:
        st.write(f"Model: {model}, Part: {part}, Required Quantity: {required_qty}")

# Section to decrement stock for custom number of rickshaws
st.subheader("Record New Rickshaws")
model = st.selectbox('Select Rickshaw Model', parts_requirements.keys(), key='model')
num_rickshaws = st.number_input('Number of Rickshaws to Record', min_value=1, step=1, key='num_rickshaws')
if st.button('Record Rickshaws Made'):
    df, success = decrement_stock(df, num_rickshaws, model, parts_requirements)
    if success:
        save_stock_data(df)
        df, producible_dict = calculate_producible(df, parts_requirements)
        st.success(f"Stock updated successfully for {num_rickshaws} rickshaw(s) of {model}!")
    else:
        st.error(f"Not enough stock to make {num_rickshaws} rickshaw(s) of {model}!")
    df_print = df[['Parts', 'Stock']]
    st.dataframe(df_print)
    producible_text = ", ".join([f"{model}: {qty}" for model, qty in producible_dict.items()])
    st.write(f"Number of producible models: {producible_text}")

    # Check for parts replenishment after recording new rickshaws


    # Initialize a DataFrame with three columns and no rows
    parts_required_df = pd.DataFrame(columns=['Model', 'Part', 'Required Quantity'])

    replenishment_list = find_parts_to_replenish(df, parts_requirements, producible_dict)
    if replenishment_list:
        st.warning("Some parts need to be replenished:")
        for model, part, required_qty in replenishment_list:
            st.write(f"Model: {model}, Part: {part}, Required Quantity: {required_qty}")

# Section to increment stock
st.subheader("Increment Stock of Parts")
parts_list = ["All stock"] + df['Parts'].tolist()
increment_parts = st.multiselect('Select Parts to Increment', parts_list)
quantity_increment = st.number_input('Quantity to Add', min_value=1, step=1, key='increment_qty')
if st.button('Increment Stock'):
    df = increment_stock(df, increment_parts, quantity_increment)
    save_stock_data(df)
    df, producible_dict = calculate_producible(df, parts_requirements)
    st.success("Stock updated successfully!")
    df_print = df[['Parts', 'Stock']]
    st.dataframe(df_print)
    producible_text = ", ".join([f"{model}: {qty}" for model, qty in producible_dict.items()])
    st.write(f"Number of producible models: {producible_text}")

    # Check for parts replenishment after incrementing stock
    replenishment_list = find_parts_to_replenish(df, parts_requirements, producible_dict)
    if replenishment_list:
        st.warning("Some parts need to be replenished:")
        for model, part, required_qty in replenishment_list:
            st.write(f"Model: {model}, Part: {part}, Required Quantity: {required_qty}")

# Section to decrement custom stock
st.subheader("Decrement Stock of Parts")
decrement_parts = st.multiselect('Select Parts to Decrement', parts_list)
quantity_decrement = st.number_input('Quantity to Remove', min_value=1, step=1, key='decrement_qty')
if st.button('Decrement Stock'):
    df, success = decrement_custom_stock(df, decrement_parts, quantity_decrement)
    if success:
        save_stock_data(df)
        df, producible_dict = calculate_producible(df, parts_requirements)
        st.success("Stock updated successfully!")
    else:
        st.error(f"Not enough stock to remove {quantity_decrement} of one or more selected parts!")
    df_print = df[['Parts', 'Stock']]
    st.dataframe(df_print)
    producible_text = ", ".join([f"{model}: {qty}" for model, qty in producible_dict.items()])
    st.write(f"Number of producible models: {producible_text}")

    # Check for parts replenishment after decrementing stock
    replenishment_list = find_parts_to_replenish(df, parts_requirements, producible_dict)
    if replenishment_list:
        st.warning("Some parts need to be replenished:")
        for model, part, required_qty in replenishment_list:
            st.write(f"Model: {model}, Part: {part}, Required Quantity: {required_qty}")
