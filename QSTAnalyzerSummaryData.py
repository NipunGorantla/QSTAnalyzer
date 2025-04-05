import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import openpyxl
import math

st.set_page_config(page_title="QST Thermal Parameters Analyzer", layout="wide")

LOG_TRANSFORMED_PARAMETERS = ["CDT", "WDT"]  # CDT and WDT are log-transformed according to the grey shading

def load_reference_values():
    reference_values = {
        'female': {
            '20-30': {}, 
            '30-40': {}, 
            '40-50': {}, 
            '50-60': {}, 
            '>60': {}
        },
        'male': {
            '20-30': {}, 
            '30-40': {}, 
            '40-50': {}, 
            '50-60': {}, 
            '>60': {}
        }
    }
    
    # Female reference values
    # CDT (Cold Detection Threshold) - Log-transformed in greyed areas
    reference_values['female']['20-30']['CDT'] = {'face': (-0.030, 0.199), 'hand': (0.046, 0.232), 'feet': (0.278, 0.257)}
    reference_values['female']['30-40']['CDT'] = {'face': (-0.035, 0.167), 'hand': (0.078, 0.209), 'feet': (0.348, 0.258)}
    reference_values['female']['40-50']['CDT'] = {'face': (-0.004, 0.191), 'hand': (0.145, 0.217), 'feet': (0.417, 0.256)}
    reference_values['female']['50-60']['CDT'] = {'face': (0.022, 0.218), 'hand': (0.158, 0.229), 'feet': (0.404, 0.279)}
    reference_values['female']['>60']['CDT'] = {'face': (0.016, 0.240), 'hand': (0.187, 0.271), 'feet': (0.377, 0.298)}

    # WDT (Warm Detection Threshold) - Log-transformed in greyed areas
    reference_values['female']['20-30']['WDT'] = {'face': (0.129, 0.187), 'hand': (0.187, 0.193), 'feet': (0.565, 0.175)}
    reference_values['female']['30-40']['WDT'] = {'face': (0.118, 0.174), 'hand': (0.210, 0.206), 'feet': (0.598, 0.203)}
    reference_values['female']['40-50']['WDT'] = {'face': (0.153, 0.213), 'hand': (0.295, 0.217), 'feet': (0.650, 0.214)}
    reference_values['female']['50-60']['WDT'] = {'face': (0.178, 0.224), 'hand': (0.346, 0.204), 'feet': (0.664, 0.215)}
    reference_values['female']['>60']['WDT'] = {'face': (0.176, 0.215), 'hand': (0.368, 0.211), 'feet': (0.657, 0.222)}

    # CPT (Cold Pain Threshold) - Not log-transformed
    reference_values['female']['20-30']['CPT'] = {'face': (18.00, 7.74), 'hand': (15.61, 7.15), 'feet': (14.11, 8.49)}
    reference_values['female']['30-40']['CPT'] = {'face': (15.26, 8.91), 'hand': (13.88, 8.55), 'feet': (13.36, 9.08)}
    reference_values['female']['40-50']['CPT'] = {'face': (14.92, 9.92), 'hand': (12.17, 8.71), 'feet': (12.16, 9.76)}
    reference_values['female']['50-60']['CPT'] = {'face': (13.34, 10.41), 'hand': (10.74, 7.92), 'feet': (11.45, 9.64)}
    reference_values['female']['>60']['CPT'] = {'face': (6.75, 8.02), 'hand': (8.58, 8.09), 'feet': (9.12, 8.42)}

    # HPT (Heat Pain Threshold) - Not log-transformed
    reference_values['female']['20-30']['HPT'] = {'face': (41.61, 4.27), 'hand': (42.68, 3.24), 'feet': (43.69, 2.80)}
    reference_values['female']['30-40']['HPT'] = {'face': (42.06, 4.22), 'hand': (42.79, 3.65), 'feet': (43.96, 3.01)}
    reference_values['female']['40-50']['HPT'] = {'face': (42.23, 3.90), 'hand': (43.49, 3.63), 'feet': (44.73, 2.78)}
    reference_values['female']['50-60']['HPT'] = {'face': (43.04, 3.73), 'hand': (44.73, 2.72), 'feet': (45.71, 2.12)}
    reference_values['female']['>60']['HPT'] = {'face': (44.29, 3.26), 'hand': (45.30, 2.24), 'feet': (45.99, 1.99)}

    # Male reference values
    # CDT (Cold Detection Threshold) - Log-transformed in greyed areas
    reference_values['male']['20-30']['CDT'] = {'face': (-0.062, 0.228), 'hand': (0.035, 0.223), 'feet': (0.380, 0.249)}
    reference_values['male']['30-40']['CDT'] = {'face': (-0.088, 0.214), 'hand': (0.024, 0.228), 'feet': (0.406, 0.247)}
    reference_values['male']['40-50']['CDT'] = {'face': (0.008, 0.202), 'hand': (0.090, 0.270), 'feet': (0.473, 0.319)}
    reference_values['male']['50-60']['CDT'] = {'face': (0.015, 0.224), 'hand': (0.126, 0.261), 'feet': (0.557, 0.290)}
    reference_values['male']['>60']['CDT'] = {'face': (-0.001, 0.236), 'hand': (0.209, 0.234), 'feet': (0.616, 0.266)}

    # WDT (Warm Detection Threshold) - Log-transformed in greyed areas
    reference_values['male']['20-30']['WDT'] = {'face': (0.104, 0.228), 'hand': (0.210, 0.206), 'feet': (0.645, 0.217)}
    reference_values['male']['30-40']['WDT'] = {'face': (0.072, 0.206), 'hand': (0.273, 0.237), 'feet': (0.733, 0.218)}
    reference_values['male']['40-50']['WDT'] = {'face': (0.160, 0.214), 'hand': (0.294, 0.239), 'feet': (0.784, 0.211)}
    reference_values['male']['50-60']['WDT'] = {'face': (0.168, 0.240), 'hand': (0.289, 0.198), 'feet': (0.785, 0.235)}
    reference_values['male']['>60']['WDT'] = {'face': (0.135, 0.254), 'hand': (0.393, 0.262), 'feet': (0.803, 0.237)}

    # CPT (Cold Pain Threshold) - Not log-transformed
    reference_values['male']['20-30']['CPT'] = {'face': (13.69, 9.54), 'hand': (11.24, 8.15), 'feet': (10.65, 7.90)}
    reference_values['male']['30-40']['CPT'] = {'face': (15.18, 10.29), 'hand': (12.01, 9.23), 'feet': (11.10, 8.94)}
    reference_values['male']['40-50']['CPT'] = {'face': (13.39, 10.69), 'hand': (10.49, 9.56), 'feet': (8.77, 8.62)}
    reference_values['male']['50-60']['CPT'] = {'face': (8.71, 8.50), 'hand': (6.51, 6.60), 'feet': (8.85, 9.01)}
    reference_values['male']['>60']['CPT'] = {'face': (9.89, 8.58), 'hand': (6.54, 6.98), 'feet': (11.19, 11.00)}

    # HPT (Heat Pain Threshold) - Not log-transformed
    reference_values['male']['20-30']['HPT'] = {'face': (43.98, 3.50), 'hand': (44.28, 2.86), 'feet': (45.12, 2.40)}
    reference_values['male']['30-40']['HPT'] = {'face': (43.87, 3.73), 'hand': (44.99, 2.86), 'feet': (45.74, 2.56)}
    reference_values['male']['40-50']['HPT'] = {'face': (44.27, 3.98), 'hand': (44.81, 2.88), 'feet': (46.36, 2.32)}
    reference_values['male']['50-60']['HPT'] = {'face': (45.27, 3.56), 'hand': (45.62, 3.07), 'feet': (46.89, 1.97)}
    reference_values['male']['>60']['HPT'] = {'face': (45.71, 2.67), 'hand': (46.95, 2.53), 'feet': (47.74, 1.55)}

    return reference_values

def is_within_normal_range(value, reference_mean, reference_sd, is_log_transformed=False):
    if is_log_transformed:
        try:
            # Convert patient value to log10 if it's positive
            if value <= 0:
                st.warning(f"Can't log-transform value {value} (must be positive)")
                return False, 0, 0
                
            log_value = math.log10(value)
            
            lower_limit = reference_mean - 2 * reference_sd
            upper_limit = reference_mean + 2 * reference_sd
            
            return lower_limit <= log_value <= upper_limit, lower_limit, upper_limit
        except Exception as e:
            st.error(f"Error in log-transformed comparison: {e}")
            return False, 0, 0
    else:
        lower_limit = reference_mean - 2 * reference_sd
        upper_limit = reference_mean + 2 * reference_sd
        return lower_limit <= value <= upper_limit, lower_limit, upper_limit

def transform_from_log(log_value):
    try:
        return 10 ** log_value
    except Exception as e:
        st.error(f"Error transforming from log space: {e}")
        return 0

def get_age_group(age):
    if 20 <= age < 30:
        return '20-30'
    elif 30 <= age < 40:
        return '30-40'
    elif 40 <= age < 50:
        return '40-50'
    elif 50 <= age < 60:
        return '50-60'
    elif age >= 60:
        return '>60'
    else:
        return None  # Age is below reference ranges

def parse_excel_file(uploaded_file):
    try:
        if uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xls'):
            xls = pd.ExcelFile(uploaded_file)
            
            sheet_names = xls.sheet_names
            
            data = {}
            
            for sheet_name in sheet_names:
                data[sheet_name] = pd.read_excel(xls, sheet_name)
            
            return data
        else:
            st.error("Please upload an Excel file (.xlsx or .xls)")
            return None
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        return None

def normalize_modality(modality):
    modality_lower = modality.lower()
    
    if "cold detection" in modality_lower:
        return "CDT"
    elif "warm detection" in modality_lower:
        return "WDT"
    elif "cold pain" in modality_lower:
        return "CPT"
    elif "hot pain" in modality_lower or "heat pain" in modality_lower:
        return "HPT"
    else:
        return modality  # Return original if not recognized

def extract_qst_parameters(summary_df):
    """
    Extract QST parameters from summary sheet data.
    
    Parameters:
    summary_df - DataFrame with QST summary data
    
    Returns:
    Dictionary with extracted QST parameters
    """
    try:
        expected_columns = ['Sequence', 'Modality', 'Trials', 'Avg', 'Var', 'STD']
        required_columns = ['Sequence', 'Modality', 'Avg']
        
        missing_columns = [col for col in required_columns if col not in summary_df.columns]
        if missing_columns:
            st.error(f"Missing essential columns in summary sheet: {', '.join(missing_columns)}")
            st.write("Available columns:", ', '.join(summary_df.columns))
            return None
        
        summary_df['Normalized_Modality'] = summary_df['Modality'].apply(normalize_modality)
        
        st.subheader("Map Body Areas")
        st.write("""
        Please identify which tests correspond to which body areas (face, hand, feet).
        If you have multiple tests for the same modality, assign them to the appropriate body area.
        """)
        
        modalities = summary_df['Normalized_Modality'].unique()
        
        qst_modalities = [m for m in modalities if m in ['CDT', 'WDT', 'CPT', 'HPT']]
        
        if not qst_modalities:
            st.error("Could not find or normalize modalities to CDT, WDT, CPT, or HPT in the data.")
            st.write("Available modalities:", ', '.join(modalities))
            return None
        
        st.write("### Detected Test Types:")
        modality_mapping = pd.DataFrame({
            'Original Modality': summary_df['Modality'].unique(),
            'Normalized Modality': [normalize_modality(m) for m in summary_df['Modality'].unique()]
        })
        st.table(modality_mapping)
        
        modality_area_map = {}
        
        for modality in qst_modalities:
            st.write(f"### {modality} Tests")
            
            if modality in LOG_TRANSFORMED_PARAMETERS:
                st.info(f"Note: {modality} is log10-transformed in the normative reference data.")
                
            modality_rows = summary_df[summary_df['Normalized_Modality'] == modality]
            
            for _, row in modality_rows.iterrows():
                sequence = row['Sequence']
                
                area = st.selectbox(
                    f"Body area for {modality} test (Sequence {sequence}, Original: '{row['Modality']}', Avg: {row['Avg']}):", 
                    ["Select area...", "Face", "Hand", "Feet"],
                    key=f"{modality}_{sequence}"
                )
                
                if area != "Select area...":
                    modality_area_map[(modality, sequence)] = area.lower()
        
        parameters = {}
        for (modality, sequence), area in modality_area_map.items():
            row = summary_df[(summary_df['Normalized_Modality'] == modality) & (summary_df['Sequence'] == sequence)]
            
            if not row.empty:
                value = row['Avg'].iloc[0]
                
                param_name = f"{modality}_{area}"
                
                parameters[param_name] = value
        
        return parameters
    
    except Exception as e:
        st.error(f"Error extracting QST parameters: {e}")
        st.exception(e)
        return None

def analyze_qst_parameters(params, gender, age, reference_values):
    age_group = get_age_group(age)
    if not age_group:
        st.error("Age must be at least 20 years.")
        return None
    
    results = {}
    
    for param_area, value in params.items():
        parts = param_area.split('_')
        if len(parts) != 2:
            st.warning(f"Invalid parameter name format: {param_area}")
            continue
            
        param, area = parts
        
        if param not in ['CDT', 'WDT', 'CPT', 'HPT']:
            st.warning(f"Unknown parameter: {param}")
            continue
            
        if area not in ['face', 'hand', 'feet']:
            st.warning(f"Unknown body area: {area}")
            continue
        
        if param not in reference_values[gender][age_group]:
            st.warning(f"No reference values for {param} in {gender}, age group {age_group}")
            continue
            
        if area not in reference_values[gender][age_group][param]:
            st.warning(f"No reference values for {param} in {area}, {gender}, age group {age_group}")
            continue
        
        ref_mean, ref_sd = reference_values[gender][age_group][param][area]
        
        is_log_transformed = param in LOG_TRANSFORMED_PARAMETERS
        
        is_normal, lower_limit, upper_limit = is_within_normal_range(
            value, ref_mean, ref_sd, is_log_transformed=is_log_transformed
        )
        
        if param not in results:
            results[param] = {}
            
        if is_log_transformed:
            display_lower = transform_from_log(lower_limit)
            display_upper = transform_from_log(upper_limit)
            display_mean = transform_from_log(ref_mean)
            
            results[param][area] = {
                'patient_value': value,
                'reference_mean': ref_mean,
                'reference_sd': ref_sd,
                'lower_limit': lower_limit,
                'upper_limit': upper_limit,
                'display_lower': display_lower,
                'display_upper': display_upper,
                'display_mean': display_mean,
                'log_transformed': True,
                'is_normal': is_normal
            }
        else:
            results[param][area] = {
                'patient_value': value,
                'reference_mean': ref_mean,
                'reference_sd': ref_sd,
                'lower_limit': lower_limit,
                'upper_limit': upper_limit,
                'log_transformed': False,
                'is_normal': is_normal
            }
    
    return results

def display_results(results):
    if not results:
        return
    
    st.subheader("QST Analysis Results")
    
    parameters = list(results.keys())
    tabs = st.tabs(parameters)
    
    for i, param in enumerate(parameters):
        with tabs[i]:
            st.write(f"### {param} Results")
            
            is_log_transformed = any(results[param][area].get('log_transformed', False) for area in results[param] if area in ['face', 'hand', 'feet'])
            
            if is_log_transformed:
                st.info(f"{param} values are log10-transformed in the normative reference data. The table below shows both the original values and the transformed ranges for comparison.")
            
            data = []
            for area in ['face', 'hand', 'feet']:
                if area in results[param]:
                    res = results[param][area]
                    status = "✅ Normal" if res['is_normal'] else "❌ Abnormal"
                    
                    if res.get('log_transformed', False):
                        data.append({
                            "Body Area": area.capitalize(),
                            "Patient Value": f"{res['patient_value']:.2f}",
                            "Reference Mean": f"{res['display_mean']:.2f} (log10: {res['reference_mean']:.2f})",
                            "Reference SD": f"{res['reference_sd']:.2f} (in log10 space)",
                            "Normal Range": f"{res['display_lower']:.2f} to {res['display_upper']:.2f}",
                            "Status": status
                        })
                    else:
                        data.append({
                            "Body Area": area.capitalize(),
                            "Patient Value": f"{res['patient_value']:.2f}",
                            "Reference Mean": f"{res['reference_mean']:.2f}",
                            "Reference SD": f"{res['reference_sd']:.2f}",
                            "Normal Range": f"{res['lower_limit']:.2f} to {res['upper_limit']:.2f}",
                            "Status": status
                        })
            
            if data:
                df = pd.DataFrame(data)
                st.table(df)
                
                fig, ax = plt.subplots(figsize=(10, 4))
                
                areas = [area.capitalize() for area in ['face', 'hand', 'feet'] if area in results[param]]
                patient_values = [results[param][area]['patient_value'] for area in ['face', 'hand', 'feet'] if area in results[param]]
                
                if is_log_transformed:
                    ref_means = [results[param][area]['display_mean'] for area in ['face', 'hand', 'feet'] if area in results[param]]
                    lower_limits = [results[param][area]['display_lower'] for area in ['face', 'hand', 'feet'] if area in results[param]]
                    upper_limits = [results[param][area]['display_upper'] for area in ['face', 'hand', 'feet'] if area in results[param]]
                else:
                    ref_means = [results[param][area]['reference_mean'] for area in ['face', 'hand', 'feet'] if area in results[param]]
                    lower_limits = [results[param][area]['lower_limit'] for area in ['face', 'hand', 'feet'] if area in results[param]]
                    upper_limits = [results[param][area]['upper_limit'] for area in ['face', 'hand', 'feet'] if area in results[param]]
                
                x = np.arange(len(areas))
                width = 0.35
                
                ax.bar(x, patient_values, width, label='Patient Value', color='lightcoral')
                ax.bar(x + width, ref_means, width, label='Reference Mean', color='lightblue')
                
                for i, (lower, upper, mean) in enumerate(zip(lower_limits, upper_limits, ref_means)):
                    ax.plot([i + width, i + width], [lower, upper], color='blue', linestyle='-', linewidth=2)
                    ax.plot([i + width - 0.1, i + width + 0.1], [lower, lower], color='blue', linestyle='-', linewidth=2)
                    ax.plot([i + width - 0.1, i + width + 0.1], [upper, upper], color='blue', linestyle='-', linewidth=2)
                
                ax.set_ylabel('Value')
                ax.set_title(f'{param} Comparison')
                ax.set_xticks(x + width / 2)
                ax.set_xticklabels(areas)
                ax.legend()
                
                st.pyplot(fig)

def main():
    st.title("QST Thermal Parameters Analyzer")
    
    
    reference_values = load_reference_values()
    
    st.sidebar.header("Patient Information")
    gender = st.sidebar.radio("Gender:", ["male", "female"])
    age = st.sidebar.number_input("Age:", min_value=18, max_value=100, value=50)
    
    st.subheader("Upload QST Excel File")
    
    
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        excel_data = parse_excel_file(uploaded_file)
        
        if excel_data:
            sheet_names = list(excel_data.keys())
            
            st.write(f"Found {len(sheet_names)} sheets: {', '.join(sheet_names)}")
            
            summary_sheet = st.selectbox(
                "Select the sheet containing the summary data:",
                sheet_names
            )
            
            if summary_sheet:
                st.write(f"### Preview of {summary_sheet}")
                st.dataframe(excel_data[summary_sheet].head())
                
                parameters = extract_qst_parameters(excel_data[summary_sheet])
                
                if parameters:
                    st.success("Successfully extracted QST parameters!")
                    st.write("### Extracted Parameters")
                    
                    param_df = pd.DataFrame([
                        {"Parameter": k, "Value": f"{v:.2f}" if isinstance(v, (int, float)) else v} 
                        for k, v in parameters.items()
                    ])
                    st.table(param_df)
                    
                    if st.button("Analyze QST Parameters"):
                        results = analyze_qst_parameters(parameters, gender, age, reference_values)
                        
                        if results:
                            display_results(results)
                        else:
                            st.error("No valid QST parameters to analyze.")

if __name__ == "__main__":
    main()